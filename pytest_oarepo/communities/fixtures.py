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
from pytest_oarepo.communities.functions import community_get_or_create


@pytest.fixture()
def community_inclusion_service():
    return current_oarepo_communities.community_inclusion_service


@pytest.fixture()
def community_records_service():
    return current_oarepo_communities.community_records_service


@pytest.fixture()
def init_communities_cf(app, db, cache):
    from oarepo_runtime.services.custom_fields.mappings import prepare_cf_indices

    prepare_cf_indices()
    result = app.test_cli_runner().invoke(create_communities_custom_field, [])
    assert result.exit_code == 0
    Community.index.refresh()





@pytest.fixture()
def community(app, community_owner):
    return community_get_or_create(community_owner)


@pytest.fixture()
def communities(app, community_owner):
    return {
        "aaa": community_get_or_create(
            community_owner,
            slug="aaa"
        ),
        "bbb": community_get_or_create(
            community_owner,
            slug="bbb"
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
