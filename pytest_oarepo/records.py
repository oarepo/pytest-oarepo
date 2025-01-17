import copy
from collections import namedtuple
from io import BytesIO

import pytest
from deepmerge import always_merger
from invenio_access.permissions import system_identity


@pytest.fixture()
def draft_factory(record_service, _merge_record_data):
    """
    Call to instance a draft.
    """
    def draft(
        client,
        custom_workflow=None,
        additional_data=None,
        expand=None,
        **service_kwargs,
    ):
        """
        Create instance of a draft.
        :param client: Client instance.
        :param custom_workflow: If user wants to use different workflow that the default one.
        :param additional_data: Additional data beyond the defaults that should be put into the service.
        :param expand: Expand the response.
        """
        json = _merge_record_data(custom_workflow, additional_data)
        draft = record_service.create(
            identity=client.user_fixture.identity, data=json, expand=expand, **service_kwargs
        )
        return draft.to_dict() # unified interface

    return draft


@pytest.fixture()
def record_factory(record_service, draft_factory):
    # bypassing request pattern with system identity
    def record(
        client,
        custom_workflow=None,
        additional_data=None,
        expand=None,
        **service_kwargs):
        """
        Create instance of a draft.
        :param client: Client instance.
        :param custom_workflow: If user wants to use different workflow that the default one.
        :param additional_data: Additional data beyond the defaults that should be put into the service.
        :param expand: Expand the response.
        """
        draft = draft_factory(
            client, additional_data=additional_data, custom_workflow=custom_workflow, expand=expand, **service_kwargs
        )
        record = record_service.publish(system_identity, draft.json["id"])
        return record.to_dict() # unified interface

    return record

"""
@pytest.fixture()
def draft_factory(draft_factory_record_object, urls):
    def _create_draft(
        client,
        *service_args,
        custom_workflow=None,
        additional_data=None,
        expand=True,
        **service_kwargs,
    ):
        draft = draft_factory_record_object(
            client,
            *service_args,
            custom_workflow=custom_workflow,
            additional_data=additional_data,
            **service_kwargs,
        )
        url = f"{urls['BASE_URL']}{draft['id']}/draft" # todo repeated code + it would probably make more sense to use service outputs as defaults - requires rewriting tests in requests and communities
        if expand:
            url += "?expand=true"
        return client.get(url)

    return _create_draft



@pytest.fixture()
def record_factory(
    record_service, draft_factory_record_object, urls, record_factory_record_object
):

    def record(client, custom_workflow=None, additional_data=None, expand=True):
        record = record_factory_record_object(client, custom_workflow, additional_data)
        url = f"{urls['BASE_URL']}{record['id']}"
        if expand:
            url += "?expand=true"
        return client.get(url)

    return record
"""


@pytest.fixture()
def upload_file():
    def _upload_file(identity, record_id, files_service):
        """
        Uploads a default file to a record.
        :param identity: Identity of the requester.
        :param record_id: Id of the record to be uploaded on.
        """
        init = files_service.init_files(
            identity,
            record_id,
            data=[
                {"key": "test.pdf", "metadata": {"title": "Test file"}},
            ],
        )
        upload = files_service.set_file_content(
            identity, record_id, "test.pdf", stream=BytesIO(b"testfile")
        )
        commit = files_service.commit_file(identity, record_id, "test.pdf")
        return commit

    return _upload_file


@pytest.fixture()
def record_with_files_factory(
    record_service,
    upload_file,
    draft_factory,
    default_record_with_workflow_json,
    urls,
):
    def record(client, custom_workflow=None, additional_data=None, expand=None):
        """
        Create instance of a published record with the default file.
        :param client: Client instance.
        :param custom_workflow: If user wants to use different workflow that the default one.
        :param additional_data: Additional data beyond the defaults that should be put into the service.
        :param expand: Expand the response.
        """
        identity = client.user_fixture.identity
        if (
            "files" in default_record_with_workflow_json
            and "enabled" in default_record_with_workflow_json["files"]
        ):
            if not additional_data:
                additional_data = {}
            additional_data.setdefault("files", {}).setdefault("enabled", True)
        draft = draft_factory(
            client, custom_workflow=custom_workflow, additional_data=additional_data
        )
        files_service = record_service._draft_files
        upload_file(identity, draft["id"], files_service)
        record = record_service.publish(system_identity, draft["id"], expand=expand)
        return record.to_dict()

    return record
