import pytest
from invenio_access.permissions import system_identity


@pytest.fixture()
def draft_factory(record_service, prepare_record_data):
    """
    Call to instance a draft.
    """

    def draft(
        identity,
        custom_data=None,
        additional_data=None,
        custom_workflow=None,
        expand=None,
        **service_kwargs,
    ):
        """
        Create instance of a draft.
        :param identity: Identity of the caller.
        :param custom_data: If defined, the default record data are overwritten.
        :param additional_data: If defined, the additional data are merged with the default data.
        :param custom_workflow: Define to use custom workflow.
        :param expand: Expand the response.
        :param service_kwargs: Additional keyword arguments to pass to the service.
        """
        # todo possibly support for more model types?
        # like this perhaps
        # service = record_service(model) if isinstance(record_service, callable) else record_service

        json = prepare_record_data(custom_data, custom_workflow, additional_data)
        draft = record_service.create(
            identity=identity, data=json, expand=expand, **service_kwargs
        )
        return draft.to_dict()  # unified interface

    return draft


@pytest.fixture()
def record_factory(record_service, draft_factory):
    """
    Call to instance a published record.
    """

    def record(
        identity,
        custom_data=None,
        additional_data=None,
        custom_workflow=None,
        expand=None,
        **service_kwargs,
    ):
        """
        Create instance of a published record.
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
        record = record_service.publish(
            system_identity, draft["id"], expand=expand
        )
        return record.to_dict()  # unified interface

    return record


@pytest.fixture()
def record_with_files_factory(
    record_service, draft_factory, default_record_with_workflow_json, upload_file
):
    """
    Call to instance a published record with a file.
    """
    def record(
        identity,
        custom_data=None,
        additional_data=None,
        custom_workflow=None,
        expand=None,
        file_name="test.pdf",
        custom_file_metadata=None,
        **service_kwargs,
    ):
        """
        Create instance of a published record.
        :param identity: Identity of tha caller.
        :param custom_data: If defined, the default record data are overwritten.
        :param additional_data: If defined, the additional data are merged with the default data.
        :param custom_workflow: Define to use custom workflow.
        :param expand: Expand the response.
        :param file_name: Name of the file to upload.
        :param custom_file_metadata: Define to use custom file metadata.
        :param service_kwargs: Additional keyword arguments to pass to the service.
        """

        if (
            "files" in default_record_with_workflow_json
            and "enabled" in default_record_with_workflow_json["files"]
        ):
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
            file_name=file_name,
            custom_file_metadata=custom_file_metadata,
        )
        return record.to_dict()

    return record
