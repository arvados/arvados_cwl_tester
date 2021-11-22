#!/usr/bin/python

# TODO check if file exists and do not push if yes
import datetime
import json
import os
import yaml
import docker


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
    print(colors.OKBLUE + f"\n Dockerpull requirement: {after.strip()}")
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
    print(colors.OKBLUE + f"\n Building docker image {tag} based on {dockerfile_path}")


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
        print(colors.OKBLUE + f"\n Docker image {tag} exists locally")
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


def check_element(key_name, data, name, pipeline: bool):
    if key_name in data:
        print(colors.OKGREEN + f"{name} contains {key_name}")
        return
    if pipeline:
        raise Exception(print(colors.ERROR + f"{name} pipeline does not contain {key_name}"))
    print(colors.WARNING + f"{name} does not contain {key_name}")
    return


def validate_cwl_metadata(path, pipeline=False):
    cwl_data = convert_cwl_to_dict(path)
    for key_name in ["label", "doc", "hints", "inputs", "outputs"]:
        check_element(key_name, cwl_data, f"Cwl script {path}", pipeline)
    for i in cwl_data["inputs"]:
        check_element("doc", cwl_data["inputs"][i], f"Input '{i}' for Cwl script {path}", pipeline)


def run_cwl(cwl_path: str, inputs_dictionary):
    print(colors.RUNNING + f"\n Running cwl workflow: {cwl_path}...")
    create_input_yml(inputs_dictionary)
    basedir = "/tmp"
    cwl_name = get_cwl_name_from_path(cwl_path)
    outdir = create_output_dir(cwl_name)
    os.system(f"cwl-runner --js-console --move-outputs --basedir {basedir} --outdir {outdir} {cwl_path} ./.input.yml")
    result = {
        "cwl": cwl_path,
        "inputs": inputs_dictionary,
        "outputdir": outdir,
        "list_of_outputs": create_list_of_files_in_dir(outdir)
    }
    print(json.dumps(result, indent=4))
    return result



def check_if_file_exists(path) -> bool:
    return os.path.isfile(path)



def check_file_does_not_exists(path) -> bool:
    return not os.path.isfile(path)
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

# maybe something about resources
