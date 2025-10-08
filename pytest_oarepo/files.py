#
# Copyright (c) 2025 CESNET z.s.p.o.
#
# This file is a part of pytest-oarepo (see https://github.com/oarepo/pytest_oarepo).
#
# pytest-oarepo is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
"""Test fixtures for working with files."""

from __future__ import annotations

from io import BytesIO
from typing import TYPE_CHECKING, Any, Protocol, cast

import pytest

if TYPE_CHECKING:
    from flask_principal import Identity
    from invenio_records_resources.services.files.results import FileItem
    from invenio_records_resources.services.files.service import FileService


class UploadFileFn(Protocol):
    """Callable to upload a file to a record."""

    def __call__(
        self,
        identity: Identity,
        record_id: str,
        files_service: FileService,
        file_name: str = ...,
        custom_file_metadata: dict[str, Any] | None = ...,
    ) -> FileItem:  # type: ignore[reportReturnType]
        """Upload a file to a record."""


@pytest.fixture
def file_metadata() -> dict[str, Any]:
    """Return default file metadata."""
    return {"title": "Test file"}


@pytest.fixture
def upload_file(file_metadata: dict[str, Any]) -> UploadFileFn:
    """Fixture to upload a file to a record."""

    def _upload_file(
        identity: Identity,
        record_id: str,
        files_service: FileService,
        file_name: str = "test.pdf",
        custom_file_metadata: dict[str, Any] | None = None,
    ) -> FileItem:
        """Upload a default file to a record.

        :param identity: Identity of the requester.
        :param record_id: Id of the record to be uploaded on.
        :param files_service: Service to upload the file.
        :param file_name: Name of the file to be uploaded.
        :param custom_file_metadata: Custom metadata to be uploaded.
        """
        actual_file_metadata = custom_file_metadata if custom_file_metadata else file_metadata
        files_service.init_files(
            identity,
            record_id,
            data=[
                {"key": file_name, "metadata": actual_file_metadata},
            ],
        )
        files_service.set_file_content(identity, record_id, file_name, stream=BytesIO(b"testfile"))
        return cast("FileItem", files_service.commit_file(identity, record_id, file_name))

    return _upload_file
