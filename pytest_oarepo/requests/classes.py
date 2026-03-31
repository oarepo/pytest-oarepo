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

from typing import TYPE_CHECKING, Any, override

from invenio_requests.customizations import CommentEventType
from oarepo_runtime.services.generators import Generator
from oarepo_workflows.requests import RecipientGeneratorMixin

if TYPE_CHECKING:
    from collections.abc import Mapping

    from invenio_records_resources.records import Record
    from invenio_requests.customizations import RequestType
    from invenio_search.engine import dsl


class TestEventType(CommentEventType):
    """Custom EventType."""

    type_id = "T"


class TestRecipient(RecipientGeneratorMixin, Generator):
    """Test recipient that always returns user 1."""

    @override
    def reference_receivers(
        self,
        record: Record | None = None,
        request_type: RequestType | None = None,
        **context: Any,
    ) -> list[Mapping[str, str]]:
        return [{"user": "1"}]


class TestRecipient2(RecipientGeneratorMixin, Generator):
    """Test recipient that always returns user 2."""

    @override
    def reference_receivers(
        self,
        record: Record | None = None,
        request_type: RequestType | None = None,
        **context: Any,
    ) -> list[Mapping[str, str]]:
        return [{"user": "2"}]


class FailingGenerator(Generator):
    """Generator that always raises ValueError."""

    @override
    def needs(self, **kwargs: Any) -> list:
        raise ValueError("Failing generator")

    @override
    def excludes(self, **kwargs: Any) -> list:
        raise ValueError("Failing generator")

    @override
    def query_filter(self, **kwargs: Any) -> dsl.query.Query:
        raise ValueError("Failing generator")
