#
# Copyright (c) 2025 CESNET z.s.p.o.
#
# This file is a part of pytest-oarepo (see https://github.com/oarepo/pytest_oarepo).
#
# pytest-oarepo is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
"""Fixtures for communities."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import pytest
from invenio_communities.cli import create_communities_custom_field
from invenio_communities.communities.records.api import Community
from invenio_communities.proxies import current_communities
from invenio_pidstore.errors import PIDDoesNotExistError
from oarepo_communities.proxies import current_oarepo_communities

from pytest_oarepo.functions import _index_users

if TYPE_CHECKING:
    from flask import Flask


@pytest.fixture
def community_inclusion_service():
    return current_oarepo_communities.community_inclusion_service


@pytest.fixture
def community_records_service():
    return current_oarepo_communities.community_records_service


@pytest.fixture
def minimal_community() -> dict[str, Any]:
    """Default data used for creating a new community."""
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


@pytest.fixture
def init_communities_cf(app: Flask, db, cache) -> None:
    """Initialize oarepo custom fields including community specific ones."""
    result = app.test_cli_runner().invoke(create_communities_custom_field, [])
    assert result.exit_code == 0
    Community.index.refresh()


@pytest.fixture
def community(app: Flask, community_owner, community_get_or_create):
    """Basic community."""
    return community_get_or_create(community_owner)


@pytest.fixture
def communities(app, community_owner, community_get_or_create):
    return {
        "aaa": community_get_or_create(community_owner, slug="aaa"),
        "bbb": community_get_or_create(community_owner, slug="bbb"),
    }


@pytest.fixture
def community_owner(UserFixture, app, db):
    """User fixture used as owner of the community fixture."""
    u = UserFixture(
        email="community_owner@inveniosoftware.org",
        password="community_owner",
        preferences={"locale": "en"},
    )
    u.create(app, db)
    return u


@pytest.fixture
def community_get_or_create(minimal_community):
    """Function returning existing community or creating new one if one with the same slug doesn't exist."""

    def _get_or_create(community_owner, slug=None, community_dict=None, workflow=None):
        """Util to get or create community, to avoid duplicate error."""
        community_dict = community_dict if community_dict else minimal_community
        slug = slug if slug else community_dict["slug"]
        community_dict["slug"] = slug
        try:
            c = current_communities.service.record_cls.pid.resolve(slug)
        except PIDDoesNotExistError:
            c = current_communities.service.create(
                community_owner.identity,
                {
                    **community_dict,
                    "custom_fields": {"workflow": workflow or "default"},
                },
            )
            Community.index.refresh()
            _index_users()
            community_owner._identity = None  # the problem with creating

        return c

    return _get_or_create
