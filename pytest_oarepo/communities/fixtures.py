import pytest
from invenio_communities.cli import create_communities_custom_field
from oarepo_communities.proxies import current_oarepo_communities
from invenio_communities.communities.records.api import Community
from invenio_communities.proxies import current_communities
from invenio_pidstore.errors import PIDDoesNotExistError

from pytest_oarepo.communities.functions import _index_users


@pytest.fixture()
def community_inclusion_service():
    return current_oarepo_communities.community_inclusion_service


@pytest.fixture()
def community_records_service():
    return current_oarepo_communities.community_records_service

@pytest.fixture()
def minimal_community():
    """
    Default data used for creating a new community.
    """
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


@pytest.fixture()
def init_communities_cf(app, db, cache):
    """
    Initialize oarepo custom fields including community specific ones.
    """
    from oarepo_runtime.services.custom_fields.mappings import prepare_cf_indices

    prepare_cf_indices()
    result = app.test_cli_runner().invoke(create_communities_custom_field, [])
    assert result.exit_code == 0
    Community.index.refresh()


@pytest.fixture()
def community(app, community_owner, community_get_or_create):
    """
    Basic community.
    """
    return community_get_or_create(community_owner)


@pytest.fixture()
def communities(app, community_owner, community_get_or_create):
    return {
        "aaa": community_get_or_create(community_owner, slug="aaa"),
        "bbb": community_get_or_create(community_owner, slug="bbb"),
    }


@pytest.fixture()
def community_owner(UserFixture, app, db):
    """
    User fixture used as owner of the community fixture.
    """
    u = UserFixture(
        email="community_owner@inveniosoftware.org",
        password="community_owner",
    )
    u.create(app, db)
    return u

@pytest.fixture()
def community_get_or_create(minimal_community):
    """
    Function returning existing community or creating new one if one with the same slug doesn't exist.
    """
    def _get_or_create(
        community_owner, slug=None, community_dict=None, workflow=None
    ):
        """Util to get or create community, to avoid duplicate error."""
        community_dict = community_dict if community_dict else minimal_community
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
            community_owner._identity = None  # the problem with creating

        return c
    return _get_or_create
