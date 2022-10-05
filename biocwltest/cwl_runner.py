import os
import signal
import subprocess
from typing import Any

from biocwltest.helpers import create_input_yml, Colors

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


def run_cwl(cwl_path: str, inputs_dictionary):
    create_input_yml(inputs_dictionary)
    basedir = "/tmp"
    args = "--leave-tmpdir --debug --custom-net host --js-console --move-outputs --on-error stop".split(" ")
    args.extend(["--basedir", basedir, cwl_path, "./.input.yml"])
    run(args)


def run_cwl_arvados(cwl_path: str, inputs_dictionary, project_id, test_name):
    create_input_yml(inputs_dictionary)
    user = os.popen("git config user.name").read()
    run = subprocess.run([
        'arvados-cwl-runner',
        "--debug",
        "--name", f"{test_name}",
        f"--project-uuid={project_id}",
        "--intermediate-output-ttl", "604800",
        f"{cwl_path}",
        "./.input.yml"
    ], check=True)

