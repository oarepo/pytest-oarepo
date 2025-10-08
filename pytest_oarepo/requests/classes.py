#
# Copyright (c) 2025 CESNET z.s.p.o.
#
# This file is a part of pytest-oarepo (see https://github.com/oarepo/pytest_oarepo).
#
# pytest-oarepo is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
"""Test classes for requests."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast, override

from flask_principal import UserNeed
from invenio_accounts.models import User
from invenio_requests.customizations import CommentEventType
from oarepo_runtime.services.generators import Generator
from oarepo_workflows.requests.generators import RecipientGeneratorMixin

if TYPE_CHECKING:
    from collections.abc import Collection, Mapping

    from flask_principal import Need
    from invenio_records_resources.records import Record
    from invenio_requests.customizations import RequestType


class TestEventType(CommentEventType):
    """Custom EventType."""

    type_id = "T"


class SystemUserGenerator(RecipientGeneratorMixin, Generator):
    """Generator primarily used to define system user as recipient of a request."""

    @override
    def needs(self, **kwargs: Any) -> Collection[Need]:
        return [UserNeed("system")]

    @override
    def reference_receivers(
        self,
        record: Record | None = None,
        request_type: RequestType | None = None,
        **context: Any,
    ) -> list[Mapping[str, str]]:
        return [{"user": "system"}]


class UserGenerator(RecipientGeneratorMixin, Generator):
    """Generator primarily used to define specific user as recipient of a request."""

    @override
    def __init__(self, user_email: str) -> None:
        self.user_email = user_email

    @property
    def _user_id(self) -> int:
        # id is Integer column
        return cast("int", User.query.filter_by(email=self.user_email).one().id)

    @override
    def needs(self, **kwargs: Any) -> Collection[Need]:
        return [UserNeed(self._user_id)]

    @override
    def reference_receivers(
        self,
        record: Record | None = None,
        request_type: RequestType | None = None,
        **context: Any,
    ) -> list[Mapping[str, str]]:
        return [{"user": str(self._user_id)}]


class CSLocaleUserGenerator(RecipientGeneratorMixin, Generator):
    """Generator primarily used to define specific user as recipient of a request."""

    @property
    def _user_id(self) -> int:
        users = User.query.all()
        users = [user for user in users if "locale" in user.preferences and user.preferences["locale"] == "cs"]
        if users:
            return cast("int", users[0].id)
        raise ValueError("No CS locale user found")

    @override
    def needs(self, **kwargs: Any) -> Collection[Need]:
        return [UserNeed(self._user_id)]

    @override
    def reference_receivers(
        self,
        record: Record | None = None,
        request_type: RequestType | None = None,
        **context: Any,
    ) -> list[Mapping[str, str]]:
        return [{"user": str(self._user_id)}]
