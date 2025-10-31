#
# Copyright (c) 2025 CESNET z.s.p.o.
#
# This file is a part of pytest-oarepo (see https://github.com/oarepo/pytest_oarepo).
#
# pytest-oarepo is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
"""Functions used in communities."""

from __future__ import annotations

from typing import TYPE_CHECKING

from invenio_access.permissions import system_identity
from invenio_communities.proxies import current_communities

from pytest_oarepo.functions import _index_users

if TYPE_CHECKING:
    from pytest_invenio.user import UserFixtureBase


def invite(user_fixture: UserFixtureBase, community_id: str, role: str) -> None:
    """Add/invite a user to a community with a specific role."""
    invitation_data = {
        "members": [
            {
                "type": "user",
                "id": user_fixture.id,
            }
        ],
        "role": role,
        "visible": True,
    }
    current_communities.service.members.add(system_identity, community_id, invitation_data)
    _index_users()
    user_fixture._identity = None  # noqa SLF001


def remove_member_from_community(user_id: str, community_id: str) -> None:
    """Remove a user from a community."""
    delete_data = {
        "members": [{"type": "user", "id": user_id}],
    }
    current_communities.service.members.delete(system_identity, community_id, delete_data)


def set_community_workflow(community_id: str, workflow: str = "default") -> None:
    """Set default workflow of a community."""
    community_item = current_communities.service.read(system_identity, community_id)
    current_communities.service.update(
        system_identity,
        community_id,
        data={**community_item.data, "custom_fields": {"workflow": workflow}},
    )
