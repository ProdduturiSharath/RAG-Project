"""Execute copied wrappers with Bash stand-ins for Python; never run a stage."""

from __future__ import annotations

import fcntl
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
STAGES = ("gpu", "eval")
ENV_NAMES = (
    "PWD",
    "HF_HOME",
    "PYTHONPATH",
    "PYTHONUNBUFFERED",
    "TOKENIZERS_PARALLELISM",
    "HF_HUB_DISABLE_TELEMETRY",
    "RAG_EVAL_DATABASE_URL",
    "RAG_DENSE_MODEL",
    "RAG_RERANKER_MODEL",
    "RAG_EMBEDDER_ID",
    "HF_HUB_CACHE",
    "TRANSFORMERS_CACHE",
    "SENTENCE_TRANSFORMERS_HOME",
)
FAKE_PYTHON = (
    'printf "%s\\0" "$0" "$@" > "$WRAPPER_ARGS"\n'
    + "for name in "
    + " ".join(ENV_NAMES)
    + r'''; do
    printf '%s\0' "${!name-<unset>}"
done > "$WRAPPER_ENV"
if [[ "${CHECK_EVAL_LOCK:-0}" == 1 ]]; then
    exec 8>.cache/phase5/eval.lock
    if flock -n 8; then
        printf 'eval lock was not held through exec\n' >&2
        exit 90
    fi
fi
exit "${FAKE_PYTHON_EXIT:-0}"
'''
)


