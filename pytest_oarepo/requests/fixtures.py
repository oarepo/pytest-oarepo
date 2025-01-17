#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
import pytest
from deepmerge import always_merger
from invenio_accounts.proxies import current_datastore
from invenio_records_permissions.generators import SystemProcess
from invenio_requests.proxies import current_requests
from invenio_requests.services.generators import Receiver
from invenio_access.permissions import system_identity
from invenio_requests.proxies import current_requests

from pytest_oarepo.functions import link2testclient

"""
from oarepo_requests.notifications.builders.publish import PublishDraftRequestAcceptNotificationBuilder, \
    PublishDraftRequestSubmitNotificationBuilder
from invenio_notifications.backends import EmailNotificationBackend
"""
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
def get_request_type():
    """
    gets request create link from serialized request types
    """

    def _get_request_type(request_types_json, request_type):
        selected_entry = [
            entry for entry in request_types_json if entry["type_id"] == request_type
        ]
        if not selected_entry:
            return None
        return selected_entry[0]

    return _get_request_type


@pytest.fixture()
def get_request_link(get_request_type):
    """
    gets request create link from serialized request types
    """

    def _create_request_from_link(request_types_json, request_type):
        selected_entry = get_request_type(request_types_json, request_type)
        return selected_entry["links"]["actions"]["create"]

    return _create_request_from_link

@pytest.fixture()
def request_type_additional_data():
    return {"publish_draft": {"payload": {"version": "1.0"}}}

@pytest.fixture
def create_request(get_request_link, request_type_additional_data, record_service, oarepo_requests_service):
    def _create_request(
        client, record_id, request_type, additional_data=None, expand=False, **request_kwargs
    ):
        """
        Create request of specific type on a specific record..
        :param client: Client instance.
        :param record: Record on which the request should be created.
        :param request_type: Which type of request should be created.
        :param additional_data: Additional data needed to create the request.
        :param expand: Expand the created request response.
        """
        if additional_data is None:
            additional_data = {}
        """
        applicable_requests = client.get(
            link2testclient(record.json["links"]["applicable-requests"])
        ).json["hits"]["hits"]
        create_link = link2testclient(
            get_request_link(applicable_requests, request_type)
        )
        """
        if request_type in request_type_additional_data:
            additional_data = always_merger.merge(
                additional_data, request_type_additional_data[request_type]
            )
        """
        if not additional_data:
            create_response = client.post(create_link, **request_kwargs)
        else:
            create_response = client.post(
                create_link, json=additional_data, **request_kwargs
            )
        """
        try:
            record = record_service.read(system_identity, record_id)._obj #or direct db query
        except:
            record = record_service.read_draft(system_identity, record_id)._obj
        response = oarepo_requests_service.create(client.user_fixture.identity, data=additional_data,
                                                          request_type=request_type, topic=record, expand=expand, **request_kwargs)
        return response

    return _create_request


@pytest.fixture
def submit_request(create_request, requests_service):
    def _submit_request(
        client,
        record_id,
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
        create_response = create_request(
            client, record_id, request_type, additional_data=create_additional_data
        )
        """
        submit_response = client.post(
            link2testclient(create_response.json["links"]["actions"]["submit"]),
            json=submit_additional_data,
        )
        """
        submit_response = requests_service.execute_action(client.user_fixture.identity,
                                                                                   id_=create_response["id"],
                                                                           action="submit",
                                                                           expand=expand)
        return submit_response

    return _submit_request
