#!/usr/bin/python

# TODO check if file exists and do not push if yes
import datetime
import os
from typing import Any
import yaml
import docker
import filecmp
from datetime import date, datetime
import glob
from cProfile import run


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


def take_image_tag_from_cwl(cwl_path) -> Any:
    lines = load_file(cwl_path)
    for line in lines:
        if "dockerPull" in line:
            return extract_docker_tag(line)
    return False


CLIENT = docker.DockerClient(base_url='unix://var/run/docker.sock')


def get_list_of_images():
    images = CLIENT.images.list()
    return [image.tags[0] for image in images if image.tags != []]


def build_docker_image(dockerfile_path: str, tag: str):
    print(colors.OKBLUE + f"\nINFO: Building docker image {tag} based on {dockerfile_path}")
    CLIENT.images.build(path=dockerfile_path, tag=tag)


def search_docker_in_dockerhub(tag: str):
    print(colors.OKBLUE + f"\nINFO: Searching docker image {tag} on DockerHub")
    images = CLIENT.images.search(tag)
    if len(images) == 0:
        return False, images
    return True, images


def select_most_popular_official_image(images):
    for image in images:
        if image["is_official"]:
            return image["name"]
        else:
            print(colors.WARNING + f"\nWARNING: found image {image['name']} is not official")
            return image['name']


def pull_docker_from_dockerhub(tag: str):
    print(colors.OKBLUE + f"\nINFO: Pulling docker image {tag} from DockerHub")
    CLIENT.images.pull(tag)


def get_cwl_name_from_path(cwl_path):
    pathname = os.path.splitext(cwl_path)[0]
    return os.path.basename(pathname)


def pwd(path_to_file):
    return os.path.dirname(os.path.abspath(path_to_file))


def generate_path_to_dockerfile(cwl_path):
    cwl_name = get_cwl_name_from_path(cwl_path)
    dir = pwd(cwl_path)
    docker = f"{dir}/docker/{cwl_name}/Dockerfile"
    if os.path.exists(docker):
        return docker
    docker = f"{dir}/../../docker/{cwl_name}/Dockerfile"
    if os.path.exists(docker):
        return docker
    return False


# main
def setup_docker_image(cwl_path: str):
    # TODO unfortunately not all docker images are in dirname the same as component (example: sentieon).
    # TODO Additionally building docker command in sentieon is not the same as here. This setup works only for "standard" repo structure
    
    tag = take_image_tag_from_cwl(cwl_path)
    if not tag:
        return
    images = get_list_of_images()
    if tag in images:
        print(colors.OKBLUE + f"\nINFO: Docker image {tag} exists locally")
        return
    dockerhub, images = search_docker_in_dockerhub(tag)
    if dockerhub:
        pull_docker_from_dockerhub(select_most_popular_official_image(images))
    if not generate_path_to_dockerfile(cwl_path):
        raise Exception(f"{tag} image included in DockerRequirement in {cwl_path} does not exists locally, in DockerHub and there is not Dockerfile in repository")
    build_docker_image(generate_path_to_dockerfile(cwl_path), tag)


def setup_docker_images_for_all_cwl():
    main_repo_dir = "../"
    os.chdir(main_repo_dir)
    for cwl_file in glob.glob("*.cwl"):
        setup_docker_image(cwl_file)


def create_output_dir_name(cwl_name: str) -> str:
    return datetime.now().strftime(f"%H-%M-%S_%m-%d-%y")


def create_output_dir(dir_name_same_as_cwl: str):
    outdir = create_output_dir_name(dir_name_same_as_cwl)
    path = os.path.join("/tmp", dir_name_same_as_cwl, outdir)
    cwl_name = os.path.join("/tmp", dir_name_same_as_cwl)
    if not os.path.exists(cwl_name):
        os.mkdir(cwl_name)
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
    pipeline_info = ""
    if pipeline:
        pipeline_info = "PIPELINE "
    if key_name in data:
        print(colors.OKGREEN + f"\n{key_name.upper()} {pipeline_info}PASSED: {name} contains {key_name}")
        return
    if pipeline:
        raise Exception(print(colors.ERROR + f"\n{key_name.upper()} {pipeline_info}ERROR: {name} pipeline does not contain {key_name}"))
    print(colors.WARNING + f"\n{key_name.upper()} WARNING: {name} does not contain {key_name}")
    return


