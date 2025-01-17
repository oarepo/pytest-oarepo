import copy
from collections import defaultdict
from deepmerge import always_merger

from pytest_oarepo.constants import DEFAULT_RECORD_JSON


def link2testclient(link, ui=False, host="https://127.0.0.1:5000/"):
    base_string = f"{host}api/" if not ui else host
    return link[len(base_string) - 1 :]


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

def _merge_record_data(
    custom_workflow=None, additional_data=None, add_default_workflow=True
):
    """
    :param custom_workflow: If user wants to use different workflow that the default one.
    :param additional_data: Additional data beyond the defaults that should be put into the service.
    :param add_default_workflow: Allows user to to pass data into the service without workflow - this might be useful for example
    in case of wanting to use community default workflow.
    """
    json = copy.deepcopy(DEFAULT_RECORD_JSON)
    if add_default_workflow:
        always_merger.merge(json, {"parent": {"workflow": "default"}})
    if custom_workflow:  # specifying this assumes use of workflows
        json.setdefault("parent", {})["workflow"] = custom_workflow
    if additional_data:
        always_merger.merge(json, additional_data)

    return json


