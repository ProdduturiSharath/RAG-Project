"""Offline bootstrap tests: subprocesses, installed packages and CUDA are all fake."""

from __future__ import annotations

import copy
import json
import subprocess
from pathlib import Path
from types import SimpleNamespace
from typing import Any
from unittest.mock import Mock

import pytest

from scripts import phase5_runtime as runtime

PINNED = (
    "sentence-transformers==5.1.1",
    "transformers==4.56.2",
    "datasets==4.0.0",
    "accelerate==1.10.1",
    "safetensors==0.6.2",
    "rank-bm25==0.2.2",
)
PROTECTED = {
    "torch": "2.8.0+cu128",
    "torchvision": "0.23.0+cu128",
    "torchaudio": "2.8.0+cu128",
    "triton": "3.4.0",
    "nvidia-cuda-runtime-cu12": "12.8.90",
    "nvidia-cublas-cu12": "12.8.4.1",
}
BASE = {
    "python": "3.12.15",
    "torch": "2.8.0+cu128",
    "cuda": "12.8",
    "cuda_available": True,
    "numpy": "2.2.6",
    "gpu": "Fake GPU",
    "gpu_capability": [8, 9],
    "protected_distributions": PROTECTED,
}


def _report(*pins: str) -> dict[str, Any]:
    return {
        "version": "1",
        "install": [
            {"metadata": dict(zip(("name", "version"), pin.split("=="), strict=True))}
            for pin in pins
        ],
    }


