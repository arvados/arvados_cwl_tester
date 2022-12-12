import os
import subprocess
from typing import Any
from arvados_cwltest.helpers import Colors

from arvados_cwltest.helpers import create_input_yml, Colors

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


def run_cwl_arvados(cwl_path: str, inputs_dictionary, project_id, test_name):
    create_input_yml(inputs_dictionary)
    user = os.popen("git config user.name").read()
    try:
        run_cwl = subprocess.run([
            'arvados-cwl-runner',
            "--debug",
            "--name", f"{test_name}",
            f"--project-uuid={project_id}",
            "--intermediate-output-ttl", "604800",
            f"{cwl_path}",
            "./.input.yml"
        ], check=True, capture_output=True)
        print(run_cwl.stdout.decode())
        print(run_cwl.stderr.decode())
    except subprocess.CalledProcessError as e:
        print(e.stderr.decode())
