from invenio_communities.proxies import current_communities
from invenio_access.permissions import system_identity
from invenio_users_resources.proxies import current_users_service
import copy

import pytest
from invenio_access.permissions import system_identity
from invenio_communities.cli import create_communities_custom_field
from invenio_communities.communities.records.api import Community
from invenio_communities.generators import CommunityRoleNeed
from invenio_communities.proxies import current_communities
from invenio_pidstore.errors import PIDDoesNotExistError
from oarepo_communities.proxies import current_oarepo_communities

from pytest_oarepo.communities.constants import MINIMAL_COMMUNITY


def _index_users():
    current_users_service.indexer.process_bulk_queue()
    current_users_service.record_cls.index.refresh()


def invite(user_fixture, community_id, role):
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
    current_communities.service.members.add(
        system_identity, community_id, invitation_data
    )
    _index_users()
    user_fixture._identity = None

def remove_member_from_community(user_id, community_id):
    """Add/invite a user to a community with a specific role."""
    delete_data = {
        "members": [{"type": "user", "id": user_id}],
    }
    member_delete = current_communities.service.members.delete(
        system_identity, community_id, delete_data
    )

def set_community_workflow(community_id, workflow="default"):
    community_item = current_communities.service.read(system_identity, community_id)
    current_communities.service.update(
        system_identity,
        community_id,
        data={**community_item.data, "custom_fields": {"workflow": workflow}},
    )

def community_get_or_create(community_owner, slug=None, community_dict=None, workflow=None):
    """Util to get or create community, to avoid duplicate error."""
    community_dict = community_dict if community_dict else MINIMAL_COMMUNITY
    slug = slug if slug else community_dict["slug"]
    community_dict["slug"] = slug
    try:
        c = current_communities.service.record_cls.pid.resolve(slug)
    except PIDDoesNotExistError:
        c = current_communities.service.create(
            community_owner.identity,
            {**community_dict, "custom_fields": {"workflow": workflow or "default"}},
        )
        Community.index.refresh()
        _index_users()
        community_owner._identity = None # the problem with creating
        identity = community_owner.identity

    return c

"""
def create_community(slug, community_owner, workflow="default"):
    minimal_community_actual = copy.deepcopy(MINIMAL_COMMUNITY)
    minimal_community_actual["slug"] = slug
    community = community_get_or_create(
        community_owner.identity, minimal_community_actual
    )
    community_owner.identity.provides.add(
        CommunityRoleNeed(community.data["id"], "owner")
    )
    set_community_workflow(community.id, workflow=workflow)
    return community
"""



