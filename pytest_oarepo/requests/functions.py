#
# Copyright (c) 2025 CESNET z.s.p.o.
#
# This file is a part of pytest-oarepo (see https://github.com/oarepo/pytest_oarepo).
#
# pytest-oarepo is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
"""Test functions for requests."""

from __future__ import annotations


def get_request_type(request_types_json, request_type):
    selected_entry = [entry for entry in request_types_json if entry["type_id"] == request_type]
    if not selected_entry:
        return None
    return selected_entry[0]


def get_request_create_link(request_types_json, request_type):
    selected_entry = get_request_type(request_types_json, request_type)
    return selected_entry["links"]["actions"]["create"]
