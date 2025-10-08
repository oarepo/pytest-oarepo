#
# Copyright (c) 2025 CESNET z.s.p.o.
#
# This file is a part of pytest-oarepo (see https://github.com/oarepo/pytest_oarepo).
#
# pytest-oarepo is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
"""Fixtures for creating test records."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Protocol

import pytest
from invenio_access.permissions import system_identity

if TYPE_CHECKING:
    from flask_principal import Identity
    from invenio_records_resources.services import RecordService
    from invenio_records_resources.services.records.results import (
        RecordItem,
        RecordList,
    )

class CreateRecordFn(Protocol):
    def __call__(
        self,
        identity: Identity,
        custom_data: dict[str, Any] | None = ...,
        additional_data: dict[str, Any] | None = ...,
        custom_workflow: str | None = ...,
        expand: bool | None = ...,
        **service_kwargs: Any,
    ) -> dict[str, Any]: ...

class CreateRecordWithFilesFn(Protocol):
    def __call__(
        self,
        identity: Identity,
        custom_data: dict[str, Any] | None = ...,
        additional_data: dict[str, Any] | None = ...,
        custom_workflow: str | None = ...,
        expand: bool | None = ...,
        file_name: str = ...,
        custom_file_metadata: dict[str, Any] | None = ...,
        **service_kwargs: Any,
    ) -> dict[str, Any]: ...

@pytest.fixture
def draft_factory(record_service: RecordService, prepare_record_data) -> CreateRecordFn:
    """Call to instance a draft."""

    def draft(
        identity: "Identity",
        custom_data: dict[str, Any] | None = None,
        additional_data: dict[str, Any] | None = None,
        custom_workflow: str | None = None,
        expand: bool | None = None,
        **service_kwargs: Any,
    ) -> dict[str, Any]:
        """Create instance of a draft.

        :param identity: Identity of the caller.
        :param custom_data: If defined, the default record data are overwritten.
        :param additional_data: If defined, the additional data are merged with the default data.
        :param custom_workflow: Define to use custom workflow.
        :param expand: Expand the response.
        :param service_kwargs: Additional keyword arguments to pass to the service.
        """
        # TODO possibly support for more model types?
        # like this perhaps
        # service = record_service(model) if isinstance(record_service, callable) else record_service

        json = prepare_record_data(custom_data, custom_workflow, additional_data)
        draft = record_service.create(identity=identity, data=json, expand=expand, **service_kwargs)
        return draft.to_dict()  # unified interface

    return draft


@pytest.fixture
def record_factory(record_service: "RecordService", draft_factory: CreateRecordFn) -> CreateRecordFn:
    """Call to instance a published record."""

    def record(
        identity: "Identity",
        custom_data: dict[str, Any] | None = None,
        additional_data: dict[str, Any] | None = None,
        custom_workflow: str | None = None,
        expand: bool | None = None,
        **service_kwargs: Any,
    ) -> dict[str, Any]:
        """Create instance of a published record.

        :param identity: Identity of the caller.
        :param custom_data: If defined, the default record data are overwritten.
        :param additional_data: If defined, the additional data are merged with the default data.
        :param custom_workflow: Define to use custom workflow.
        :param expand: Expand the response.
        :param service_kwargs: Additional keyword arguments to pass to the service.
        """
        draft = draft_factory(
            identity,
            custom_data=custom_data,
            additional_data=additional_data,
            custom_workflow=custom_workflow,
            **service_kwargs,
        )
        record = record_service.publish(system_identity, draft["id"], expand=expand)
        return record.to_dict()  # unified interface

    return record


@pytest.fixture
def record_with_files_factory(
    record_service: "RecordService",
    draft_factory: CreateRecordFn,
    default_record_with_workflow_json: dict[str, Any],
    upload_file,
) -> CreateRecordWithFilesFn:
    """Call to instance a published record with a file."""

    def record(
        identity: "Identity",
        custom_data: dict[str, Any] | None = None,
        additional_data: dict[str, Any] | None = None,
        custom_workflow: str | None = None,
        expand: bool | None = None,
        file_name: str = "test.pdf",
        custom_file_metadata: dict[str, Any] | None = None,  # kept for API parity
        **service_kwargs: Any,
    ) -> dict[str, Any]:
        """Create instance of a published record.

        :param identity: Identity of tha caller.
        :param custom_data: If defined, the default record data are overwritten.
        :param additional_data: If defined, the additional data are merged with the default data.
        :param custom_workflow: Define to use custom workflow.
        :param expand: Expand the response.
        :param file_name: Name of the file to upload.
        :param custom_file_metadata: Define to use custom file metadata.
        :param service_kwargs: Additional keyword arguments to pass to the service.
        """
        if "files" in default_record_with_workflow_json and "enabled" in default_record_with_workflow_json["files"]:
            if not additional_data:
                additional_data = {}
            additional_data.setdefault("files", {}).setdefault("enabled", True)
        draft = draft_factory(
            identity,
            custom_data=custom_data,
            additional_data=additional_data,
            custom_workflow=custom_workflow,
            **service_kwargs,
        )
        files_service = record_service._draft_files
        upload_file(identity, draft["id"], files_service)
        record = record_service.publish(
            system_identity,
            draft["id"],
            expand=expand,
        )
        return record.to_dict()

    return record
