#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
import pytest
from deepmerge import always_merger
from invenio_access.permissions import system_identity
from invenio_accounts.proxies import current_datastore
from invenio_records_permissions.generators import SystemProcess
from invenio_requests.proxies import current_requests
from invenio_requests.records.api import RequestEventFormat
from invenio_requests.services.generators import Receiver
from oarepo_requests.proxies import current_oarepo_requests_service

can_comment_only_receiver = [
    Receiver(),
    SystemProcess(),
]


@pytest.fixture(scope="module")
def requests_service(app):
    return current_requests.requests_service


@pytest.fixture(scope="module")
def request_events_service(app):
    service = current_requests.request_events_service
    return service


@pytest.fixture(scope="module")
def oarepo_requests_service(app):
    return current_oarepo_requests_service


def _create_role(id, name, description, is_managed, database):
    """Creates a Role/Group."""
    r = current_datastore.create_role(
        id=id, name=name, description=description, is_managed=is_managed
    )
    current_datastore.commit()
    return r


@pytest.fixture()
def role(database):
    """A single group."""
    r = _create_role(
        id="it-dep",
        name="it-dep",
        description="IT Department",
        is_managed=False,
        database=database,
    )
    return r


@pytest.fixture()
def role_ui_serialization(host):
    """
    UI serialization of the example role in role fixture.
    """
    return {
        "label": "it-dep",
        "links": {
            "avatar": f"{host}api/groups/it-dep/avatar.svg",
            "self": f"{host}api/groups/it-dep",
        },
        "reference": {"group": "it-dep"},
        "type": "group",
    }


@pytest.fixture()
def events_resource_data():
    return {
        "payload": {
            "content": "This is an event.",
            "format": RequestEventFormat.HTML.value,
        }
    }


@pytest.fixture()
def request_type_additional_data():
    """
    Fixture for adding required input data default values specific by request type.
    """
    return {"publish_draft": {"payload": {"version": "1.0"}}}


@pytest.fixture()
def create_request(
    request_type_additional_data, record_service, oarepo_requests_service
):
    """
    Base fixture for creating a request.
    """
    def _create_request(
        identity,
        id_,
        request_type,
        topic_read_method,
        additional_data=None,
        expand=False,
        **request_kwargs,
    ):
        """
        Create request of specific type on a specific record.
        :param identity: Identity of the caller.
        :param id_: ID of the topic record.
        :param request_type: ID of the topic record.
        :param topic_read_method: Method the service uses to read the topic.
        :param additional_data: Additional data needed to create the request.
        :param expand: Expand the created request response.
        :param service_kwargs: Additional keyword arguments to pass to request service.
        """
        topic_service = record_service
        if additional_data is None:
            additional_data = {}

        if request_type in request_type_additional_data:
            additional_data = always_merger.merge(
                additional_data, request_type_additional_data[request_type]
            )

        topic = getattr(topic_service, topic_read_method)(system_identity, id_)._obj
        response = oarepo_requests_service.create(
            identity,
            data=additional_data,
            request_type=request_type,
            topic=topic,
            expand=expand,
            **request_kwargs,
        )
        return response

    return _create_request


@pytest.fixture()
def create_request_on_draft(create_request):
    """
    Fixture for creating a request on a draft.
    """
    def _create(
        identity,
        topic_id,
        request_type,
        additional_data=None,
        expand=False,
        **request_kwargs,
    ):
        """
        Create request of specific type on a draft record.
        :param identity: Identity of the caller.
        :param topic_id: ID of the topic record.
        :param request_type: Type of the request.
        :param additional_data: Additional data needed to create the request.
        :param expand: Expand the created request response.
        :param service_kwargs: Additional keyword arguments to pass to request service.
        """
        return create_request(
            identity,
            topic_id,
            request_type,
            topic_read_method="read_draft",
            additional_data=additional_data,
            expand=expand,
            **request_kwargs,
        )

    return _create


@pytest.fixture()
def create_request_on_record(create_request):
    """
    Fixture for creating a request on a published record.
    """
    def _create(
        identity,
        topic_id,
        request_type,
        additional_data=None,
        expand=False,
        **request_kwargs,
    ):
        """
        Create request of specific type on a published record.
        :param identity: Identity of the caller.
        :param topic_id: ID of the topic record.
        :param request_type: Type of the request.
        :param additional_data: Additional data needed to create the request.
        :param expand: Expand the created request response.
        :param service_kwargs: Additional keyword arguments to pass to request service.
        """
        return create_request(
            identity,
            topic_id,
            request_type,
            topic_read_method="read",
            additional_data=additional_data,
            expand=expand,
            **request_kwargs,
        )

    return _create


@pytest.fixture
def submit_request_on_draft(create_request_on_draft, requests_service):
    """
    Fixture for creating and submitting request on a draft in one call.
    """
    def _submit_request(
        identity,
        topic_id,
        request_type,
        create_additional_data=None,
        submit_additional_data=None,
        expand=False,
    ):
        """
        Creates and submits request of specific type on a specific record..
        :param identity: Identity of tha caller.
        :param topic_id: ID of the topic record.
        :param request_type: Type of the request.
        :param create_additional_data: Additional data needed to create the request.
        :param submit_additional_data: Additional data passed to the submit action.
        :param expand: Expand the created request response.
        :param service_kwargs: Additional keyword arguments to pass to request service.
        """
        create_response = create_request_on_draft(
            identity, topic_id, request_type, additional_data=create_additional_data
        )
        submit_response = requests_service.execute_action(
            identity,
            id_=create_response["id"],
            action="submit",
            data=submit_additional_data,
            expand=expand,
        )
        return submit_response

    return _submit_request


@pytest.fixture
def submit_request_on_record(create_request_on_record, requests_service):
    """
    Fixture for creating and submitting request on a published record in one call.
    """
    def _submit_request(
        identity,
        topic_id,
        request_type,
        create_additional_data=None,
        submit_additional_data=None,
        expand=False,
    ):
        """
        Creates and submits request of specific type on a specific record..
        :param client: Client instance.
        :param record: Record on which the request should be created.
        :param request_type: Which type of request should be created.
        :param create_additional_data: Additional data needed to create the request.
        :param submit_additional_data: Additional data passed to the submit action.
        :param expand: Expand the submitted request response.
        """
        create_response = create_request_on_record(
            identity, topic_id, request_type, additional_data=create_additional_data
        )
        submit_response = requests_service.execute_action(
            identity,
            id_=create_response["id"],
            action="submit",
            data=submit_additional_data,
            expand=expand,
        )
        return submit_response

    return _submit_request
