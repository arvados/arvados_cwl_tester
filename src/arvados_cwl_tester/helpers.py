import contextlib
from functools import lru_cache
from typing import Dict

import yaml
import os
import json
import tempfile

from arvados_cwl_tester.client import ArvadosClient


class Colors:
    TESTING_INFO = "\033[95m"
    OKBLUE = "\033[94m"
    RUNNING = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    ERROR = "\033[91m"
    BOLD = "\033[1m"


def load_json(path) -> dict:
    with open(path, "r") as f:
        data = json.load(f)
    return data


def load_file(path: str) -> list:
    with open(path, "r") as file:
        lines = file.readlines()
    return lines


def get_cwl_name_from_path(cwl_path):
    pathname = os.path.splitext(cwl_path)[0]
    return os.path.basename(pathname)


def pwd(path_to_file):
    return os.path.dirname(os.path.abspath(path_to_file))


def change_path_in_values(item_dict: dict) -> dict:
    result = item_dict.copy()
    if "path" in item_dict:
        if not item_dict["path"].startswith("keep:"):
            result["path"] = os.path.abspath(result["path"])
    return result


def change_local_paths_to_abs(inputs_dictionary: dict = None) -> dict:
    result = inputs_dictionary.copy()
    if inputs_dictionary:
        for key, values in inputs_dictionary.items():
            if isinstance(values, dict):
                result[key] = change_path_in_values(result[key])
            elif isinstance(values, list):
                items = []
                for item in range(0, len(values)):
                    items.append(change_path_in_values(result[key][item]))
                result[key] = items
    print(result)
    return result


@contextlib.contextmanager
def create_input_yml(inputs_dictionary: Dict = None):
    """
    Create temp file with random name to avoid collisions with other concurrent tests
    """
    with tempfile.NamedTemporaryFile(mode="w") as file:
        if inputs_dictionary:
            yaml.dump(inputs_dictionary, file)
        yield file.name


def create_dict_for_input_file(name: str, resources) -> dict:
    return {"class": "File", "path": os.path.join(resources, name)}


@lru_cache
def get_username():
    client = ArvadosClient()
    user = client.get_current_user()
    return user["full_name"] or user["username"]
