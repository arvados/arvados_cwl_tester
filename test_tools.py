from tools import *


def test_load_file():
    assert type(load_file("./docker/testing_image/Dockerfile")) == list


def test_extract_docker_tag():
    assert extract_docker_tag("    dockerPull: ubuntu:20.04") == "ubuntu:20.04"


def test_get_list_of_images():
    assert type(get_list_of_images()) == list
    assert len(get_list_of_images()) > 0


def test_pull_docker_from_dockerhub():
    pull_docker_from_dockerhub("ubuntu")


def test_search_docker_in_dockerhub():
    assert search_docker_in_dockerhub("this_does_not_exists_in_dockerhub")[0] == False
    assert search_docker_in_dockerhub("ubuntu")[0] == True


def test_build_docker_image():
    tag = "test:latest"
    images = get_list_of_images()
    if tag in images:
        print(colors.TESTING_INFO + f"\nTESTING INFO: Removing docker image {tag} for testing...")
        CLIENT.images.remove(tag)
    build_docker_image("./docker/test/", tag)


def test_setup_docker_image():
    setup_docker_image("./components/single_step/single_step.cwl")


def test_create_input_yml():
    create_input_yml(
        {
            "metaInfoFile": {
                "class": "File",
                "location": "keep:b05083d7db79c2e4e211dbef369e98a7+76/sampleList_E-MTAB-8208.txt",
            },
            "fastqCollection": {
                "class": "File",
                "location": "keep:00780063929dcd34186ae2394505202d+422439",
            }
        }
    )


def test_create_output_dir():
    create_output_dir("test")
    assert os.path.isdir("/tmp/test") is True


def test_run_cwl(): # 
    inputs = {"name": "example.txt"}
    run_cwl("components/single_step/single_step.cwl", inputs)


def test_load_version():
    assert load_version("./example_pipeline.cwl") == "v1.0"


def test_validate_metadata_component():
    validate_cwl_metadata("./components/single_step/single_step.cwl")


def test_validate_cwl_metadata_pipeline():
    validate_cwl_metadata("./example_pipeline.cwl", pipeline=True)


def test_get_outputs():
    assert get_outputs("./components/single_step/single_step.cwl") == ['testing_result']


# def test_validate_cwl_metadata_pipeline():
#     validate_cwl_metadata("../arvados-workflow-sentieon/sentieon-germline-gvcf_multi-cohort.cwl", pipeline=True)


# def test_validate_outputs():
#     output_data = {
#         "output1": {
#             "compare": path_to_compare,
#             "validate_bam": True,
#         }
#     }
#     info_dict = {
#
#     }
#     validate_outputs(output_data, info_dict)


# TO DO - setup all docker images for whole project - for each cwl