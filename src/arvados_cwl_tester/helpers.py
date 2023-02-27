import contextlib
from functools import lru_cache
from typing import Dict
from pathlib import Path

import yaml
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


def change_path_in_values(item_dict: dict) -> dict:
    result = item_dict.copy()

    if "path" in item_dict:
        if not item_dict["path"].startswith("keep:"):
            result["path"] = str(Path(result["path"]).resolve())
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
    return result


@contextlib.contextmanager
def create_input_yml(inputs_dictionary: Dict = None):
    """
    Create temp file with random name to avoid collisions with other concurrent tests
    """
    with tempfile.NamedTemporaryFile(mode="w") as file:
        if inputs_dictionary:
            yaml.dump(change_local_paths_to_abs(inputs_dictionary), file)
        yield file.name


@lru_cache
def get_username():
    client = ArvadosClient()
    user = client.get_current_user()
    return user["full_name"] or user["username"]
