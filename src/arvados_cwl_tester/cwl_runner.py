from io import StringIO
from typing import Dict
import os

import arvados_cwl

from arvados_cwl_tester.helpers import create_input_yml
from arvados_cwl_tester.helpers import Colors


def run_cwl_arvados(cwl_path: str, inputs_dictionary: Dict, project_id, test_name):
    output = StringIO()
    error = StringIO()
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
        exit_code = arvados_cwl.main(
            args,
            stdout=output,
            stderr=error,
            install_sig_handlers=False,  # to work with parallel testing
        )
    error = error.getvalue()
    if error or exit_code:
        print(error)
        return
