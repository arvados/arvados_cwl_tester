#!/usr/bin/python

# The code taken from:

import os
# TODO check if file exists and do not push if yes
# check if image exists in the cloud and pull
import datetime

from docker import client

import docker


# client = docker.from_env()

class colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    RUNNING = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    ERROR = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def load_file(path: str) -> list:
    with open(path, "r") as file:
        lines = file.readlines()
    return lines


def extract_docker_tag(line: str) -> str:
    phrase_starts = line.find("dockerPull:")
    length = len("dockerPull:")
    after = line[phrase_starts + length:]
    return after.strip()


def take_image_tag_from_cwl(cwl_path) -> str:
    lines = load_file(cwl_path)
    for line in lines:
        if "dockerPull" in line:
            return extract_docker_tag(line)


CLIENT = docker.DockerClient(base_url='unix://var/run/docker.sock')


def get_list_of_images():
    images = CLIENT.images.list()
    return [image.tags[0] for image in images if image.tags != []]


def build_docker_image(tag: str, path: str):
    CLIENT.images.build(path=path, tag=tag)


# def generate_path_to_docker():
#


def setup_docker_image(cwl_path: str):
    tag = take_image_tag_from_cwl(cwl_path)
    images = get_list_of_images()
    if tag in images:
        return
    #pull from dockerhub
    #pull from gitlab
    build_docker_image()




def create_output_dir_name(cwl_name: str) -> str:
    return datetime.datetime.now().strftime(f"{cwl_name})_%H.%M.%S_%m.%d.%y")


def create_output_dir(dir_name: str):
    path = os.path.join("/tmp", dir_name)
    if os.path.exists(path):
        return
    os.mkdir(path)


def run_cwl(path: str):
    os.system(f"cwl-runner {path} ../.input.yml")

#


# # Folder
#
#

#
#
# def clean_tmp():
#     pass
#
#
# def print_colored_text():
#     pass
#
#
# # OUTPUTS
# def check_file_exists():
#     pass
#
#
# def validate_bam():
#     pass
#
#
# def validate_vcf():
#     pass
#
#
# def check_file_does_not_exists():
#     pass
#
#
# # def pull_testing_docker():
#     # it is a problem - it is not available on github - howe to solve
#
#
# def run_in_docker():
#     pass
#
#
# def create_test_name_on_arvados():
#     # task_name, date and time
#
#
# def testing_on_arvados(project_id):
#     # if project_id provided lets run on arvados
#     # how to check outputs?? there are no in /tmp anymore
#     # if in arvados do not check /tmp and make any /tmp issues
#
#
# if __main__():
#     argparse():
# project_id, optional. If provided cwl will run on arvados
# clean optional - cleans all tmp
# input_yml
# if_exists_outputs - list of outputs to check if exists
# if does not exists outputs - list of outputs should do not exists
# build - builds all docker images based on dockerfiles

# validate -make validation of pipelines - what should have main pipeline: label, doc, doc for every input,
# maybe something about resources