def write_executable(path: Path, body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("#!/bin/bash\nset -euo pipefail\n" + body, encoding="utf-8")
    path.chmod(0o755)


@pytest.fixture
def wrapper_repo(tmp_path: Path) -> tuple[Path, dict[str, str]]:
    repo = tmp_path / "repo with spaces"
    (repo / "scripts").mkdir(parents=True)
    for stage in STAGES:
        name = f"phase5_{stage}.sh"
        shutil.copyfile(ROOT / "scripts" / name, repo / "scripts" / name)

    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    # An allowlisted PATH and a fresh environment keep real runtimes, provider
    # clients, credentials, and shell startup hooks out of wrapper subprocesses.
    for name in ("bash", "dirname", "realpath", "date", "mkdir", "flock"):
        executable = shutil.which(name)
        assert executable is not None, f"wrapper tests require {name}"
        (bin_dir / name).symlink_to(executable)
    write_executable(bin_dir / "python", FAKE_PYTHON)
    write_executable(repo / ".venv" / "bin" / "python", FAKE_PYTHON)
    write_executable(
        bin_dir / "mountpoint",
        '[[ "$#" == 2 && "$1" == -q && "$2" == /workspace ]] || exit 91\n'
        'exit "${WORKSPACE_MOUNTPOINT_STATUS:-32}"\n',
    )
    home = tmp_path / "home"
    home.mkdir()
    return repo, {
        "PATH": str(bin_dir),
        "HOME": str(home),
        "LC_ALL": "C",
        "WRAPPER_ARGS": str(tmp_path / "args.bin"),
        "WRAPPER_ENV": str(tmp_path / "env.bin"),
    }


def run_wrapper(
    repo: Path, env: dict[str, str], stage: str, *args: str
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["/bin/bash", str(repo / "scripts" / f"phase5_{stage}.sh"), *args],
        cwd=repo.parent,
        env=env,
        capture_output=True,
        text=True,
        timeout=10,
        check=False,
    )


def recorded_values(path: str) -> list[str]:
    return Path(path).read_bytes().decode("utf-8").removesuffix("\0").split("\0")


def recorded_env(env: dict[str, str]) -> dict[str, str]:
    return dict(zip(ENV_NAMES, recorded_values(env["WRAPPER_ENV"]), strict=True))


@pytest.mark.parametrize("stage", STAGES)
@pytest.mark.parametrize("mounted", [False, True])
@pytest.mark.parametrize("existing", [None, "", "custom cache with spaces"])
def test_hf_home_defaults_and_override(
    wrapper_repo: tuple[Path, dict[str, str]], stage: str, mounted: bool, existing: str | None
) -> None:
    repo, env = wrapper_repo
    env["WORKSPACE_MOUNTPOINT_STATUS"] = "0" if mounted else "32"
    if existing is not None:
        env["HF_HOME"] = str(repo.parent / existing) if existing else ""

    result = run_wrapper(repo, env, stage)

    assert result.returncode == 0, result.stderr
    values = recorded_env(env)
    cache_root = Path("/workspace") if mounted else repo
    assert values["HF_HOME"] == (env.get("HF_HOME") or str(cache_root / ".cache/huggingface"))
    assert values["PYTHONPATH"] == f"{repo}/src:{repo}"
    assert values["RAG_DENSE_MODEL"] == "<unset>"
    assert values["RAG_RERANKER_MODEL"] == "<unset>"
    assert values["RAG_EMBEDDER_ID"] == "<unset>"


@pytest.mark.parametrize("stage", STAGES)
@pytest.mark.parametrize("exit_code", [0, 37])
def test_delegation_preserves_args_environment_and_exit_status(
    wrapper_repo: tuple[Path, dict[str, str]], stage: str, exit_code: int
) -> None:
    repo, env = wrapper_repo
    preserved = {
        "PYTHONPATH": "/caller/src:/caller/extensions",
        "RAG_EVAL_DATABASE_URL": "postgresql://localhost/custom_eval",
        "RAG_DENSE_MODEL": "caller-dense-model",
        "RAG_RERANKER_MODEL": "caller-reranker-model",
        "RAG_EMBEDDER_ID": "caller-embedder-id",
        "HF_HUB_CACHE": "/caller/hub",
        "TRANSFORMERS_CACHE": "/caller/transformers",
        "SENTENCE_TRANSFORMERS_HOME": "/caller/sentence-transformers",
    }
    env.update(preserved, FAKE_PYTHON_EXIT=str(exit_code))
    args = ("--outputs" if stage == "eval" else "--output", "output with spaces", "*", "")

    result = run_wrapper(repo, env, stage, *args)

    assert result.returncode == exit_code, result.stderr
    interpreter = repo / ".venv/bin/python" if stage == "eval" else Path(env["PATH"]) / "python"
    assert recorded_values(env["WRAPPER_ARGS"]) == [
        str(interpreter), f"scripts/phase5_{stage}.py", *args
    ]
    values = recorded_env(env)
    assert values["PWD"] == str(repo)
    assert values["PYTHONUNBUFFERED"] == "1"
    assert values["TOKENIZERS_PARALLELISM"] == "false"
    assert values["HF_HUB_DISABLE_TELEMETRY"] == "1"
    preserved["PYTHONPATH"] = f"{repo}/src:{repo}:" + preserved["PYTHONPATH"]
    assert {key: values[key] for key in preserved} == preserved


def test_eval_creates_lock_directory_and_holds_lock_through_exec(
    wrapper_repo: tuple[Path, dict[str, str]],
) -> None:
    repo, env = wrapper_repo
    env["CHECK_EVAL_LOCK"] = "1"
    assert not (repo / ".cache").exists()

    result = run_wrapper(repo, env, "eval")

    assert result.returncode == 0, result.stderr
    assert not (repo.parent / ".cache").exists()
    assert recorded_env(env)["RAG_EVAL_DATABASE_URL"] == (
        "postgresql://postgres:postgres@127.0.0.1:5432/evidence_rag_eval"
    )
    with (repo / ".cache/phase5/eval.lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)


def test_eval_refuses_contended_lock_and_runs_after_release(
    wrapper_repo: tuple[Path, dict[str, str]],
) -> None:
    repo, env = wrapper_repo
    lock_path = repo / ".cache/phase5/eval.lock"
    lock_path.parent.mkdir(parents=True)
    with lock_path.open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        result = run_wrapper(repo, env, "eval")
    assert result.returncode == 1
    assert "another runner holds .cache/phase5/eval.lock" in result.stderr
    assert not Path(env["WRAPPER_ARGS"]).exists()
    result = run_wrapper(repo, env, "eval")
    assert result.returncode == 0, result.stderr
    assert Path(env["WRAPPER_ARGS"]).is_file()


@pytest.mark.parametrize("missing", [False, True])
def test_eval_requires_executable_host_venv(
    wrapper_repo: tuple[Path, dict[str, str]], missing: bool
) -> None:
    repo, env = wrapper_repo
    interpreter = repo / ".venv/bin/python"
    if missing:
        interpreter.unlink()
    else:
        interpreter.chmod(0o644)

    result = run_wrapper(repo, env, "eval")

    assert result.returncode == 1
    assert f"missing host interpreter {interpreter}" in result.stderr
    assert not Path(env["WRAPPER_ARGS"]).exists()
    assert not (repo / ".cache").exists()


@pytest.mark.parametrize(
    "args", [(), ("--no-stop",), ("--stop-on-exit",), ("--no-stop", "--stop-on-exit")]
)
def test_gpu_leaves_shutdown_flags_to_python(
    wrapper_repo: tuple[Path, dict[str, str]], args: tuple[str, ...]
) -> None:
    repo, env = wrapper_repo

    result = run_wrapper(repo, env, "gpu", *args)

    assert result.returncode == 0, result.stderr
    assert recorded_values(env["WRAPPER_ARGS"])[1:] == ["scripts/phase5_gpu.py", *args]


@pytest.mark.parametrize("mounted", [False, True])
@pytest.mark.parametrize("on_runpod", [False, True])
def test_gpu_advises_on_nonpersistent_runpod_checkout(
    wrapper_repo: tuple[Path, dict[str, str]], mounted: bool, on_runpod: bool
) -> None:
    repo, env = wrapper_repo
    env["WORKSPACE_MOUNTPOINT_STATUS"] = "0" if mounted else "32"
    if on_runpod:
        env["RUNPOD_POD_ID"] = "fake-pod"

    result = run_wrapper(repo, env, "gpu")

    assert result.returncode == 0, result.stderr
    if on_runpod:
        assert "advisory" in result.stderr
        assert str(repo) in result.stderr
        assert "/workspace" in result.stderr
        assert "phase5_outputs.tar.gz" in result.stderr
    else:
        assert result.stderr == ""


@pytest.mark.parametrize("stage", STAGES)
def test_missing_mountpoint_uses_repo_cache(
    wrapper_repo: tuple[Path, dict[str, str]], stage: str
) -> None:
    repo, env = wrapper_repo
    (Path(env["PATH"]) / "mountpoint").unlink()

    result = run_wrapper(repo, env, stage)

    assert result.returncode == 0, result.stderr
    assert recorded_env(env)["HF_HOME"] == str(repo / ".cache/huggingface")
    assert result.stderr == ""
