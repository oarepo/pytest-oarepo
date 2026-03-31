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
import re
from typing import TYPE_CHECKING, Any, Protocol, cast
from urllib import parse

import pytest
from deepmerge import always_merger
from flask_principal import Identity, Need, UserNeed
from flask_security import login_user
from invenio_accounts.testutils import login_user_via_session
from invenio_app.factory import create_api

if TYPE_CHECKING:
    from collections.abc import Callable, Generator

    from flask import Flask
    from flask.testing import FlaskClient
    from pytest_invenio.user import UserFixtureBase
    from werkzeug.test import TestResponse

pytest_plugins = [
    "pytest_oarepo.users",
]


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
def default_record_with_workflow_json(
    default_record_json: dict[str, Any],
) -> dict[str, Any]:
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
        record_json = custom_data or default_record_json
        json = copy.deepcopy(record_json)
        if add_default_workflow:
            always_merger.merge(json, {"parent": {"workflow": "default"}})
        if custom_workflow:  # specifying this assumes use of workflows
            json.setdefault("parent", {})["workflow"] = custom_workflow
        if additional_data:
            always_merger.merge(json, additional_data)

        return json

    return _merge_record_data


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


@pytest.fixture
def identity_simple(users: list[UserFixtureBase]) -> Identity:
    """Provide simple identity fixture."""
    user = users[0]
    i = Identity(user.id)
    i.provides.add(UserNeed(user.id))
    i.provides.add(Need(method="system_role", value="any_user"))
    i.provides.add(Need(method="system_role", value="authenticated_user"))
    return i


@pytest.fixture(scope="module")
def app_config(app_config: dict[str, Any]) -> dict[str, Any]:
    """Set common boilerplate app config defaults used across OARepo test suites."""
    app_config["JSONSCHEMAS_HOST"] = "localhost"
    app_config["RECORDS_REFRESOLVER_CLS"] = "invenio_records.resolver.InvenioRefResolver"
    app_config["RECORDS_REFRESOLVER_STORE"] = "invenio_jsonschemas.proxies.current_refresolver_store"
    app_config["RATELIMIT_AUTHENTICATED_USER"] = "200 per second"
    app_config["CACHE_TYPE"] = "SimpleCache"
    app_config["CACHE_DEFAULT_TIMEOUT"] = 300
    app_config["FILES_REST_STORAGE_CLASS_LIST"] = {
        "L": "Local",
        "F": "Fetch",
        "R": "Remote",
    }
    app_config["FILES_REST_DEFAULT_STORAGE_CLASS"] = "L"
    return app_config


@pytest.fixture(scope="session")
def model_types() -> dict[str, Any]:
    """Return common model type definitions for test record models."""
    return {
        "Metadata": {
            "properties": {
                "title": {"type": "fulltext+keyword", "required": True},
                "creators": {
                    "type": "array",
                    "items": {"type": "keyword"},
                },
                "contributors": {
                    "type": "array",
                    "items": {"type": "keyword"},
                },
            }
        }
    }


class URLNormalizer[T](Protocol):
    """URL normalizer protocol."""

    def __call__(
        self,
        data: T,
        *,
        remove_api_prefix: bool = True,
        replacements: dict[str, str] | None = None,
    ) -> T:
        """Normalize the URL."""
        ...


@pytest.fixture
def normalize_urls[T]() -> URLNormalizer[T]:  # noqa C901
    """Normalize URLs in the data structure, optionally removing the `/api/` prefix.

    Normalization:
        1. Remove protocol, server and port from the URL.
        2. Optionally remove the `/api/` prefix from the path.
        3. For query parameters, sort by parameter name
        4. Optionally replace string values in the URL from the replacements table.
        Key is a regex pattern, value is the replacement string.
    """

    def _replace_in_string(
        s: str,
        remove_api_prefix: bool = True,
        replacements: dict[str, str] | None = None,
    ) -> str:
        if s.startswith("http://"):
            s = s[7:]
        elif s.startswith("https://"):
            s = s[8:]
        else:
            return s

        if replacements is not None:
            for k, v in replacements.items():
                s = re.sub(k, v, s)

        url_parts = parse.urlparse(s)
        path = url_parts.path
        query = url_parts.query

        if remove_api_prefix and path.startswith("/api"):
            path = path[4:]

        if query:
            query_list = sorted(parse.parse_qsl(query))
            query = "&".join(f"{k}={v}" for k, v in query_list)
            s = f"{parse.quote(path)}?{parse.quote(query)}"

        return s

    def _normalize_urls(
        d: Any,
        *,
        remove_api_prefix: bool = True,
        replacements: dict[str, str] | None = None,
    ) -> Any:

        if isinstance(d, dict):
            for k, v in list(d.items()):
                d[k] = _normalize_urls(v, remove_api_prefix=remove_api_prefix, replacements=replacements)
        elif isinstance(d, list):
            for idx, v in enumerate(d):
                d[idx] = _normalize_urls(v, remove_api_prefix=remove_api_prefix, replacements=replacements)
        elif isinstance(d, str):
            return _replace_in_string(d, remove_api_prefix=remove_api_prefix, replacements=replacements)
        return d

    return cast("URLNormalizer[T]", _normalize_urls)
