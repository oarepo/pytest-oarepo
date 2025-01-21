def get_request_type(request_types_json, request_type):
    selected_entry = [
        entry for entry in request_types_json if entry["type_id"] == request_type
    ]
    if not selected_entry:
        return None
    return selected_entry[0]


def create_request_from_link(request_types_json, request_type):
    selected_entry = get_request_type(request_types_json, request_type)
    return selected_entry["links"]["actions"]["create"]
