#
# Copyright (c) 2025 CESNET z.s.p.o.
#
# This file is a part of pytest-oarepo (see https://github.com/oarepo/pytest_oarepo).
#
# pytest-oarepo is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
"""Fixtures for creating test users."""

from __future__ import annotations

import base64
import os
from typing import TYPE_CHECKING

import pytest
from sqlalchemy.exc import IntegrityError

from pytest_oarepo.functions import _index_users

if TYPE_CHECKING:
    from flask import Flask
    from invenio_db.shared import SQLAlchemy
    from pytest_invenio.user import UserFixtureBase


@pytest.fixture
def password() -> str:
    """Return password."""
    return base64.b64encode(os.urandom(16)).decode("utf-8")


def _create_user(user_fixture: UserFixtureBase, app: Flask, db: SQLAlchemy) -> None:
    """Create users, reusing it if it already exists."""
    try:
        user_fixture.create(app, db)
    except IntegrityError:
        datastore = app.extensions["security"].datastore
        user_fixture._user = datastore.get_user_by_email(  # noqa: SLF001
            user_fixture.email
        )
        user_fixture._app = app  # noqa: SLF001


@pytest.fixture
def users(app: Flask, db: SQLAlchemy, UserFixture: type[UserFixtureBase], password: str) -> list[UserFixtureBase]:  # noqa N803
    """Predefined user fixtures."""
    user1 = UserFixture(
        email="user1@example.org",
        password=password,
        active=True,
        confirmed=True,
        user_profile={
            "affiliations": "CERN",
        },
        preferences={"locale": "en", "visibility": "public"},
    )
    _create_user(user1, app, db)

    user2 = UserFixture(
        email="user2@example.org",
        password=password,
        username="beetlesmasher",
        active=True,
        confirmed=True,
        user_profile={
            "affiliations": "CERN",
        },
        preferences={"locale": "en", "visibility": "public"},
    )
    _create_user(user2, app, db)

    user3 = UserFixture(
        email="user3@example.org",
        password=password,
        username="beetlesmasherXXL",
        user_profile={
            "full_name": "Maxipes Fik",
            "affiliations": "CERN",
        },
        active=True,
        confirmed=True,
        preferences={"locale": "en", "visibility": "public"},
    )
    _create_user(user3, app, db)

    user4 = UserFixture(
        email="user4@example.org",
        password=password,
        username="african",
        preferences={
            "timezone": "Africa/Dakar",  # something without daylight saving time; +0.0
            "locale": "en",
            "visibility": "public",
        },
        user_profile={
            "affiliations": "CERN",
        },
        active=True,
        confirmed=True,
    )
    _create_user(user4, app, db)

    user5 = UserFixture(
        email="user5@example.org",
        password=password,
        username="mexican",
        preferences={
            "timezone": "America/Mexico_City",  # something without daylight saving time
            "locale": "en",
            "visibility": "public",
        },
        user_profile={
            "affiliations": "CERN",
        },
        active=True,
        confirmed=True,
    )
    _create_user(user5, app, db)

    db.session.commit()
    _index_users()
    return [user1, user2, user3, user4, user5]


@pytest.fixture
def user_with_cs_locale(
    app: Flask,
    db: SQLAlchemy,
    UserFixture: type[UserFixtureBase],  # noqa N803
    password: str,
) -> UserFixtureBase:
    """User with Czech locale."""
    u = UserFixture(
        email="pat@mat.cz",
        password=password,
        username="patmat",
        user_profile={
            "full_name": "patmat",
            "affiliations": "cesnet",
        },
        preferences={"locale": "cs"},
        active=True,
        confirmed=True,
    )
    _create_user(u, app, db)
    db.session.commit()
    _index_users()
    return u
