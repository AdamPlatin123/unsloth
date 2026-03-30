# SPDX-License-Identifier: AGPL-3.0-only
# Copyright 2026-present the Unsloth AI Inc. team. All rights reserved. See /studio/LICENSE.AGPL-3.0

"""
Settings API routes (China mirror toggle, etc.)
"""

import os

from fastapi import APIRouter, Depends

from auth.authentication import get_current_subject
from models.settings import ChinaMirrorRequest, ChinaMirrorResponse
from utils.paths import load_studio_config, save_studio_config, apply_china_mirrors

router = APIRouter()


@router.get("/china-mirror", response_model = ChinaMirrorResponse)
async def get_china_mirror(
    _current_subject: str = Depends(get_current_subject),
) -> ChinaMirrorResponse:
    """Return current China-mirror setting."""
    cfg = load_studio_config()
    enabled = bool(cfg.get("china_mirror_enabled"))
    return ChinaMirrorResponse(
        enabled = enabled,
        hf_endpoint = os.environ.get("HF_ENDPOINT") if enabled else None,
    )


@router.put("/china-mirror", response_model = ChinaMirrorResponse)
async def set_china_mirror(
    request: ChinaMirrorRequest,
    _current_subject: str = Depends(get_current_subject),
) -> ChinaMirrorResponse:
    """Enable or disable China-mainland mirrors and persist the choice."""
    cfg = load_studio_config()
    cfg["china_mirror_enabled"] = request.enabled
    save_studio_config(cfg)
    apply_china_mirrors(request.enabled)

    return ChinaMirrorResponse(
        enabled = request.enabled,
        hf_endpoint = os.environ.get("HF_ENDPOINT") if request.enabled else None,
    )
