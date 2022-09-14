#!/usr/bin/python
# TODO check if file exists and do not push if yes
import datetime
import os
from typing import Any
import yaml
import filecmp
from datetime import datetime
import signal
import glob
import subprocess

from biocwltest.arvados_client import ArvadosClient

"""
███████████████████████████
███████▀▀▀░░░░░░░▀▀▀███████
████▀░░░░░░░░░░░░░░░░░▀████
███│░░░░░░░░░░░░░░░░░░░│███
██▌│░░░░░░░░░░░░░░░░░░░│▐██
██░└┐░░░░░░░░░░░░░░░░░┌┘░██
██░░└┐░░░░░░░░░░░░░░░┌┘░░██
██░░┌┘▄▄▄▄▄░░░░░▄▄▄▄▄└┐░░██
██▌░│██████▌░░░▐██████│░▐██
███░│▐███▀▀░░▄░░▀▀███▌│░███
██▀─┘░░░░░░░▐█▌░░░░░░░└─▀██
██▄░░░▄▄▄▓░░▀█▀░░▓▄▄▄░░░▄██
████▄─┘██▌░░░░░░░▐██└─▄████
█████░░▐█─┬┬┬┬┬┬┬─█▌░░█████
████▌░░░▀┬┼┼┼┼┼┼┼┬▀░░░▐████
█████▄░░░└┴┴┴┴┴┴┴┘░░░▄█████
███████▄░░░░░░░░░░░▄███████
██████████▄▄▄▄▄▄▄██████████
███████████████████████████
"""
# Copied from cwltool library (bug - no idea what I'm doing) # TODO pull request tpo cwltool???
from cwltool.main import main, _terminate_processes

def _signal_handler(signum: int, _: Any) -> None:
    _terminate_processes()

def run(*args: Any, **kwargs: Any) -> None:
    signal.signal(signal.SIGTERM, _signal_handler)
    try:
        assert main(*args, **kwargs) == 0
    finally:
        _terminate_processes()


# Ours code
from biocwltest.helpers import *

def run_cwl(cwl_path: str, inputs_dictionary):
    helpers.create_input_yml(inputs_dictionary)
    basedir = "/tmp"
    args = "--leave-tmpdir --debug --custom-net host --js-console --move-outputs --on-error stop".split(" ")
    args.extend(["--basedir", basedir, cwl_path, "./.input.yml"])
    run(args)


def test_arvados_cwl_runner():
    
    import arvados
    import json
    api = arvados.api()
    x = json.dumps(api.container_requests().list().execute(), indent=4)
    with open("sample.json", "w") as outfile:
        outfile.write(x)


# NEW PLANS


def create_new_project(target):
    # Create project in target
    client = ArvadosClient()
    project_uuid = client.create_project(target)['uuid']
    print(f"Project was created succesfully: {project_uuid}")
    return project_uuid


def run_cwl_arvados(cwl_path: str, inputs_dictionary, project_id, test_name):
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
    # do not make anything else until this function is completed


def find_process_in_new_project(project_uuid):
    client = ArvadosClient()
    return client.get_container_request_by_parent_uuid(project_uuid)


def check_if_process_is_completed(process):
    client = ArvadosClient()
    container = client.get_container(process['container_uuid'])
    return container["state"] in ["Complete", "Cancelled"]


def basic_arvados_test(target_project, test_name, cwl_path, inputs_dictionary) -> dict:
    new_created_project = create_new_project(target_project)
    run_cwl_arvados(cwl_path, inputs_dictionary, new_created_project, test_name)
    process = find_process_in_new_project(new_created_project) # Process will be a dictionary
    assert check_if_process_is_completed(process) == True

    return process

"""
Plan:


1. Zrób nowy projekt, który ma zniknąć po tygodniu
2. Uruchom w tym projekcie arvados-cwl-runner
    a. daj w subprocess żeby następna komenda uruchomiła się dopiero jak ten subprocess się skończy
    b. Zrób nazwę procesu
3. Za pomocą items wyszukaj w tym projekcie item, który będzie tym procesem. Sprawdź jaki jest jego status - jeżeli nie jest success to wtedy zwróć błąd. 
    sprawdź jakieś outputy i np. ich wielkość itd. 
4. Opcjonalnie uruchom inny cwl, który sprawdzi te outputy np. vcf ile ma lnijek, czy jest poprawny, czy ma indeks itd itp

pytest - niech uruchomi te testy parallelnie, po to żeby nie czekać i żeby na arvadosie już się liczyło

Pomysły:
- Mapowanie odpowiedzi z Arvadosa do klas pythona
- Dodanie funkcji to sprawdzania statusu procesu (failed, cancelled, completed):
  pole `state` in container:
  Queued: Queued
  Cancelled: Cancelled
  Completed: Completed, exit_code = 0 ((["container_requests.container.state","=","Complete"],["container_requests.container.exit_code","=","0"]))
  Failed: Completed, exit_code != 0 (["container_requests.container.state","=","Complete"],["container_requests.container.exit_code","!=","0"])
  Running: ["container_requests.container.state","=","Running"]
"""