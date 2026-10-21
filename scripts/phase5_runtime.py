"""Bounded Phase 5 bootstrap for the image-owned torch 2.8.0 / CUDA 12.8 stack.

Only the caller's exact training pins and their dependencies are installed. All
runtime imports happen in fresh, offline subprocesses, including when skipping
installation. Importing this helper itself requires only the standard library.
"""

from __future__ import annotations

import importlib
import json
import os
import re
import subprocess
import sys
import tempfile
from contextlib import redirect_stdout
from importlib import metadata
from pathlib import Path
from typing import Any

__all__ = ["install_deps", "print_versions"]

_PIP_TIMEOUT = 600
_PROBE_TIMEOUT = 120
_PIN = re.compile(r"([A-Za-z0-9][A-Za-z0-9._-]*)==([A-Za-z0-9][A-Za-z0-9.!+_-]*)")
_LIBRARIES = (
    "sentence-transformers", "transformers", "datasets", "accelerate", "safetensors", "rank-bm25",
)
_SMOKE_IMPORTS = {
    "sentence_transformers": ("SentenceTransformer", "SentenceTransformerTrainer", "InputExample"),
    "sentence_transformers.losses": ("MultipleNegativesRankingLoss",),
    "transformers": ("AutoModel", "AutoTokenizer", "Trainer", "BertModel"),
    "datasets": ("Dataset",),
    "accelerate": ("Accelerator",),
    "safetensors.torch": ("load_file", "save_file"),
    "rank_bm25": ("BM25Okapi",),
    "torch.utils.data": ("DataLoader",),
    "huggingface_hub": (), "tokenizers": (), "sklearn": (), "scipy": (),
    "pyarrow": (), "dill": (), "xxhash": (), "multiprocess": (), "tqdm": (), "regex": (),
}


def _canonical(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name).lower()


def _protected(name: str) -> bool:
    name = _canonical(name)
    return name in {"torch", "torchvision", "torchaudio", "triton"} or name.startswith("nvidia-")


def _pin_versions(pinned: tuple[str, ...]) -> dict[str, str]:
    versions: dict[str, str] = {}
    for requirement in pinned:
        match = _PIN.fullmatch(requirement)
        if match is None:
            raise ValueError(f"Phase 5 requires exact name==version pins: {requirement!r}")
        name, version = match.groups()
        name = _canonical(name)
        if name in versions and versions[name] != version:
            raise ValueError(f"Phase 5 has conflicting pins for {name}")
        versions[name] = version
    return versions


def _import_symbols(module: str, symbols: tuple[str, ...] = ()) -> Any:
    try:
        loaded = importlib.import_module(module)
        for symbol in symbols:
            getattr(loaded, symbol)  # Exercise lazy imports as well as module availability.
        return loaded
    except Exception as exc:
        raise RuntimeError(f"Phase 5 import smoke failed for {module}: {exc}") from exc


def _collect_versions(smoke: bool, pinned: tuple[str, ...]) -> dict[str, Any]:
    """Executed only in the child process (directly mocked in unit tests)."""
    # The GPU entry point imports source helpers, not the Python-3.12 host package.
    # Its minimum is 3.11 (datetime.UTC and hashlib.file_digest); keep the image's Python.
    if sys.version_info < (3, 11):  # noqa: UP036 - diagnose an unsupported pod image.
        raise RuntimeError("Phase 5 GPU scripts require Python >=3.11")
    torch = _import_symbols("torch")
    if str(torch.__version__).split("+", 1)[0] != "2.8.0" or torch.version.cuda != "12.8":
        raise RuntimeError(
            "Phase 5 requires preinstalled torch==2.8.0 with CUDA 12.8; "
            f"found torch={torch.__version__}, CUDA={torch.version.cuda}"
        )
    if not torch.cuda.is_available():
        raise RuntimeError("Phase 5 requires a CUDA GPU; no CUDA GPU is available")
    _import_symbols("numpy")
    protected: dict[str, str] = {}
    for distribution in metadata.distributions():
        name = _canonical(distribution.metadata["Name"] or "")
        if _protected(name):
            if name in protected and protected[name] != distribution.version:
                raise RuntimeError(f"Phase 5 found conflicting installed versions of {name}")
            protected[name] = distribution.version
    if "torch" not in protected:
        raise RuntimeError("Phase 5 requires installed torch distribution metadata")
    versions: dict[str, Any] = {
        "python": sys.version,
        "torch": str(torch.__version__),
        "cuda": torch.version.cuda,
        "cuda_available": True,
        "gpu": torch.cuda.get_device_name(0),
        "gpu_capability": list(torch.cuda.get_device_capability(0)),
        "numpy": metadata.version("numpy"),
        "protected_distributions": protected,
    }
    if smoke:
        for name, expected in _pin_versions(pinned).items():
            actual = metadata.version(name)
            if actual != expected:
                raise RuntimeError(f"Phase 5 pin mismatch: {name}=={expected}, installed {actual}")
        for module, symbols in _SMOKE_IMPORTS.items():
            _import_symbols(module, symbols)
        versions.update({name.replace("-", "_"): metadata.version(name) for name in _LIBRARIES})
    return versions


