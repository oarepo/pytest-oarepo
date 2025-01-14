import copy
from io import BytesIO

import pytest
from deepmerge import always_merger
from invenio_access.permissions import system_identity


@pytest.fixture()
def default_record_with_workflow_json():
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


@pytest.fixture()
def default_record_with_workflow_parent_json():
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
        "parent": {"workflow": "default"},
    }


@pytest.fixture()
def merge_record_data(default_record_with_workflow_json):
    def _merge_data(
        custom_workflow=None, additional_data=None, add_default_workflow=True
    ):
        json = copy.deepcopy(default_record_with_workflow_json)
        if add_default_workflow:
            always_merger.merge(json, {"parent": {"workflow": "default"}})
        if custom_workflow:  # specifying this assumes use of workflows
            json.setdefault("parent", {})["workflow"] = custom_workflow
        if additional_data:
            always_merger.merge(json, additional_data)

        return json

    return _merge_data


@pytest.fixture()
def draft_factory_record_object(record_service, merge_record_data):
    def record(
        client,
        *service_args,
        custom_workflow=None,
        additional_data=None,
        **service_kwargs,
    ):
        json = merge_record_data(custom_workflow, additional_data)
        draft = record_service.create(
            client.user_fixture.identity, json, *service_args, **service_kwargs
        )
        return draft._obj

    return record


@pytest.fixture()
def record_factory_record_object(record_service, draft_factory_record_object, urls):
    # bypassing request pattern with system identity
    def record(client, custom_workflow=None, additional_data=None):
        draft = draft_factory_record_object(
            client, custom_workflow=custom_workflow, additional_data=additional_data
        )
        return record_service.publish(system_identity, draft["id"])._obj

    return record


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


@pytest.fixture()
def upload_file():
    def _upload_file(files_service, identity, record_id):
        # upload file
        # Initialize files upload
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
    draft_factory_record_object,
    default_record_with_workflow_json,
    urls,
):
    def record(client, custom_workflow=None, additional_data=None):
        identity = client.user_fixture.identity
        if (
            "files" in default_record_with_workflow_json
            and "enabled" in default_record_with_workflow_json["files"]
        ):
            if not additional_data:
                additional_data = {}
            additional_data.setdefault("files", {}).setdefault("enabled", True)
        draft = draft_factory_record_object(
            client, custom_workflow=custom_workflow, additional_data=additional_data
        )

        files_service = record_service._draft_files
        upload_file(files_service, identity, draft["id"])
        # publish record
        record = record_service.publish(system_identity, draft["id"])
        ret = client.get(f"{urls['BASE_URL']}{record['id']}")  # unified return value
        return ret

    return record
