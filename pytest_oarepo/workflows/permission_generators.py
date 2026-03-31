#
# Copyright (c) 2026 CESNET z.s.p.o.
#
# This file is a part of pytest-oarepo (see https://github.com/oarepo/pytest_oarepo).
#
# pytest-oarepo is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
"""Test permission generators."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast, override

from flask_principal import Need, UserNeed
from invenio_accounts.models import User
from oarepo_workflows.requests import RecipientGeneratorMixin

from pytest_oarepo.permission_generators import (
    CSLocaleUserGenerator as CSLocaleUserGeneratorWithoutRecipients,
)
from pytest_oarepo.permission_generators import (
    SystemUserGenerator as SystemUserGeneratorWithoutRecipients,
)
from pytest_oarepo.permission_generators import (
    UserGenerator as UserGeneratorWithoutRecipients,
)

if TYPE_CHECKING:
    from collections.abc import Collection, Mapping

    from invenio_records_resources.records import Record
    from invenio_requests.customizations import RequestType


class SystemUserGenerator(RecipientGeneratorMixin, SystemUserGeneratorWithoutRecipients):
    """Generator primarily used to define system user as recipient of a request."""

    @override
    def reference_receivers(
        self,
        record: Record | None = None,
        request_type: RequestType | None = None,
        **context: Any,
    ) -> list[Mapping[str, str]]:
        return [{"user": "system"}]


class UserGenerator(RecipientGeneratorMixin, UserGeneratorWithoutRecipients):
    """Generator primarily used to define specific user as recipient of a request."""

    @override
    def reference_receivers(
        self,
        record: Record | None = None,
        request_type: RequestType | None = None,
        **context: Any,
    ) -> list[Mapping[str, str]]:
        return [{"user": str(self._user_id)}]


class CSLocaleUserGenerator(RecipientGeneratorMixin, CSLocaleUserGeneratorWithoutRecipients):
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
