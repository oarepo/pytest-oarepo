import pytest
from invenio_access.permissions import system_identity

@pytest.fixture()
def draft_with_community_factory(community_records_service, base_model_schema, prepare_record_data):
    def record(
        identity,
        community_id,
        model_schema=None,
        custom_data=None,
        additional_data=None,
        custom_workflow=None,
        expand=None,
        **service_kwargs,
    ):
        additional_data = {} if not additional_data else additional_data
        if "$schema" not in additional_data:
            additional_data["$schema"] = (
                base_model_schema if not model_schema else model_schema
            )
        json = prepare_record_data(custom_data, custom_workflow, additional_data, add_default_workflow=False)
        draft = community_records_service.create(
            identity=identity,
            data=json,
            community_id=community_id,
            expand=expand,
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
            identity,
            community_id,
            model_schema=None,
            custom_data=None,
            additional_data=None,
            custom_workflow=None,
            expand=None,
            **service_kwargs,
    ):
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
        return record.to_dict()

    return _published_record_with_community
