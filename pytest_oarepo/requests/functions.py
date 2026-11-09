# SPDX-FileCopyrightText: 2025 CESNET z.s.p.o
# SPDX-License-Identifier: MIT

"""Test functions for requests."""

from __future__ import annotations

from typing import Any, cast


def get_request_type(request_types_json: list[dict[str, Any]], request_type: str) -> dict[str, Any] | None:
    """Get request type from request types json."""
    selected_entry = [entry for entry in request_types_json if entry["type_id"] == request_type]
    if not selected_entry:
        return None
    return selected_entry[0]


def get_request_create_link(request_types_json: list[dict[str, Any]], request_type: str) -> str:
    """Get request create link from request types json."""
    selected_entry = get_request_type(request_types_json, request_type)
    if not selected_entry:
        raise ValueError(f"Request type {request_type} not found in request types")
    return cast("str", selected_entry["links"]["actions"]["create"])
