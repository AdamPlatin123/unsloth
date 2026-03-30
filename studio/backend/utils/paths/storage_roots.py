# SPDX-License-Identifier: AGPL-3.0-only
# Copyright 2026-present the Unsloth AI Inc. team. All rights reserved. See /studio/LICENSE.AGPL-3.0

from __future__ import annotations

import json
import os
from pathlib import Path
import tempfile


def studio_root() -> Path:
    return Path.home() / ".unsloth" / "studio"


def cache_root() -> Path:
    """Central cache directory for all studio downloads (models, datasets, etc.)."""
    return Path.home() / ".unsloth" / "studio" / "cache"


def assets_root() -> Path:
    return studio_root() / "assets"


def datasets_root() -> Path:
    return assets_root() / "datasets"


def dataset_uploads_root() -> Path:
    return datasets_root() / "uploads"


def recipe_datasets_root() -> Path:
    return datasets_root() / "recipes"


def outputs_root() -> Path:
    return studio_root() / "outputs"


def exports_root() -> Path:
    return studio_root() / "exports"


def auth_root() -> Path:
    return studio_root() / "auth"


def auth_db_path() -> Path:
    return auth_root() / "auth.db"


def tmp_root() -> Path:
    return Path(tempfile.gettempdir()) / "unsloth-studio"


def seed_uploads_root() -> Path:
    return datasets_root() / "seed-uploads"


def unstructured_seed_cache_root() -> Path:
    return tmp_root() / "unstructured-seed-cache"


def unstructured_uploads_root() -> Path:
    return datasets_root() / "unstructured-uploads"


def oxc_validator_tmp_root() -> Path:
    return tmp_root() / "oxc-validator"


def tensorboard_root() -> Path:
    return studio_root() / "runs"


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents = True, exist_ok = True)
    return path


# ---------------------------------------------------------------------------
# Studio config (persisted as JSON in ~/.unsloth/studio/config.json)
# ---------------------------------------------------------------------------

def config_path() -> Path:
    """Return path to the studio config file."""
    return studio_root() / "config.json"


def load_studio_config() -> dict:
    """Read studio config; return empty dict on missing / corrupt file."""
    cp = config_path()
    if not cp.is_file():
        return {}
    try:
        return json.loads(cp.read_text(encoding = "utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def save_studio_config(config: dict) -> None:
    """Write *config* dict to the studio config file."""
    cp = config_path()
    ensure_dir(cp.parent)
    cp.write_text(
        json.dumps(config, indent = 2, ensure_ascii = False) + "\n",
        encoding = "utf-8",
    )


def apply_china_mirrors(enabled: bool) -> None:
    """Set or clear China-mainland mirror environment variables.

    When *enabled* is True, sets HF_ENDPOINT / PIP_INDEX_URL / UV_INDEX_URL
    to domestic mirrors.  When False, only removes values that match the
    mirror URLs we set — user-supplied values are preserved.
    """
    mirrors = {
        "HF_ENDPOINT": "https://hf-mirror.com",
        "PIP_INDEX_URL": "https://pypi.tuna.tsinghua.edu.cn/simple",
        "UV_INDEX_URL": "https://pypi.tuna.tsinghua.edu.cn/simple",
    }
    if enabled:
        for key, value in mirrors.items():
            os.environ[key] = value
    else:
        for key, value in mirrors.items():
            if os.environ.get(key) == value:
                os.environ.pop(key, None)


def _setup_cache_env() -> None:
    """Set cache environment variables for HuggingFace, uv, and vLLM.

    Only sets variables that are not already set by the user, so
    explicit overrides (e.g. HF_HOME=/data/hf) are respected.
    Works on Linux, macOS, and Windows.
    """
    root = cache_root()
    hf_dir = root / "huggingface"
    defaults = {
        "HF_HOME": str(hf_dir),
        "HF_HUB_CACHE": str(hf_dir / "hub"),
        "HF_XET_CACHE": str(hf_dir / "xet"),
        "UV_CACHE_DIR": str(root / "uv"),
        "VLLM_CACHE_ROOT": str(root / "vllm"),
    }
    for key, value in defaults.items():
        if key not in os.environ:
            os.environ[key] = value
            Path(value).mkdir(parents = True, exist_ok = True)

    # Restore China mirror setting from persisted config
    cfg = load_studio_config()
    if cfg.get("china_mirror_enabled"):
        apply_china_mirrors(True)


def ensure_studio_directories() -> None:
    """Create all standard studio directories on startup."""
    for dir_fn in (
        studio_root,
        assets_root,
        datasets_root,
        dataset_uploads_root,
        recipe_datasets_root,
        unstructured_uploads_root,
        outputs_root,
        exports_root,
        auth_root,
        tensorboard_root,
    ):
        ensure_dir(dir_fn())
    _setup_cache_env()


def _clean_relative_path(
    path_value: str, *, strip_prefixes: tuple[str, ...] = ()
) -> Path:
    path = Path(path_value).expanduser()
    parts = [part for part in path.parts if part not in ("", ".")]
    while parts and parts[0] in strip_prefixes:
        parts = parts[1:]
    return Path(*parts) if parts else Path()


def resolve_under_root(
    path_value: str | None,
    *,
    root: Path,
    strip_prefixes: tuple[str, ...] = (),
) -> Path:
    if not path_value or not str(path_value).strip():
        return root

    path = Path(str(path_value).strip()).expanduser()
    if path.is_absolute():
        return path

    cleaned = _clean_relative_path(str(path), strip_prefixes = strip_prefixes)
    return root / cleaned


def resolve_output_dir(path_value: str | None = None) -> Path:
    return resolve_under_root(
        path_value,
        root = outputs_root(),
        strip_prefixes = ("outputs",),
    )


def resolve_export_dir(path_value: str | None = None) -> Path:
    return resolve_under_root(
        path_value,
        root = exports_root(),
        strip_prefixes = ("exports",),
    )


def resolve_tensorboard_dir(path_value: str | None = None) -> Path:
    return resolve_under_root(
        path_value,
        root = tensorboard_root(),
        strip_prefixes = ("runs", "tensorboard"),
    )


def resolve_dataset_path(path_value: str) -> Path:
    path = Path(path_value).expanduser()
    if path.is_absolute():
        return path

    parts = [part for part in Path(path_value).parts if part not in ("", ".")]
    if parts[:2] == ["assets", "datasets"]:
        parts = parts[2:]
    if parts and parts[0] == "uploads":
        cleaned = Path(*parts[1:]) if len(parts) > 1 else Path()
        return dataset_uploads_root() / cleaned
    if parts and parts[0] == "recipes":
        cleaned = Path(*parts[1:]) if len(parts) > 1 else Path()
        return recipe_datasets_root() / cleaned

    cleaned = Path(*parts) if parts else Path()
    candidates = [
        dataset_uploads_root() / cleaned,
        recipe_datasets_root() / cleaned,
        datasets_root() / cleaned,
        dataset_uploads_root() / cleaned.name,
        recipe_datasets_root() / cleaned.name,
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return candidates[0]
