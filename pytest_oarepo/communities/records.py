# SPDX-FileCopyrightText: 2025 CESNET z.s.p.o
# SPDX-License-Identifier: MIT

"""Fixtures for creating records in communities."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Protocol

import pytest
from invenio_access.permissions import system_identity
from invenio_rdm_records.proxies import current_rdm_records_service
from invenio_requests.proxies import current_requests_service

if TYPE_CHECKING:
    from flask_principal import Identity
    from invenio_rdm_records.services import RDMRecordService

    from pytest_oarepo.files import UploadFileFn
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


class SubmitReviewFn(Protocol):
    """Callable to submit the review of a draft."""

    def __call__(self, identity: Identity, draft_id: str) -> dict[str, Any]:
        """Submit the review of a draft."""


@pytest.fixture
def submit_review() -> SubmitReviewFn:
    """Call to submit the review of a draft."""

    def _submit_review(identity: Identity, draft_id: str) -> dict[str, Any]:
        return current_rdm_records_service.review.submit(identity, draft_id).to_dict()

    return _submit_review


@pytest.fixture
def draft_with_community_submission_factory(
    record_service: RDMRecordService,
    base_model_schema: str,
    prepare_record_data: PrepareRecordDataFn,
    upload_file: UploadFileFn,
) -> CreateCommunityRecordFn:
    """Override pytest-oarepo's factory: a draft with a not yet submitted community-submission review.

    As in the Invenio review process, the draft is not in the community until the review is accepted.
    """

    def _create(
        identity: Identity,
        community_id: str,
        model_schema: str | None = None,
        custom_data: dict[str, Any] | None = None,
        additional_data: dict[str, Any] | None = None,
        custom_workflow: str | None = None,
        expand: bool = False,
        **service_kwargs: Any,
    ) -> dict[str, Any]:
        additional_data = {"$schema": model_schema or base_model_schema, **(additional_data or {})}
        data = prepare_record_data(custom_data, custom_workflow, additional_data, add_default_workflow=False)
        draft = record_service.create(identity=identity, data=data, **service_kwargs)
        # files.enabled=False is applied only for identities that can manage files, the others must upload
        # a file, otherwise accepting the review fails
        if draft.data["files"]["enabled"]:
            upload_file(identity=identity, record_id=draft.id, files_service=record_service.draft_files)
        record_service.review.update(
            identity, draft.id, {"receiver": {"community": community_id}, "type": "community-submission"}
        )
        return record_service.read_draft(identity, draft.id, expand=expand).to_dict()

    return _create


@pytest.fixture
def published_record_with_community_factory(
    record_service: RDMRecordService,
    draft_with_community_submission_factory: CreateCommunityRecordFn,
    submit_review: SubmitReviewFn,
) -> CreateCommunityRecordFn:
    """A record published by accepting its community-submission review."""

    def _create(
        identity: Identity,
        community_id: str,
        model_schema: str | None = None,
        custom_data: dict[str, Any] | None = None,
        additional_data: dict[str, Any] | None = None,
        custom_workflow: str | None = None,
        expand: bool = False,
        **service_kwargs: Any,
    ) -> dict[str, Any]:
        draft = draft_with_community_submission_factory(
            identity,
            community_id,
            model_schema=model_schema,
            custom_data=custom_data,
            additional_data=additional_data,
            custom_workflow=custom_workflow,
            **service_kwargs,
        )
        review = submit_review(identity, draft["id"])
        # submissions of community curators are accepted directly on submit
        if review["status"] != "accepted":
            current_requests_service.execute_action(system_identity, review["id"], "accept", send_notification=False)
        return record_service.read(identity, draft["id"], expand=expand).to_dict()

    return _create