@pytest.fixture(autouse=True)
def offline(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("PHASE5_SKIP_INSTALL", raising=False)
    monkeypatch.setattr(
        runtime.subprocess, "run", Mock(side_effect=AssertionError("real subprocess forbidden")),
    )
    monkeypatch.setattr(
        runtime, "importlib",
        SimpleNamespace(import_module=Mock(side_effect=AssertionError("real import forbidden"))),
    )


@pytest.fixture
def process(monkeypatch: pytest.MonkeyPatch) -> dict[str, Any]:
    state: dict[str, Any] = {
        "before": copy.deepcopy(BASE),
        "after": copy.deepcopy(BASE),
        "report": _report(*PINNED, "tokenizers==0.22.0", "huggingface-hub==0.34.4"),
        "calls": [],
        "fail_at": None,
    }

    def run(command: list[str], **kwargs: Any) -> subprocess.CompletedProcess[str]:
        is_pip = command[1:4] == ["-m", "pip", "install"]
        stage = ("dry-run" if "--dry-run" in command else "install") if is_pip else command[2]
        call = {"stage": stage, "command": command, "kwargs": kwargs}
        if is_pip:
            path = Path(command[command.index("--constraint") + 1])
            call["constraints"] = path.read_text(encoding="utf-8").splitlines()
        state["calls"].append(call)
        if state["fail_at"] == stage:
            raise state["error"]
        if stage == "dry-run" and state["report"] is not None:
            path = Path(command[command.index("--report") + 1])
            report = state["report"]
            path.write_text(report if isinstance(report, str) else json.dumps(report))
        output = state["before"] if stage == "base" else state["after"]
        return subprocess.CompletedProcess(command, 0, json.dumps(output), "")

    monkeypatch.setattr(runtime.subprocess, "run", run)
    return state


def _stages(process: dict[str, Any]) -> list[str]:
    return [call["stage"] for call in process["calls"]]


def test_install_resolves_transitives_and_preserves_image_stack(process: dict[str, Any]) -> None:
    runtime.install_deps(PINNED)

    assert _stages(process) == ["base", "dry-run", "install", "smoke"]
    baseline, dry_run, install, smoke = process["calls"]
    frozen = {f"{name}=={version}" for name, version in PROTECTED.items()} | {"numpy==2.2.6"}
    assert set(dry_run["constraints"]) == frozen
    assert set(install["constraints"]) == frozen | set(PINNED) | {
        "tokenizers==0.22.0", "huggingface-hub==0.34.4",
    }
    for call in (dry_run, install):
        command = call["command"]
        assert all(pin in command for pin in PINNED)
        assert not {
            "--no-deps", "--upgrade", "--force-reinstall", "--ignore-installed",
        } & set(command)
        assert call["kwargs"]["timeout"] == 600
        assert command[command.index("--retries") + 1] == "1"
        assert command[command.index("--timeout") + 1] == "30"
        assert not Path(command[command.index("--constraint") + 1]).exists()
    for call in (baseline, smoke):
        assert call["command"][:2] == [
            runtime.sys.executable, str(Path(runtime.__file__).resolve()),
        ]
        assert call["kwargs"]["timeout"] == 120
        for variable in ("HF_HUB_OFFLINE", "HF_DATASETS_OFFLINE", "TRANSFORMERS_OFFLINE"):
            assert call["kwargs"]["env"][variable] == "1"
    assert json.loads(smoke["command"][3]) == list(PINNED)


@pytest.mark.parametrize("pin", [
    "torch==2.8.0+cu128", "torch==2.9.0", "TorchVision==0.23.0+cu128",
    "torchaudio==2.8.0+cu128", "triton==3.4.0", "NVIDIA.CUBLAS_CU12==12.8.4.1",
    "nvidia-new-cu12==1.0", "numpy==2.2.6",
])
def test_protected_plans_abort_before_install(process: dict[str, Any], pin: str) -> None:
    process["report"] = _report("tokenizers==0.22.0", pin)
    with pytest.raises(RuntimeError, match="refused pip plan.*protected"):
        runtime.install_deps(PINNED)
    assert _stages(process) == ["base", "dry-run"]
    command = process["calls"][-1]["command"]
    assert not Path(command[command.index("--report") + 1]).exists()


@pytest.mark.parametrize("report", [
    None, "not JSON", [], {}, {"version": "2", "install": []},
    {"version": "1", "install": None}, {"version": "1", "install": [{}]},
    {"version": "1", "install": [{"metadata": {"name": "torch", "version": None}}]},
    _report("package==1.0\n--no-deps"), _report("package==1.0", "PACKAGE==2.0"),
])
def test_invalid_or_missing_report_fails_closed(process: dict[str, Any], report: Any) -> None:
    process["report"] = report
    with pytest.raises(RuntimeError, match="could not validate pip dry-run report"):
        runtime.install_deps(PINNED)
    assert _stages(process) == ["base", "dry-run"]


@pytest.mark.parametrize("stage,error,match", [
    ("base", subprocess.CalledProcessError(1, "probe", stderr="no CUDA GPU"), "no CUDA GPU"),
    ("dry-run", subprocess.CalledProcessError(1, "pip", stderr="ResolutionImpossible"),
     "dependency dry-run failed.*"),
    ("dry-run", subprocess.TimeoutExpired("pip", 600), "dry-run timed out after 600s"),
    ("dry-run", FileNotFoundError("pip unavailable"), "dry-run could not start"),
    ("install", subprocess.CalledProcessError(1, "pip", stderr="disk full"), "disk full"),
    ("smoke", subprocess.CalledProcessError(1, "probe", stderr="Trainer import failed"),
     "Trainer import failed"),
])
def test_subprocess_failures_are_contextual_and_not_retried(
    process: dict[str, Any], stage: str, error: Exception, match: str,
) -> None:
    process.update(fail_at=stage, error=error)
    with pytest.raises(RuntimeError, match=match):
        runtime.install_deps(PINNED)
    stages = ["base", "dry-run", "install", "smoke"]
    assert _stages(process) == stages[:stages.index(stage) + 1]


def test_satisfied_plan_still_gets_fresh_import_verification(process: dict[str, Any]) -> None:
    process["report"] = _report()
    runtime.install_deps(PINNED)
    assert _stages(process) == ["base", "dry-run", "smoke"]


@pytest.mark.parametrize("key,value", [
    ("torch", "2.8.0+other"), ("cuda", "12.9"), ("numpy", "2.3.0"),
    ("protected_distributions", {**PROTECTED, "triton": "3.5.0"}),
    ("protected_distributions", {**PROTECTED, "nvidia-new-cu12": "1.0"}),
    ("protected_distributions", {"torch": PROTECTED["torch"]}),
])
def test_post_install_detects_image_runtime_drift(
    process: dict[str, Any], key: str, value: Any,
) -> None:
    process["after"][key] = value
    with pytest.raises(RuntimeError, match=f"runtime changed.*{key}"):
        runtime.install_deps(PINNED)
    assert _stages(process)[-1] == "smoke"


def test_skip_install_still_checks_imports_and_exact_pins(
    monkeypatch: pytest.MonkeyPatch, process: dict[str, Any], capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setenv("PHASE5_SKIP_INSTALL", "1")
    runtime.install_deps(PINNED)
    assert _stages(process) == ["smoke"]
    assert json.loads(process["calls"][0]["command"][3]) == list(PINNED)
    assert "PHASE5_SKIP_INSTALL=1" in capsys.readouterr().out
    process.update(
        fail_at="smoke", error=subprocess.CalledProcessError(1, "probe", stderr="missing datasets"),
    )
    with pytest.raises(RuntimeError, match="missing datasets"):
        runtime.install_deps(PINNED)
    assert _stages(process) == ["smoke", "smoke"]


def test_pip_configuration_cannot_bypass_resolution_or_change_target(
    monkeypatch: pytest.MonkeyPatch, process: dict[str, Any],
) -> None:
    for key in ("PIP_NO_DEPS", "PIP_FORCE_REINSTALL", "PIP_IGNORE_INSTALLED", "PIP_TARGET"):
        monkeypatch.setenv(key, "1")
    monkeypatch.setenv("PIP_CONFIG_FILE", "/untrusted/pip.conf")
    monkeypatch.setenv("PHASE5_SKIP_INSTALL", "0")
    runtime.install_deps(PINNED)
    for call in process["calls"][1:3]:
        env = call["kwargs"]["env"]
        assert {key: value for key, value in env.items() if key.startswith("PIP_")} == {
            "PIP_CONFIG_FILE": runtime.os.devnull,
        }


@pytest.mark.parametrize("pins", [
    (), ("transformers>=4",), ("transformers==4.*",), ("--upgrade",),
    ("package @ https://example.invalid/package.whl",), ("datasets[all]==4.0.0",),
    ("transformers==4.56.2", "TRANSFORMERS==4.57.0"),
])
def test_invalid_pins_fail_before_any_subprocess(pins: tuple[str, ...]) -> None:
    with pytest.raises(ValueError, match="Phase 5"):
        runtime.install_deps(pins)


def test_print_versions_uses_fresh_smoke_and_reports_libraries_and_gpu(
    process: dict[str, Any], capsys: pytest.CaptureFixture[str],
) -> None:
    libraries = {name.replace("-", "_"): version for name, version in
                 (pin.split("==") for pin in PINNED)}
    process["after"].update(libraries)
    versions = runtime.print_versions()
    assert versions == {**BASE, **libraries}
    assert json.loads(capsys.readouterr().out) == {"phase": 5, "versions": versions}
    assert _stages(process) == ["smoke"]


@pytest.mark.parametrize("output", ["noisy output\n{}", "[]", "null"])
def test_probe_rejects_non_json_or_non_object_output(
    monkeypatch: pytest.MonkeyPatch, output: str,
) -> None:
    monkeypatch.setattr(
        runtime.subprocess, "run", Mock(return_value=subprocess.CompletedProcess([], 0, output)),
    )
    with pytest.raises(RuntimeError, match="runtime verification returned invalid JSON"):
        runtime.print_versions()


@pytest.fixture
def packages(monkeypatch: pytest.MonkeyPatch) -> dict[str, Any]:
    versions = dict(pin.split("==") for pin in PINNED) | PROTECTED | {"numpy": "2.2.6"}
    modules = {
        name: SimpleNamespace(**{symbol: object() for symbol in symbols})
        for name, symbols in runtime._SMOKE_IMPORTS.items()
    }
    modules["torch"] = SimpleNamespace(
        __version__="2.8.0+cu128", version=SimpleNamespace(cuda="12.8"),
        cuda=SimpleNamespace(
            is_available=Mock(return_value=True), get_device_name=Mock(return_value="Fake GPU"),
            get_device_capability=Mock(return_value=(8, 9)),
        ),
    )
    modules["numpy"] = SimpleNamespace(__version__="2.2.6")
    distributions = [
        SimpleNamespace(metadata={"Name": name.replace("-", "_").upper()}, version=version)
        for name, version in versions.items()
    ]

    def version(name: str) -> str:
        try:
            return versions[name]
        except KeyError as exc:
            raise runtime.metadata.PackageNotFoundError(name) from exc

    monkeypatch.setattr(runtime.sys, "version_info", (3, 12, 15))
    monkeypatch.setattr(runtime.metadata, "version", version)
    monkeypatch.setattr(runtime.metadata, "distributions", lambda: distributions)
    import_module = Mock(side_effect=modules.__getitem__)
    monkeypatch.setattr(runtime, "importlib", SimpleNamespace(import_module=import_module))
    return {"versions": versions, "modules": modules, "distributions": distributions,
            "import_module": import_module}


def test_worker_smokes_training_apis_and_reports_canonical_protected_versions(
    packages: dict[str, Any],
) -> None:
    versions = runtime._collect_versions(True, PINNED)
    assert versions["protected_distributions"] == PROTECTED
    assert versions["torch"] == "2.8.0+cu128"
    assert versions["cuda"] == "12.8"
    assert versions["cuda_available"] is True
    assert versions["gpu"] == "Fake GPU"
    assert versions["gpu_capability"] == [8, 9]
    for pin in PINNED:
        name, version = pin.split("==")
        assert versions[name.replace("-", "_")] == version
    imported = {call.args[0] for call in packages["import_module"].call_args_list}
    assert {"numpy", "torch", "sentence_transformers", "sentence_transformers.losses",
            "transformers", "datasets", "accelerate", "safetensors.torch", "rank_bm25",
            "torch.utils.data"} <= imported


def test_baseline_does_not_require_training_deps_before_install(packages: dict[str, Any]) -> None:
    for name in tuple(packages["modules"]):
        if name not in {"torch", "numpy"}:
            del packages["modules"][name]
    assert runtime._collect_versions(False, ())["torch"] == "2.8.0+cu128"


@pytest.mark.parametrize("name", ["torch", "numpy", "datasets", "safetensors.torch", "rank_bm25"])
def test_missing_import_has_actionable_library_name(packages: dict[str, Any], name: str) -> None:
    del packages["modules"][name]
    with pytest.raises(RuntimeError, match=f"import smoke failed for {name}"):
        runtime._collect_versions(True, PINNED)


def test_lazy_trainer_import_failure_is_not_hidden_by_module_version(
    packages: dict[str, Any],
) -> None:
    delattr(packages["modules"]["transformers"], "Trainer")
    with pytest.raises(RuntimeError, match="import smoke failed for transformers.*Trainer"):
        runtime._collect_versions(True, PINNED)


def test_installed_pin_mismatch_is_reported_even_if_module_importable(
    packages: dict[str, Any],
) -> None:
    packages["versions"]["sentence-transformers"] = "6.1.0"
    with pytest.raises(RuntimeError, match=r"pin mismatch: sentence-transformers==5.1.1.*6.1.0"):
        runtime._collect_versions(True, PINNED)


@pytest.mark.parametrize("torch_version,cuda_version", [
    ("2.7.1+cu128", "12.8"), ("2.8.0+cpu", None), ("2.8.0+cu126", "12.6"),
])
def test_worker_rejects_wrong_torch_or_cuda_build(
    packages: dict[str, Any], torch_version: str, cuda_version: str | None,
) -> None:
    packages["modules"]["torch"].__version__ = torch_version
    packages["modules"]["torch"].version.cuda = cuda_version
    with pytest.raises(RuntimeError, match="preinstalled torch==2.8.0 with CUDA 12.8"):
        runtime._collect_versions(False, ())


def test_worker_fails_clearly_without_cuda_device(packages: dict[str, Any]) -> None:
    cuda = packages["modules"]["torch"].cuda
    cuda.is_available.return_value = False
    with pytest.raises(RuntimeError, match="no CUDA GPU is available"):
        runtime._collect_versions(True, PINNED)
    cuda.get_device_name.assert_not_called()


@pytest.mark.parametrize("version", [(3, 11, 9), (3, 12, 15)])
def test_worker_accepts_gpu_image_python(
    monkeypatch: pytest.MonkeyPatch, packages: dict[str, Any], version: tuple[int, int, int],
) -> None:
    monkeypatch.setattr(runtime.sys, "version_info", version)
    assert runtime._collect_versions(True, PINNED)["torch"] == "2.8.0+cu128"


def test_worker_requires_python_311(
    monkeypatch: pytest.MonkeyPatch, packages: dict[str, Any],
) -> None:
    monkeypatch.setattr(runtime.sys, "version_info", (3, 10, 9))
    with pytest.raises(RuntimeError, match="Python >=3.11"):
        runtime._collect_versions(False, ())
    packages["import_module"].assert_not_called()


def test_worker_rejects_conflicting_protected_metadata(packages: dict[str, Any]) -> None:
    packages["distributions"].append(
        SimpleNamespace(metadata={"Name": "TORCH"}, version="2.7.1"),
    )
    with pytest.raises(RuntimeError, match="conflicting installed versions of torch"):
        runtime._collect_versions(False, ())


def test_worker_requires_torch_metadata_to_freeze_it(packages: dict[str, Any]) -> None:
    packages["distributions"][:] = [
        dist for dist in packages["distributions"] if dist.metadata["Name"] != "TORCH"
    ]
    with pytest.raises(RuntimeError, match="installed torch distribution metadata"):
        runtime._collect_versions(False, ())
