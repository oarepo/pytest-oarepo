#
# Copyright (c) 2025 CESNET z.s.p.o.
#
# This file is a part of pytest-oarepo (see https://github.com/oarepo/pytest_oarepo).
#
# pytest-oarepo is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
"""Fixtures for creating records in communities."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Protocol

import pytest
from invenio_access.permissions import system_identity

if TYPE_CHECKING:
    from flask_principal import Identity
    from invenio_drafts_resources.services import RecordService

    from pytest_oarepo.fixtures import PrepareRecordDataFn


class CreateCommunityRecordFn(Protocol):
    """Callable to create a record in a community."""

    def __call__(  # noqa PLR0913
        self,
        identity: Identity,
        community_id: str,
        model_schema: str | None = ...,
        custom_data: dict[str, Any] | None = ...,
        additional_data: dict[str, Any] | None = ...,
        custom_workflow: str | None = ...,
        expand: bool = ...,
        **service_kwargs: Any,
    ) -> dict[str, Any]:  # type: ignore[reportReturnType]
        """Create a record in a community."""


@pytest.fixture
def draft_with_community_factory(
    record_service: RecordService,
    base_model_schema: str,
    prepare_record_data: PrepareRecordDataFn,
) -> CreateCommunityRecordFn:
    """Call to instance draft in a community."""

    def record(  # noqa PLR0913
        identity: Identity,
        community_id: str,
        model_schema: str | None = None,
        custom_data: dict[str, Any] | None = None,
        additional_data: dict[str, Any] | None = None,
        custom_workflow: str | None = None,
        expand: bool = False,
        **service_kwargs: Any,
    ) -> dict[str, Any]:
        """Create instance of a draft in a community.

        :param identity: Identity of the caller.
        :param community_id: ID of the community.
        :param model_schema: Optional model schema if using different than defined in base_model_schema fixture.
        :param custom_data: If defined, the default record data are overwritten.
        :param additional_data: If defined, the additional data are merged with the default data.
        :param custom_workflow: Define to use custom workflow.
        :param expand: Expand the response.
        :param service_kwargs: Additional keyword arguments to pass to the service.
        """
        additional_data = additional_data if additional_data else {}
        if "$schema" not in additional_data:
            additional_data["$schema"] = model_schema if model_schema else base_model_schema
        json = prepare_record_data(
            custom_data, custom_workflow, additional_data, add_default_workflow=False
        )  # default workflow taken from community
        json.setdefault("parent", {}).setdefault("communities", {})["default"] = community_id
        draft = record_service.create(
            identity=identity,
            data=json,
            expand=expand,
            **service_kwargs,
        )
        return draft.to_dict()  # type: ignore[no-any-return]

    return record


@pytest.fixture
def published_record_with_community_factory(
    record_service: RecordService,
    draft_with_community_factory: CreateCommunityRecordFn,
) -> CreateCommunityRecordFn:
    """Call to instance published record in a community."""

    def _published_record_with_community(  # noqa PLR0913
        identity: Identity,
        community_id: str,
        model_schema: str | None = None,
        custom_data: dict[str, Any] | None = None,
        additional_data: dict[str, Any] | None = None,
        custom_workflow: str | None = None,
        expand: bool = False,
        **service_kwargs: Any,
    ) -> dict[str, Any]:
        """Create instance of a published record in a community.

        :param identity: Identity of the caller.
        :param community_id: ID of the community.
        :param model_schema: Optional model schema if using different than defined in base_model_schema fixture.
        :param custom_data: If defined, the default record data are overwritten.
        :param additional_data: If defined, the additional data are merged with the default data.
        :param custom_workflow: Define to use custom workflow.
        :param expand: Expand the response.
        :param service_kwargs: Additional keyword arguments to pass to the service.
        """
        draft = draft_with_community_factory(
            identity,
            community_id,
            model_schema=model_schema,
            custom_data=custom_data,
            additional_data=additional_data,
            custom_workflow=custom_workflow,
            **service_kwargs,
        )
        record = record_service.publish(system_identity, draft["id"], expand=expand)
        return record.to_dict()  # type: ignore[no-any-return]

    return _published_record_with_community
