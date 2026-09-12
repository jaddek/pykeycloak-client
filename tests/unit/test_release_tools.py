import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parents[2]
SYNC_VERSION = ROOT / "bin" / "sync_version_from_tag.py"
CHECK_SBOM = ROOT / "bin" / "check_sbom_licenses.py"


def run_script(script: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(script), *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


def test_sync_version_updates_release_tag(tmp_path: Path):
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text('version = "0.8.2"\n', encoding="utf-8")

    result = run_script(SYNC_VERSION, "--tag", "v0.9.0", "--file", str(pyproject))

    assert result.returncode == 0
    assert 'version = "0.9.0"' in pyproject.read_text(encoding="utf-8")


def test_sync_version_ignores_non_release_tag(tmp_path: Path):
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text('version = "0.8.2"\n', encoding="utf-8")

    result = run_script(SYNC_VERSION, "--tag", "dev", "--file", str(pyproject))

    assert result.returncode == 0
    assert 'version = "0.8.2"' in pyproject.read_text(encoding="utf-8")


def test_sync_version_fails_without_version(tmp_path: Path):
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text("[project]\nname = 'example'\n", encoding="utf-8")

    result = run_script(SYNC_VERSION, "--tag", "v0.9.0", "--file", str(pyproject))

    assert result.returncode == 1
    assert "Could not find" in result.stderr


def test_sbom_policy_rejects_denied_license(tmp_path: Path):
    sbom = tmp_path / "sbom.json"
    sbom.write_text(
        json.dumps(
            {
                "components": [
                    {
                        "name": "example",
                        "version": "1.0.0",
                        "licenses": [{"license": {"id": "GPL-3.0-only"}}],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    policy = tmp_path / "policy.toml"
    policy.write_text('deny = ["GPL-3.0-only"]\n', encoding="utf-8")

    result = run_script(CHECK_SBOM, "--sbom", str(sbom), "--policy", str(policy))

    assert result.returncode == 1
    assert "example@1.0.0: GPL-3.0-only" in result.stderr


def test_sbom_policy_allows_permitted_license(tmp_path: Path):
    sbom = tmp_path / "sbom.json"
    sbom.write_text(
        json.dumps(
            {
                "components": [
                    {
                        "name": "example",
                        "version": "1.0.0",
                        "licenses": [{"license": {"id": "MIT"}}],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    policy = tmp_path / "policy.toml"
    policy.write_text('deny = ["GPL-3.0-only"]\n', encoding="utf-8")

    result = run_script(CHECK_SBOM, "--sbom", str(sbom), "--policy", str(policy))

    assert result.returncode == 0
    assert "passed" in result.stdout
