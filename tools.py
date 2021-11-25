#!/usr/bin/python

# TODO check if file exists and do not push if yes
import datetime
import os
import yaml
import docker
import filecmp


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


def extract_docker_tag(line: str) -> str:
    phrase_starts = line.find("dockerPull:")
    length = len("dockerPull:")
    after = line[phrase_starts + length:]
    print(colors.OKBLUE + f"\nINFO: Dockerpull requirement: {after.strip()}")
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


def build_docker_image(dockerfile_path: str, tag: str):
    CLIENT.images.build(path=dockerfile_path, tag=tag)
    print(colors.OKBLUE + f"\nINFO: Building docker image {tag} based on {dockerfile_path}")


def get_cwl_name_from_path(cwl_path):
    pathname = os.path.splitext(cwl_path)[0]
    return os.path.basename(pathname)


def generate_path_to_docker(cwl_path):
    cwl_name = get_cwl_name_from_path(cwl_path)
    return f"./docker/{cwl_name}/Dockerfile"


def setup_docker_image(cwl_path: str):
    tag = take_image_tag_from_cwl(cwl_path)
    images = get_list_of_images()
    if tag in images:
        print(colors.OKBLUE + f"\nINFO: Docker image {tag} exists locally")
        return
    # pull from dockerhub
    # pull from gitlab
    build_docker_image(generate_path_to_docker(cwl_path), tag)


def create_output_dir_name(cwl_name: str) -> str:
    return datetime.datetime.now().strftime(f"%H.%M.%S_%m.%d.%y")


def create_output_dir(dir_name_same_as_cwl: str):
    outdir = create_output_dir_name(dir_name_same_as_cwl)
    path = os.path.join("/tmp", dir_name_same_as_cwl, outdir)
    if os.path.exists(path):
        return path
    os.mkdir(path)
    return path


def create_input_yml(inputs_dictionary):
    data = yaml.dump(inputs_dictionary)
    with open("./.input.yml", "w") as yml:
        yml.write(data)


def create_list_of_files_in_dir(dir_path):
    # TODO be sure is necessary
    d = []
    for file in os.listdir(dir_path):
        x = {"name": file}
        if os.path.isdir(file):
            x['type'] = "directory"
            x['children'] = [create_list_of_files_in_dir(os.path.join(dir_path, x)) for x in os.listdir(dir_path)]
        else:
            x['type'] = "file"
    d.append(x)
    return d


def convert_cwl_to_dict(cwl_path):
    with open(cwl_path) as cwl:
        return yaml.full_load(cwl)


def check_key_in_cwl(key_name, data, name, pipeline: bool):
    if key_name in data:
        print(colors.OKGREEN + f"\nPASSED: {name} contains {key_name}")
        return
    if pipeline:
        raise Exception(print(colors.ERROR + f"\nERROR: {name} pipeline does not contain {key_name}"))
    print(colors.WARNING + f"\nWARNING: {name} does not contain {key_name}")
    return


def load_version(steps_path: str) -> str:
    return convert_cwl_to_dict(steps_path)["cwlVersion"]


def check_if_cwl_versions_are_the_same(cwl_data: dict):
    cwl_versions = {}
    cwl_versions["main_pipeline"] = cwl_data["cwlVersion"]
    if "steps" in cwl_data:
        for step_name, values in cwl_data["steps"].items():
            cwl_versions[cwl_data["steps"][step_name]["run"]]= load_version(values["run"])
        first = list(cwl_versions.values())[0]
        for cwl, version in cwl_versions.items():
            if version == first:
                next
            else:
                #TODO decide if make exception or print error
                # raise Exception(
                #     f"Pipeline: '{cwl}' has different version than the rest used in pipeline: {cwl_versions}"
                # )
                print(colors.ERROR + f"\nERROR: Pipeline: '{cwl}' has different version than the rest used in pipeline: {cwl_versions}")
    return


def validate_cwl_metadata(path, pipeline=False):
    cwl_data = convert_cwl_to_dict(path)
    for key_name in ["label", "doc", "hints", "inputs", "outputs"]:
        check_key_in_cwl(key_name, cwl_data, f"Cwl script {path}", pipeline)
    for i in cwl_data["inputs"]:
        check_key_in_cwl("doc", cwl_data["inputs"][i], f"Input '{i}' for Cwl script {path}", pipeline)
    check_if_cwl_versions_are_the_same(cwl_data)


def run_cwl(cwl_path: str, inputs_dictionary):
    print(colors.RUNNING + f"\n INFO: Running cwl workflow: {cwl_path}...")
    create_input_yml(inputs_dictionary)
    basedir = "/tmp"
    cwl_name = get_cwl_name_from_path(cwl_path)
    outdir = create_output_dir(cwl_name)
    os.system(f"cwl-runner --move-outputs --basedir {basedir} --outdir {outdir} {cwl_path} ./.input.yml")
    result = {
        "cwl": cwl_path,
        "inputs": inputs_dictionary,
        "outputdir": outdir,
        "list_of_outputs": create_list_of_files_in_dir(outdir)
    }
    return result


def check_if_file_exists(path) -> bool:
    return os.path.isfile(path)


def check_file_does_not_exists(path) -> bool:
    return not os.path.isfile(path)


def compare_result_with_expected(result_path, expected_path) -> bool:
    return filecmp.cmp(result_path, expected_path)


# def validate_outputs(info_dict: dict):
#     for output in info_dict():
#         if


# def create_test_name_on_arvados():
#     # task_name, date and time
#
#
# def testing_on_arvados(project_id):
#     # if project_id provided lets run on arvados
#     # how to check outputs?? there are no in /tmp anymore
#     # if in arvados do not check /tmp and make any /tmp issues
#

