import pytest
from invenio_access.permissions import system_identity

@pytest.fixture()
def draft_with_community_factory(community_records_service, base_model_schema, prepare_record_data):
    """
    Call to instance draft in a community.
    """
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
        """
        Create instance of a draft in a community.
        :param identity: Identity of the caller.
        :param community_id: ID of the community.
        :param model_schema: Optional model schema if using different than defined in base_model_schema fixture.
        :param custom_data: If defined, the default record data are overwritten.
        :param additional_data: If defined, the additional data are merged with the default data.
        :param custom_workflow: Define to use custom workflow.
        :param expand: Expand the response.
        :param service_kwargs: Additional keyword arguments to pass to the service.
        """
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
    """
    Call to instance published record in a community.
    """
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
        """
        Create instance of a published record in a community.
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
        return record.to_dict()

    return _published_record_with_community
