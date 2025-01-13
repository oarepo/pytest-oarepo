from collections import defaultdict

# todo - it's kind of ugly to request each time we need things like this but can't be called with autouse
def link2testclient(link, ui=False):
    base_string = "https://127.0.0.1:5000/api/" if not ui else "https://127.0.0.1:5000/"
    return link[len(base_string) - 1 :]


# from chatgpt
def dict_diff(dict1, dict2, path=""):
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
            sub_result = dict_diff(dict1[key], dict2[key], new_path)
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
    diff = dict_diff(subdict, dict_)
    return "different values" not in diff and "second dict missing" not in diff
