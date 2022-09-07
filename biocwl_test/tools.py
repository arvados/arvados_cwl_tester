#!/usr/bin/python

# TODO check if file exists and do not push if yes
import datetime
import os
from typing import Any
import yaml
import docker
import filecmp
from datetime import datetime
import glob
import subprocess
from cProfile import run
from cwltool.main import run as runCwl



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


def get_outputs(path):
    cwl_data = convert_cwl_to_dict(path)
    return list(cwl_data["outputs"].keys())


def create_dict_for_input_file(name: str, resources) -> dict:
    return {
        "class": "File",
        "path": os.path.join(resources, name)
    }


def run_cwl(cwl_path: str, inputs_dictionary):
    create_input_yml(inputs_dictionary)
    basedir = "/tmp"
    cwl_name = get_cwl_name_from_path(cwl_path)
    outdir = create_output_dir(cwl_name)
    args = "--leave-tmpdir --debug --custom-net host --js-console --move-outputs".split(" ")
    args.extend(["--basedir", basedir, "--outdir", outdir, cwl_path, "./.input.yml"])
    runCwl(args)
    

def run_cwl_arvados(cwl_path: str, inputs_dictionary, project_id, comment=None):
    print(colors.RUNNING + f"\n INFO: Running cwl workflow on arvados: {cwl_path}..., project_id: {project_id}")
    create_input_yml(inputs_dictionary)
    user = os.popen("git config user.name").read()
    subprocess.run([
        'arvados-cwl-runner',
        "--debug",
        "--name",
        f"Testing {os.path.basename(cwl_path)} {user}",
        f"--project-uuid={project_id}",
        "--intermediate-output-ttl", "604800",
        f"{cwl_path}",
        "./.input.yml"
    ])


def check_if_file_exists(path) -> bool:
    exist = os.path.isfile(path)
    if exist:
        print(colors.OKGREEN + f"File {path} exists.")
        return exist
    print(colors.ERROR + f"File {path} does not exist. List of files:")
    for file in glob.glob(os.path.dirname(path) + "/*"):
        print(" - " + os.path.basename(file))
    return exist


def check_file_does_not_exists(path) -> bool:
    return not os.path.isfile(path)


def check_file_is_not_empty(outdir, path) -> bool:
    file = os.path.join(outdir, path)
    if os.path.getsize(file) > 0:
        return True
    return False


def compare_result_with_expected(result_path, expected_path) -> bool:
    return filecmp.cmp(result_path, expected_path)


def check_files_in_out_dir(outdir: str, files: list) -> bool:
    # TODO does it check all list for sure?

    for file in files:
        assert check_if_file_exists(os.path.join(outdir, f"{file}")) == True
        # assert check_file_is_not_empty == True # TODO debug


def how_many_variants_in_vcf(outdir: str, filename: str):
    # TODO after setup py is completed lets do it by pysam
    # TODO implement gzipped files
    with open(os.path.join(outdir, filename), "r") as file:
        variants = 0
        for line in file:
            if not "#" in line[0]:
                variants += 1
    print(colors.OKBLUE + f"{filename} contains {variants} variants.")
    return variants
