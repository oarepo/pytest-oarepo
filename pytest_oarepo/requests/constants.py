from invenio_requests.records.api import RequestEventFormat

EVENTS_RESOURCE_DATA = {
        "payload": {
            "content": "This is an event.",
            "format": RequestEventFormat.HTML.value,
        }
    }