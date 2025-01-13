#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
import copy
import os
from io import BytesIO
from typing import Dict
from invenio_records_resources.references.entity_resolvers import ServiceResultResolver
import pytest
from deepmerge import always_merger
from invenio_accounts.proxies import current_datastore
from invenio_records_permissions.generators import SystemProcess
from invenio_requests.proxies import current_requests
from invenio_requests.records.api import RequestEventFormat
from invenio_requests.services.generators import Receiver

from pytest_oarepo.functions import link2testclient

"""
from oarepo_requests.notifications.builders.publish import PublishDraftRequestAcceptNotificationBuilder, \
    PublishDraftRequestSubmitNotificationBuilder
from invenio_notifications.backends import EmailNotificationBackend
"""

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



@pytest.fixture()
def events_resource_data():
    """Input data for the Request Events Resource (REST body)."""
    return {
        "payload": {
            "content": "This is an event.",
            "format": RequestEventFormat.HTML.value,
        }
    }


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
def role_ui_serialization():
    return {
        "label": "it-dep",
        "links": {
            "avatar": "https://127.0.0.1:5000/api/groups/it-dep/avatar.svg",
            "self": "https://127.0.0.1:5000/api/groups/it-dep",
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
        selected_entry = [entry for entry in request_types_json if entry["type_id"] == request_type]
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
def create_request_by_link(get_request_link, request_type_additional_data):
    def _create_request(
        client, record, request_type, additional_data=None, **request_kwargs
    ):
        if additional_data is None:
            additional_data = {}
        applicable_requests = client.get(
            link2testclient(record.json["links"]["applicable-requests"])
        ).json["hits"]["hits"]
        create_link = link2testclient(
            get_request_link(applicable_requests, request_type)
        )
        if request_type in request_type_additional_data:
            additional_data = always_merger.merge(
                additional_data, request_type_additional_data[request_type]
            )
        if not additional_data:
            create_response = client.post(create_link, **request_kwargs)
        else:
            create_response = client.post(
                create_link, json=additional_data, **request_kwargs
            )
        return create_response

    return _create_request


@pytest.fixture
def submit_request_by_link(create_request_by_link):
    def _submit_request(
        client,
        record,
        request_type,
        create_additional_data=None,
        submit_additional_data=None,
    ):
        create_response = create_request_by_link(
            client, record, request_type, additional_data=create_additional_data
        )
        submit_response = client.post(
            link2testclient(create_response.json["links"]["actions"]["submit"]),
            json=submit_additional_data,
        )
        return submit_response

    return _submit_request