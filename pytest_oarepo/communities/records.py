import pytest
from invenio_access.permissions import system_identity
from pytest_oarepo.functions import _merge_record_data


@pytest.fixture()
def draft_with_community_factory(
    community_records_service, base_model_schema, urls
):
    def record(
        client,
        community_id,
        custom_workflow=None,
        additional_data=None,
        model_schema=None,
        expand=None,
        **service_kwargs,
    ):
        additional_data = {} if not additional_data else additional_data
        if "$schema" not in additional_data:
            additional_data["$schema"] = (
                base_model_schema if not model_schema else model_schema
            )
        json = _merge_record_data(
            custom_workflow, additional_data, add_default_workflow=False
        )
        draft = community_records_service.create(
            identity=client.user_fixture.identity,
            data=json,
            community_id=community_id,
            **service_kwargs,
        )
        return draft.to_dict()

    return record


@pytest.fixture
def published_record_with_community_factory(
    record_service, draft_with_community_factory
):
    # skip the request approval
    def _published_record_with_community(
        client, community_id, custom_workflow=None, additional_data=None, expand=None
    ):
        draft = draft_with_community_factory(
            client,
            community_id,
            custom_workflow=custom_workflow,
            additional_data=additional_data,
        )
        record = record_service.publish(system_identity, draft["id"], expand=expand)
        return record.to_dict()

    return _published_record_with_community
