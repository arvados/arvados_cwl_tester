import os

from tools import load_file, run_cwl, create_output_dir, extract_docker_tag, get_list_of_images, setup_docker_image, \
    build_docker_image, CLIENT, generate_path_to_docker, colors, create_input_yml, validate_cwl_metadata


def test_load_file():
    assert type(load_file("./docker/single_step/Dockerfile")) == list


def test_extract_docker_tag():
    assert extract_docker_tag("    dockerPull: ubuntu:20.04") == "ubuntu:20.04"


def test_get_list_of_images():
    assert type(get_list_of_images()) == list
    assert len(get_list_of_images()) > 0


def test_generate_path_to_docker():
    assert generate_path_to_docker("./components/single_step/single_step.cwl") == "./docker/single_step/Dockerfile"


def test_build_docker_image():
    tag = "test:latest"
    images = get_list_of_images()
    if tag in images:
        print(colors.TESTING_INFO + f"\n Removing docker image {tag} for testing...")
        CLIENT.images.remove(tag)
    build_docker_image("./docker/test/", tag)


def test_setup_docker_image():
    setup_docker_image("./components/single_step/single_step.cwl")


def test_create_input_yml():
    create_input_yml({"name": "example.txt", "path": "some"})


def test_run_cwl():
    inputs = {"name": "example.txt"}
    run_cwl("components/single_step/single_step.cwl", inputs)


def test_create_output_dir():
    create_output_dir("test")
    assert os.path.isdir("/tmp/test") is True


def test_validate_metadata_component():
    validate_cwl_metadata("./components/single_step/single_step.cwl")


def test_validate_cwl_metadata_pipeline():
    validate_cwl_metadata("./example_pipeline.cwl", pipeline=True)

