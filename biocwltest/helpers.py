#!/usr/bin/python

import yaml
import os

class colors:
    TESTING_INFO = '\033[95m'
    OKBLUE = '\033[94m'
    RUNNING = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    ERROR = '\033[91m'
    BOLD = '\033[1m'


def load_file(path: str) -> list:
    with open(path, "r") as file:
        lines = file.readlines()
    return lines


def get_cwl_name_from_path(cwl_path):
    pathname = os.path.splitext(cwl_path)[0]
    return os.path.basename(pathname)


def pwd(path_to_file):
    return os.path.dirname(os.path.abspath(path_to_file))


def create_input_yml(inputs_dictionary):
    data = yaml.dump(inputs_dictionary)
    with open("./.input.yml", "w") as yml:
        yml.write(data)


def create_dict_for_input_file(name: str, resources) -> dict:
    return {
        "class": "File",
        "path": os.path.join(resources, name)
    }
