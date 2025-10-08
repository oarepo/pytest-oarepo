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
    from invenio_drafts_resources.services import RecordService

    from pytest_oarepo.files import UploadFileFn
    from pytest_oarepo.fixtures import PrepareRecordDataFn


class CreateRecordFn(Protocol):
    """Callable to create a record."""

    def __call__(
        self,
        identity: Identity,
        custom_data: dict[str, Any] | None = ...,
        additional_data: dict[str, Any] | None = ...,
        custom_workflow: str | None = ...,
        expand: bool = ...,
        **service_kwargs: Any,
    ) -> dict[str, Any]:  # type: ignore[reportReturnType]
        """Create instance of a record."""


class CreateRecordWithFilesFn(Protocol):
    """Callable to create a record with a file."""

    def __call__(  # noqa PLR0913
        self,
        identity: Identity,
        custom_data: dict[str, Any] | None = ...,
        additional_data: dict[str, Any] | None = ...,
        custom_workflow: str | None = ...,
        expand: bool = ...,
        file_name: str = ...,
        custom_file_metadata: dict[str, Any] | None = ...,
        **service_kwargs: Any,
    ) -> dict[str, Any]:  # type: ignore[reportReturnType]
        """Create instance of a record with a file."""


@pytest.fixture
def draft_factory(record_service: RecordService, prepare_record_data: PrepareRecordDataFn) -> CreateRecordFn:
    """Call to instance a draft."""

    def draft(
        identity: Identity,
        custom_data: dict[str, Any] | None = None,
        additional_data: dict[str, Any] | None = None,
        custom_workflow: str | None = None,
        expand: bool = False,
        **service_kwargs: Any,
    ) -> dict[str, Any]:  # type: ignore[reportReturnType]
        """Create instance of a draft.

        :param identity: Identity of the caller.
        :param custom_data: If defined, the default record data are overwritten.
        :param additional_data: If defined, the additional data are merged with the default data.
        :param custom_workflow: Define to use custom workflow.
        :param expand: Expand the response.
        :param service_kwargs: Additional keyword arguments to pass to the service.
        """
        # TODO: possibly support for more model types?
        # like this perhaps
        # ruff ok service = record_service(model) if isinstance(record_service, callable) else record_service

        json = prepare_record_data(custom_data, custom_workflow, additional_data)
        draft = record_service.create(identity=identity, data=json, expand=expand, **service_kwargs)
        # TODO: to_dict() is typed as dict[str, Any] in RecordItem, idk why it complains here
        # unified interface
        return draft.to_dict()  # type: ignore[no-any-return]

    return draft


@pytest.fixture
def record_factory(record_service: RecordService, draft_factory: CreateRecordFn) -> CreateRecordFn:
    """Call to instance a published record."""

    def record(
        identity: Identity,
        custom_data: dict[str, Any] | None = None,
        additional_data: dict[str, Any] | None = None,
        custom_workflow: str | None = None,
        expand: bool = False,
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
        return record.to_dict()  # type: ignore[no-any-return]

    return record


@pytest.fixture
def record_with_files_factory(
    record_service: RecordService,
    draft_factory: CreateRecordFn,
    default_record_with_workflow_json: dict[str, Any],
    upload_file: UploadFileFn,
) -> CreateRecordWithFilesFn:
    """Call to instance a published record with a file."""

    def record(  # noqa PLR0913
        identity: Identity,
        custom_data: dict[str, Any] | None = None,
        additional_data: dict[str, Any] | None = None,
        custom_workflow: str | None = None,
        expand: bool = False,
        # kept for API parity
        file_name: str = "test.pdf",  # noqa ARG001
        custom_file_metadata: dict[str, Any] | None = None,  # noqa ARG001
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
        # _draft_files is not typed
        files_service = record_service._draft_files  # type: ignore[reportAttributeAccessIssue]  # noqa: SLF001
        upload_file(identity, draft["id"], files_service)
        record = record_service.publish(
            system_identity,
            draft["id"],
            expand=expand,
        )
        return record.to_dict()  # type: ignore[no-any-return]

    return record
