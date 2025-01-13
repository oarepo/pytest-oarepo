import pytest
from invenio_access.permissions import system_identity


@pytest.fixture()
def draft_with_community_factory(
    community_records_service, merge_record_data, base_model_schema, urls
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
        json = merge_record_data(
            custom_workflow, additional_data, add_default_workflow=False
        )
        draft = community_records_service.create(
            identity=client.user_fixture.identity,
            data=json,
            community_id=community_id,
            **service_kwargs,
        )
        url = f"{urls['BASE_URL']}{draft['id']}/draft"
        if expand:
            url += "?expand=true"
        return client.get(url)

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
        record_item = record_service.publish(system_identity, draft.json["id"])
        url = f"/thesis/{record_item['id']}"
        if expand:
            url += "?expand=true"
        return client.get(url)

    return _published_record_with_community
