from invenio_access.permissions import system_identity
from invenio_communities.proxies import current_communities
from invenio_users_resources.proxies import current_users_service


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
    """Remove a user from a community."""
    delete_data = {
        "members": [{"type": "user", "id": user_id}],
    }
    member_delete = current_communities.service.members.delete(
        system_identity, community_id, delete_data
    )


def set_community_workflow(community_id, workflow="default"):
    """
    Set default workflow of a community.
    """
    community_item = current_communities.service.read(system_identity, community_id)
    current_communities.service.update(
        system_identity,
        community_id,
        data={**community_item.data, "custom_fields": {"workflow": workflow}},
    )