def load_version(steps_path: str) -> str:
    return convert_cwl_to_dict(steps_path)["cwlVersion"]


def validate_cwl_metadata(path, pipeline=False):
    cwl_data = convert_cwl_to_dict(path)
    print(colors.RUNNING + f"\n##### Validation of cwl fields for pipepiline: '{path}' #####")
    for key_name in ["label", "doc"]:
        check_key_in_cwl(key_name, cwl_data, f"Cwl script {path}", pipeline)
    for i in cwl_data["inputs"]:
        check_key_in_cwl("doc", cwl_data["inputs"][i], f"Input '{i}' for Cwl script {path}", pipeline)
    return 


def get_outputs(path):
    cwl_data = convert_cwl_to_dict(path)
    return list(cwl_data["outputs"].keys())


def create_dict_for_input_file(name: str, resources) -> dict:
    return {
        "class": "File",
        "path": os.path.join(resources, name)
    }


# main
def run_cwl(cwl_path: str, inputs_dictionary):
    print(colors.RUNNING + f"\n INFO: Running cwl workflow: {cwl_path}...")
    create_input_yml(inputs_dictionary)
    basedir = "/tmp"
    cwl_name = get_cwl_name_from_path(cwl_path)
    outdir = create_output_dir(cwl_name)
    os.system(f"cwl-runner --leave-tmpdir --debug --custom-net host --js-console --move-outputs --basedir {basedir} --outdir {outdir} {cwl_path} ./.input.yml")
    print(colors.OKBLUE + f"Cwl running completed: {cwl_path}")
    return outdir


# main
def run_cwl_arvados(cwl_path: str, inputs_dictionary, project_id):
    print(colors.RUNNING + f"\n INFO: Running cwl workflow on arvados: {cwl_path}..., project_id: {project_id}")
    create_input_yml(inputs_dictionary)
    dt = f"{datetime.now()}"
    os.system(f'arvados-cwl-runner --debug --name "Testing {dt} {cwl_path}" --project-uuid={project_id} --intermediate-output-ttl 604800 {cwl_path} ./.input.yml')


# main
def check_if_file_exists(path) -> bool:
    exist = os.path.isfile(path)
    if exist:
        print(colors.OKGREEN + f"File {path} exists.")
        return exist
    print(colors.ERROR + f"File {path} does not exist. List of files:")
    for file in glob.glob(os.path.dirname(path) + "/*"):
        print(" - " + os.path.basename(file))
    return exist


# main
def check_file_does_not_exists(path) -> bool:
    return not os.path.isfile(path)


# main
def check_file_is_not_empty(outdir, path) -> bool:
    file = os.path.join(outdir, path)
    if os.path.getsize(file) > 0:
        return True
    return False


# main
def compare_result_with_expected(result_path, expected_path) -> bool:
    return filecmp.cmp(result_path, expected_path)


# main
def check_files_in_out_dir(outdir: str, files: list) -> bool:
    # TODO does it check all list for sure?

    for file in files:
        assert check_if_file_exists(os.path.join(outdir, f"{file}")) == True
        # assert check_file_is_not_empty == True # TODO debug


# main
def how_many_variants_in_vcf(outdir: str, filename: str):
    # TODO after setup py is completed lets do it by pysam
    # TODO implement gzipped files
    with open(os.path.join(outdir, filename),"r") as file:
        variants = 0
        for line in file:
            if not "#" in line[0]:
                variants += 1
    print(colors.OKBLUE + f"{filename} contains {variants} variants.")
    return variants





