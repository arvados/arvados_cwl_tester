import os

from tools import load_file, run_cwl, create_output_dir, extract_docker_tag, get_list_of_images, check_if_docker_exists_locally


def test_load_file():
    assert type(load_file("./docker/single_step/Dockerfile")) == list


def test_extract_docker_tag():
    assert extract_docker_tag("    dockerPull: ubuntu:20.04") == "ubuntu:20.04"


def test_get_list_of_images():
    assert type(get_list_of_images()) == list
    assert len(get_list_of_images()) > 0


def test_run_cwl():
    run_cwl("components/single_step/single_step.cwl")


def test_create_output_dir():
    create_output_dir("test")
    assert os.path.isdir("/tmp/test") is True



