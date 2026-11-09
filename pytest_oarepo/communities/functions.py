# SPDX-FileCopyrightText: 2025 CESNET z.s.p.o
# SPDX-License-Identifier: MIT

"""Functions used in communities."""

from __future__ import annotations

from invenio_access.permissions import system_identity
from invenio_communities.proxies import current_communities


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
