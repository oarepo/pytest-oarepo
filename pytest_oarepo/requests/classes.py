#
# Copyright (c) 2025 CESNET z.s.p.o.
#
# This file is a part of pytest-oarepo (see https://github.com/oarepo/pytest_oarepo).
#
# pytest-oarepo is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
"""Test classes for requests."""

from __future__ import annotations

from invenio_requests.customizations import CommentEventType


class TestEventType(CommentEventType):
    """Custom EventType."""

    type_id = "T"
