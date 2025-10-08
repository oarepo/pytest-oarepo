#
# Copyright (c) 2025 CESNET z.s.p.o.
#
# This file is a part of pytest-oarepo (see https://github.com/oarepo/pytest_oarepo).
#
# pytest-oarepo is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
"""Test fixtures."""

from __future__ import annotations

import copy
from typing import TYPE_CHECKING, Any, Protocol

import pytest
from deepmerge import always_merger
from flask_security import login_user
from invenio_accounts.testutils import login_user_via_session
from invenio_app.factory import create_api

if TYPE_CHECKING:
    from collections.abc import Callable, Generator

    from flask import Flask
    from flask.testing import FlaskClient
    from pytest_invenio.user import UserFixtureBase
    from werkzeug.test import TestResponse


@pytest.fixture(scope="module")
def create_app(instance_path: str, entry_points: Generator[None]) -> Callable[..., Flask]:  # noqa: ARG001
    """Application factory fixture."""
    return create_api  # type: ignore [no-any-return]


@pytest.fixture
def host() -> str:
    """Return host url."""
    return "https://127.0.0.1:5000/"


@pytest.fixture
def link2testclient(host: str) -> Callable[[str, bool], str]:
    """Convert link to testclient link."""

    def _link2testclient(link: str, ui: bool = False) -> str:
        base_string = f"{host}api/" if not ui else host
        return link[len(base_string) - 1 :]

    return _link2testclient


@pytest.fixture
def default_record_json() -> dict[str, Any]:
    """Return default data for creating a record, without default workflow."""
    return {
        "metadata": {
            "creators": [
                "Creator 1",
                "Creator 2",
            ],
            "contributors": ["Contributor 1"],
            "title": "blabla",
        },
        "files": {"enabled": False},
    }


@pytest.fixture
def default_record_with_workflow_json(default_record_json: dict[str, Any]) -> dict[str, Any]:
    """Return default data for creating a record."""
    return {
        **default_record_json,
        "parent": {"workflow": "default"},
    }


class PrepareRecordDataFn(Protocol):
    """Protocol for prepare_record_data fixture."""

    def __call__(
        self,
        custom_data: dict[str, Any] | None = ...,
        custom_workflow: str | None = ...,
        additional_data: dict[str, Any] | None = ...,
        add_default_workflow: bool = ...,
    ) -> dict[str, Any]:  # type: ignore[reportReturnType]
        """Call to merge input definitions into data passed to record service."""


@pytest.fixture
def prepare_record_data(default_record_json: dict[str, Any]) -> PrepareRecordDataFn:
    """Merge input definitions into data passed to record service."""

    def _merge_record_data(
        custom_data: dict[str, Any] | None = None,
        custom_workflow: str | None = None,
        additional_data: dict[str, Any] | None = None,
        add_default_workflow: bool = True,
    ) -> dict[str, Any]:
        """Merge input definitions into data passed to record service.

        :param custom_workflow: If user wants to use different workflow that the default one.
        :param additional_data: Additional data beyond the defaults that should be put into the service.
        :param add_default_workflow: Allows user to to pass data into the service without workflow -
        this might be useful for example in case of wanting to use community default workflow.
        """
        record_json = custom_data if custom_data else default_record_json
        json = copy.deepcopy(record_json)
        if add_default_workflow:
            always_merger.merge(json, {"parent": {"workflow": "default"}})
        if custom_workflow:  # specifying this assumes use of workflows
            json.setdefault("parent", {})["workflow"] = custom_workflow
        if additional_data:
            always_merger.merge(json, additional_data)

        return json

    return _merge_record_data


"""
@pytest.fixture
def vocab_cf(app: Flask, db: SQLAlchemy, cache) -> None:
    from oarepo_runtime.services.custom_fields.mappings import prepare_cf_indices

    prepare_cf_indices()
"""


class LoggedClient:
    """Logged client."""

    # TODO: - using the different clients thing?
    def __init__(self, client: FlaskClient, user_fixture: UserFixtureBase):
        """Initialize the logged client."""
        self.client: FlaskClient = client
        self.user_fixture: UserFixtureBase = user_fixture

    def _login(self) -> None:
        login_user(self.user_fixture.user, remember=True)
        login_user_via_session(self.client, email=self.user_fixture.email)

    def post(self, *args: Any, **kwargs: Any) -> TestResponse:
        """Execute POST request."""
        self._login()
        return self.client.post(*args, **kwargs)

    def get(self, *args: Any, **kwargs: Any) -> TestResponse:
        """Execute GET request."""
        self._login()
        return self.client.get(*args, **kwargs)

    def put(self, *args: Any, **kwargs: Any) -> TestResponse:
        """Execute PUT request."""
        self._login()
        return self.client.put(*args, **kwargs)

    def delete(self, *args: Any, **kwargs: Any) -> TestResponse:
        """Execute DELETE request."""
        self._login()
        return self.client.delete(*args, **kwargs)


@pytest.fixture
def logged_client(client: FlaskClient) -> Callable[[UserFixtureBase], LoggedClient]:
    """Return logged client."""

    def _logged_client(user: UserFixtureBase) -> LoggedClient:
        return LoggedClient(client, user)

    return _logged_client
