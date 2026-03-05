#
# Copyright (c) 2026 CESNET z.s.p.o.
#
# This file is a part of pytest-oarepo (see https://github.com/oarepo/pytest_oarepo).
#
# pytest-oarepo is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
"""Fixtures for creating test roles."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import pytest
from invenio_access import ActionRoles
from invenio_access.permissions import system_identity
from invenio_accounts.models import Role
from invenio_accounts.proxies import current_datastore
from invenio_records_resources.services.errors import PermissionDeniedError
from invenio_users_resources.proxies import current_groups_service

if TYPE_CHECKING:
    from collections.abc import Callable

    from flask import Flask
    from invenio_db.shared import SQLAlchemy
    from pytest_invenio.user import UserFixtureBase


def _create_role(id_: str, name: str, description: str, is_managed: bool) -> Role:
    """Create a Role/Group."""
    r = current_datastore.create_role(id=id_, name=name, description=description, is_managed=is_managed)
    current_datastore.commit()

    current_groups_service.indexer.process_bulk_queue()
    current_groups_service.indexer.refresh()
    return r


@pytest.fixture
def roles(db: SQLAlchemy) -> list[Role]:  # noqa: ARG001
    """Create roles."""
    r1 = _create_role(
        id_="it-dep",
        name="it-dep",
        description="IT Department",
        is_managed=False,
    )
    return [r1]


@pytest.fixture
def add_user_in_role(db: SQLAlchemy) -> Callable[[UserFixtureBase, Role | str], None]:
    """Add user to role or creates it if it doesn't exist."""

    def _add_user_in_role(user: UserFixtureBase, role_or_role_name: Role | str) -> None:
        if isinstance(role_or_role_name, str):
            try:
                role = current_groups_service.read(system_identity, role_or_role_name)._group.model.model_obj  # noqa SLF001
            except PermissionDeniedError:  # missing group in db raises this
                role = Role(name=role_or_role_name)
                db.session.add(role_or_role_name)
        else:
            role = role_or_role_name
        # TODO: UserFixtureBase is not typed
        user.user.roles.append(role)  # type: ignore[reportOptionalMemberAccess]
        db.session.commit()

    return _add_user_in_role


@pytest.fixture
def role_ui_serialization(host: str) -> dict[str, Any]:
    """UI serialization of the example role in role fixture."""
    return {
        "label": "it-dep",
        "links": {
            "avatar": f"{host}api/groups/it-dep/avatar.svg",
            "self": f"{host}api/groups/it-dep",
        },
        "reference": {"group": "it-dep"},
        "type": "group",
    }


@pytest.fixture
def role_with_administration_rights(app: Flask, db: SQLAlchemy) -> Role:
    """Set administration rights to the first user and return it."""
    role = _create_role(
        id_="admin",
        name="admin",
        description="Administrator group.",
        is_managed=False,
    )
    actions = app.extensions["invenio-access"].actions
    act = ActionRoles.allow(actions["administration-access"], role_id=role.id)
    db.session.add(act)
    db.session.commit()
    return role
