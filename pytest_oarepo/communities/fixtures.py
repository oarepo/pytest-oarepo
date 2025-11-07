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

from typing import TYPE_CHECKING, Any, Protocol, cast

import pytest
from invenio_access.permissions import system_identity
from invenio_communities.cli import create_communities_custom_field
from invenio_communities.communities.records.api import Community
from invenio_communities.proxies import current_communities
from invenio_pidstore.errors import PIDDoesNotExistError

from pytest_oarepo.functions import _index_users

if TYPE_CHECKING:
    from collections.abc import Callable

    from flask import Flask
    from invenio_db.shared import SQLAlchemy
    from pytest_invenio.user import UserFixtureBase


class CommunityGetOrCreateFn(Protocol):
    """Function returning existing community or creating new one if one with the same slug doesn't exist."""

    def __call__(
        self,
        community_owner: UserFixtureBase,
        slug: str | None = ...,
        community_dict: dict[str, Any] | None = ...,
        workflow: str | None = ...,
    ) -> Community:  # type: ignore[reportReturnType]
        """Get or create community."""


@pytest.fixture
def minimal_community() -> dict[str, Any]:
    """Return default data used for creating a new community."""
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
def init_communities_cf(app: Flask, cache: Any) -> None:  # noqa ARG001
    result = app.test_cli_runner().invoke(create_communities_custom_field, [])
    if result.exit_code != 0:
        raise RuntimeError(f"Failed to initialize communities custom fields: {result.output}")
    Community.index.refresh()  # type: ignore[reportAttributeAccessIssue]


@pytest.fixture
def community(
    app: Flask,  # noqa ARG001
    community_owner: UserFixtureBase,
    community_get_or_create: CommunityGetOrCreateFn,
) -> Community:
    """Return basic community."""
    return community_get_or_create(community_owner)


@pytest.fixture
def communities(
    app: Flask,  # noqa ARG001
    community_owner: UserFixtureBase,
    community_get_or_create: CommunityGetOrCreateFn,
) -> dict[str, Community]:
    """Return two communities."""
    return {
        "aaa": community_get_or_create(community_owner, slug="aaa"),
        "bbb": community_get_or_create(community_owner, slug="bbb"),
    }


@pytest.fixture
def community_owner(UserFixture, app: Flask, db: SQLAlchemy, password: str) -> UserFixtureBase:  # noqa N803
    """User fixture used as owner of the community fixture."""
    u = UserFixture(
        email="community_owner@inveniosoftware.org",
        password=password,
        preferences={"locale": "en"},
    )
    u.create(app, db)
    return u


@pytest.fixture
def community_get_or_create(minimal_community: dict[str, Any]) -> CommunityGetOrCreateFn:
    """Return existing community or creating new one if one with the same slug doesn't exist."""

    def _get_or_create(
        community_owner: UserFixtureBase,
        slug: str | None = None,
        community_dict: dict[str, Any] | None = None,
        workflow: str | None = None,
    ) -> Community:
        """Util to get or create community, to avoid duplicate error."""
        community_dict = community_dict if community_dict else minimal_community
        slug = slug if slug else community_dict["slug"]
        if not isinstance(slug, str):
            raise TypeError("Slug must be a string")
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
            c = c._obj  # noqa SLF001
            Community.index.refresh()  # type: ignore[reportAttributeAccessIssue]
            _index_users()
            community_owner._identity = None  # noqa SLF001

        return cast("Community", c)

    return _get_or_create


@pytest.fixture
def invite() -> Callable[[UserFixtureBase, str, str], None]:
    """Add a user to a community with a specific role."""

    def _invite(user_fixture: UserFixtureBase, community_id: str, role: str) -> None:
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

    return _invite
