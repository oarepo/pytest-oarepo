import copy

import pytest
from invenio_access.permissions import system_identity
from invenio_communities.cli import create_communities_custom_field
from invenio_communities.communities.records.api import Community
from invenio_communities.generators import CommunityRoleNeed
from invenio_communities.proxies import current_communities
from invenio_pidstore.errors import PIDDoesNotExistError
from invenio_users_resources.proxies import current_users_service
from oarepo_communities.proxies import current_oarepo_communities


@pytest.fixture()
def community_inclusion_service():
    return current_oarepo_communities.community_inclusion_service


@pytest.fixture()
def community_records_service():
    return current_oarepo_communities.community_records_service


@pytest.fixture()
def init_cf(app, db, cache):
    from oarepo_runtime.services.custom_fields.mappings import prepare_cf_indices

    prepare_cf_indices()
    result = app.test_cli_runner().invoke(create_communities_custom_field, [])
    assert result.exit_code == 0
    Community.index.refresh()


@pytest.fixture()
def index_users():
    """Index users for an up-to-date user service."""

    def _index():
        current_users_service.indexer.process_bulk_queue()
        current_users_service.record_cls.index.refresh()

    return _index


@pytest.fixture()
def inviter(index_users):
    """Add/invite a user to a community with a specific role."""

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
        index_users()
        user_fixture._identity = None

    return invite


@pytest.fixture()
def remover():
    """Add/invite a user to a community with a specific role."""

    def remove(user_id, community_id):
        """Add/invite a user to a community with a specific role."""
        delete_data = {
            "members": [{"type": "user", "id": user_id}],
        }
        member_delete = current_communities.service.members.delete(
            system_identity, community_id, delete_data
        )

    return remove


@pytest.fixture
def set_community_workflow():
    def _set_community_workflow(community_id, workflow="default"):
        community_item = current_communities.service.read(system_identity, community_id)
        current_communities.service.update(
            system_identity,
            community_id,
            data={**community_item.data, "custom_fields": {"workflow": workflow}},
        )

    return _set_community_workflow


@pytest.fixture(scope="module")
def minimal_community():
    """Minimal community metadata."""
    return {
        "access": {
            "visibility": "public",
            "record_policy": "open",
        },
        "slug": "public",
        "metadata": {
            "title": "My Community",
        },
    }


def _community_get_or_create(identity, community_dict, workflow=None):
    """Util to get or create community, to avoid duplicate error."""
    slug = community_dict["slug"]
    try:
        c = current_communities.service.record_cls.pid.resolve(slug)
    except PIDDoesNotExistError:
        c = current_communities.service.create(
            identity,
            {**community_dict, "custom_fields": {"workflow": workflow or "default"}},
        )
        Community.index.refresh()
        identity.provides.add(CommunityRoleNeed(str(c.id), "owner"))
    return c


@pytest.fixture()
def community(app, minimal_community, community_owner):
    return _community_get_or_create(
        community_owner.identity, minimal_community, workflow="default"
    )


@pytest.fixture()
def communities(app, minimal_community, community_owner):
    return {
        "aaa": _community_get_or_create(
            community_owner.identity,
            {
                **minimal_community,
                "slug": "aaa",
            },
            workflow="default",
        ),
        "bbb": _community_get_or_create(
            community_owner.identity,
            {
                **minimal_community,
                "slug": "bbb",
            },
            workflow="default",
        ),
    }


@pytest.fixture()
def community_owner(UserFixture, app, db):
    u = UserFixture(
        email="community_owner@inveniosoftware.org",
        password="community_owner",
    )
    u.create(app, db)
    return u


@pytest.fixture()
def community_with_workflow_factory(minimal_community, set_community_workflow):
    def create_community(slug, community_owner, workflow="default"):
        minimal_community_actual = copy.deepcopy(minimal_community)
        minimal_community_actual["slug"] = slug
        community = _community_get_or_create(
            community_owner.identity, minimal_community_actual
        )
        community_owner.identity.provides.add(
            CommunityRoleNeed(community.data["id"], "owner")
        )
        set_community_workflow(community.id, workflow=workflow)
        return community

    return create_community