def _run(command: list[str], *, label: str, timeout: int, env: dict[str, str]) -> str:
    print(f"Phase 5: {label} (timeout {timeout}s)", file=sys.stderr, flush=True)
    try:
        return subprocess.run(
            command, check=True, capture_output=not label.startswith("dependency"),
            text=True, timeout=timeout, env=env,
        ).stdout or ""
    except subprocess.CalledProcessError as exc:
        detail = (exc.stderr or exc.stdout or str(exc))[-4000:]
        raise RuntimeError(f"Phase 5 {label} failed:\n{detail}") from exc
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError(f"Phase 5 {label} timed out after {timeout}s") from exc
    except OSError as exc:
        raise RuntimeError(f"Phase 5 {label} could not start: {exc}") from exc


def _probe(smoke: bool, pinned: tuple[str, ...] = ()) -> dict[str, Any]:
    env = {
        **os.environ,
        "HF_HUB_OFFLINE": "1",
        "HF_DATASETS_OFFLINE": "1",
        "TRANSFORMERS_OFFLINE": "1",
        "HF_HUB_DISABLE_TELEMETRY": "1",
    }
    output = _run(
        [sys.executable, str(Path(__file__).resolve()), "smoke" if smoke else "base",
         json.dumps(pinned)],
        label="runtime verification", timeout=_PROBE_TIMEOUT, env=env,
    )
    try:
        versions = json.loads(output)
        if not isinstance(versions, dict):
            raise ValueError("expected a versions object")
        return versions
    except ValueError as exc:
        raise RuntimeError("Phase 5 runtime verification returned invalid JSON") from exc


def _read_plan(path: Path) -> dict[str, str]:
    try:
        report = json.loads(path.read_text(encoding="utf-8"))
        if report["version"] != "1" or not isinstance(report["install"], list):
            raise ValueError("expected pip report schema 1 (pip >=23.0)")
        pins = []
        for entry in report["install"]:
            info = entry["metadata"]
            pins.append(info["name"] + "==" + info["version"])
        return _pin_versions(tuple(pins))
    except (OSError, ValueError, KeyError, TypeError) as exc:
        raise RuntimeError(f"Phase 5 could not validate pip dry-run report: {exc}") from exc


def _write_constraints(path: Path, versions: dict[str, str]) -> None:
    # Also validate installed metadata before writing it as pip input.
    pins = tuple(f"{name}=={version}" for name, version in sorted(versions.items()))
    _pin_versions(pins)
    path.write_text("\n".join(pins) + "\n", encoding="utf-8")


def install_deps(pinned: tuple[str, ...]) -> None:
    """Resolve training pins without replacing image-owned CUDA packages or NumPy.

    Reject any protected-package installation, even a same-version reinstall or
    a previously absent NVIDIA package. Fail closed on resolution/report errors.
    PHASE5_SKIP_INSTALL=1 skips pip, but still checks pins, CUDA and real imports.
    """
    if not pinned:
        raise ValueError("Phase 5 requires a nonempty tuple of exact training pins")
    _pin_versions(pinned)
    if os.environ.get("PHASE5_SKIP_INSTALL") == "1":
        print("PHASE5_SKIP_INSTALL=1: skipped pinned dependency installation", flush=True)
        _probe(True, pinned)
        return

    before = _probe(False)
    frozen = {**before["protected_distributions"], "numpy": before["numpy"]}
    # Ignore ambient pip settings such as no-deps, force-reinstall or target.
    env = {key: value for key, value in os.environ.items() if not key.startswith("PIP_")}
    env["PIP_CONFIG_FILE"] = os.devnull
    with tempfile.TemporaryDirectory(prefix="phase5-runtime-") as directory:
        constraints = Path(directory) / "constraints.txt"
        report = Path(directory) / "plan.json"
        _write_constraints(constraints, frozen)
        command = [
            sys.executable, "-m", "pip", "install", "--disable-pip-version-check", "--no-input",
            "--timeout", "30", "--retries", "1", "--constraint", str(constraints), *pinned,
        ]
        _run(command + ["--dry-run", "--report", str(report)],
             label="dependency dry-run", timeout=_PIP_TIMEOUT, env=env)
        planned = _read_plan(report)
        blocked = sorted(name for name in planned if _protected(name) or name in frozen)
        if blocked:
            raise RuntimeError(
                "Phase 5 refused pip plan touching protected distributions: " + ", ".join(blocked)
            )
        if planned:
            # Keep the accepted resolution's versions fixed during the normal install.
            _write_constraints(constraints, {**frozen, **planned})
            _run(command, label="dependency install", timeout=_PIP_TIMEOUT, env=env)

    after = _probe(True, pinned)
    for key in ("torch", "cuda", "numpy", "protected_distributions"):
        if after[key] != before[key]:
            raise RuntimeError(f"Phase 5 image-owned runtime changed during installation: {key}")


def print_versions() -> dict[str, Any]:
    """Verify imports/CUDA freshly, print the Phase 5 JSON report and return it."""
    versions = _probe(True)
    print(json.dumps({"phase": 5, "versions": versions}, sort_keys=True), flush=True)
    return versions


if __name__ == "__main__":
    # Keep import-time library chatter out of the child process's JSON response.
    with redirect_stdout(sys.stderr):
        result = _collect_versions(sys.argv[1] == "smoke", tuple(json.loads(sys.argv[2])))
    print(json.dumps(result, sort_keys=True))
