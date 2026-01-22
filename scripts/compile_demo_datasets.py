"""Compile demo dataset prompts and update manifests only when changed."""

from __future__ import annotations

import sys
from pathlib import Path
from tempfile import TemporaryDirectory

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

DATASET_ROOT = PROJECT_ROOT / "data" / "demo_datasets"
DATASET_NAMES = ("document_analysis", "local_operations")


def _write_if_changed(source: Path, dest: Path) -> bool:
    content = source.read_text(encoding="utf-8")
    if dest.exists() and dest.read_text(encoding="utf-8") == content:
        return False
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(content, encoding="utf-8")
    return True


def compile_dataset(dataset_name: str) -> bool:
    dataset_dir = DATASET_ROOT / dataset_name
    prompts_root = dataset_dir / "prompts"
    manifest_path = dataset_dir / "manifest.json"
    from promptir.compiler import compile_prompts

    with TemporaryDirectory() as tmpdir:
        temp_manifest = Path(tmpdir) / "manifest.json"
        compile_prompts(str(prompts_root), str(temp_manifest))
        return _write_if_changed(temp_manifest, manifest_path)


def main() -> int:
    updated = False
    for dataset_name in DATASET_NAMES:
        updated = compile_dataset(dataset_name) or updated
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
