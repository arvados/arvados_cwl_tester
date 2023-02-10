import os
from io import StringIO

import arvados_cwl

from arvados_cwltest.helpers import create_input_yml


def run_cwl_arvados(cwl_path: str, inputs_dictionary, project_id, test_name):
    user = os.popen("git config user.name").read()
    output = StringIO()
    error = StringIO()
    with create_input_yml(inputs_dictionary) as filename:
        print(filename)
        exit_code = arvados_cwl.main(
            ["--debug",
             "--name", f"{test_name} {user}",
             f"--project-uuid={project_id}",
             "--intermediate-output-ttl", "604800",
             cwl_path,
             filename],
            stdout=output,
            stderr=error,
            install_sig_handlers=False  # to work with parallel testing
        )
    error = error.getvalue()
    if error or exit_code:
        print(error)
        return


# --no-wait option returns process uuid, not cwl output:
# usage:
# process_uuid = output.getvalue().strip()
# process = asyncio.run(_wait_for_container_finish(process_uuid))

# async def _wait_for_container_finish(process_uuid: str):
#     client = ArvadosClient()
#     while True:
#         await asyncio.sleep(5)
#         process = client.get_container_request(process_uuid)
#         if process.status in [
#             ProcessStatus.COMPLETED,
#             ProcessStatus.FAILED,
#             ProcessStatus.CANCELLED
#         ]:
#             return process
