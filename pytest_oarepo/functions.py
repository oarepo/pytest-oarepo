#
# Copyright (c) 2025 CESNET z.s.p.o.
#
# This file is a part of pytest-oarepo (see https://github.com/oarepo/pytest_oarepo).
#
# pytest-oarepo is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
"""Util used in testing."""

from __future__ import annotations

from collections import defaultdict

from flask import g
from invenio_users_resources.proxies import current_users_service


def _dict_diff(dict1: dict, dict2: dict, path: str = "") -> dict[str, list[str]]:
    ret = defaultdict(list)
    for key in dict1:  # noqa PLC0206
        # Construct path to current element
        new_path = key if path == "" else f"{path}.{key}"

        # Check if the key is in the second dictionary
        if key not in dict2:
            ret["second dict missing"].append(f"{new_path}: Key missing in the second dictionary")
            continue

        # If both values are dictionaries, do a recursive call
        if isinstance(dict1[key], dict) and isinstance(dict2[key], dict):
            sub_result = _dict_diff(dict1[key], dict2[key], new_path)
            ret.update(sub_result)
        # Check if values are the same
        elif dict1[key] != dict2[key]:
            ret["different values"].append(f"{new_path}: {dict1[key]} != {dict2[key]}")

    # Check for keys in the second dictionary but not in the first
    for key in dict2:
        if key not in dict1:
            new_path = key if path == "" else f"{path}.{key}"
            ret["first dict missing"].append(f"{new_path}: Key missing in the first dictionary")
    return ret


# TODO: scrap?
def is_valid_subdict(subdict: dict, dict_: dict) -> bool:
    """Check if subdict is a valid subdict of dict."""
    diff = _dict_diff(subdict, dict_)
    return "different values" not in diff and "second dict missing" not in diff


def _index_users() -> None:
    """Index users."""
    current_users_service.indexer.process_bulk_queue()
    current_users_service.indexer.refresh()


# TODO: scrap?
def clear_babel_context() -> None:
    """Clear babel context."""
    # for invenio 12
    try:
        from flask_babel import SimpleNamespace
    except ImportError:
        return
    g._flask_babel = SimpleNamespace()  # noqa: SLF001
