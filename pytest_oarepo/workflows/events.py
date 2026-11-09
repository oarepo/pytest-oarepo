# SPDX-FileCopyrightText: 2026 CESNET z.s.p.o
# SPDX-License-Identifier: MIT

"""Test events."""

from __future__ import annotations

from invenio_requests.customizations import CommentEventType


# events are first defined in workflows
class TestEventType(CommentEventType):
    """Custom EventType."""

    type_id = "T"
