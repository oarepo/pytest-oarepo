from collections import defaultdict

from invenio_users_resources.proxies import current_users_service
from flask import g

# from chatgpt
def _dict_diff(dict1, dict2, path=""):
    ret = defaultdict(list)
    for key in dict1:
        # Construct path to current element
        if path == "":
            new_path = key
        else:
            new_path = f"{path}.{key}"

        # Check if the key is in the second dictionary
        if key not in dict2:
            ret["second dict missing"].append(
                f"{new_path}: Key missing in the second dictionary"
            )
            continue

        # If both values are dictionaries, do a recursive call
        if isinstance(dict1[key], dict) and isinstance(dict2[key], dict):
            sub_result = _dict_diff(dict1[key], dict2[key], new_path)
            ret.update(sub_result)
        # Check if values are the same
        elif dict1[key] != dict2[key]:
            ret["different values"].append(f"{new_path}: {dict1[key]} != {dict2[key]}")

    # Check for keys in the second dictionary but not in the first
    for key in dict2:
        if key not in dict1:
            if path == "":
                new_path = key
            else:
                new_path = f"{path}.{key}"
            ret["first dict missing"].append(
                f"{new_path}: Key missing in the first dictionary"
            )
    return ret


def is_valid_subdict(subdict, dict_):
    diff = _dict_diff(subdict, dict_)
    return "different values" not in diff and "second dict missing" not in diff


def _index_users():
    current_users_service.indexer.process_bulk_queue()
    current_users_service.indexer.refresh()

def clear_babel_context():
    # for invenio 12
    try:
        from flask_babel import SimpleNamespace
    except ImportError:
        return
    g._flask_babel = SimpleNamespace()
