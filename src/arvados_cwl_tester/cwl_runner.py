import subprocess
from typing import Dict

from arvados_cwl_tester.helpers import Colors
from arvados_cwl_tester.helpers import create_input_yml


def run_cwl_arvados(cwl_path: str, inputs_dictionary: Dict, project_id, test_name):
    with create_input_yml(inputs_dictionary) as filename:
        print(Colors.OKBLUE + f"Process '{test_name}' is starting...")
        args = [
            "--basedir",
            ".",
            "--debug",
            "--name",
            f"{test_name}",
            f"--project-uuid={project_id}",
            "--intermediate-output-ttl",
            "604800",
            cwl_path,
            filename,
        ]
        print(args)
        try:
            run_cwl = subprocess.run([
                'arvados-cwl-runner',
                *args
            ], check=True, capture_output=True)
            print(run_cwl.stdout.decode())
            print(run_cwl.stderr.decode())
        except subprocess.CalledProcessError as e:
            print(e.stderr.decode())
