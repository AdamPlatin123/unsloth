# SPDX-License-Identifier: AGPL-3.0-only
# Copyright 2026-present the Unsloth AI Inc. team. All rights reserved. See /studio/LICENSE.AGPL-3.0

"""
Pydantic models for settings API request/response schemas.
"""

from __future__ import annotations

from pydantic import BaseModel


class ChinaMirrorRequest(BaseModel):
    enabled: bool


class ChinaMirrorResponse(BaseModel):
    enabled: bool
    hf_endpoint: str | None = None
