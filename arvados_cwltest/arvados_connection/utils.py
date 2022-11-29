from arvados_cwltest.arvados_connection.client import ArvadosClient
from arvados_cwltest.arvados_connection.entities import Process, ProcessStatus
from arvados_cwltest.cwl_runner import run_cwl_arvados
from arvados_cwltest.helpers import Colors, load_json
import os


def create_new_project(target: str, test_name: str):
    # Create project in target
    client = ArvadosClient()
    project = client.create_project(target, test_name)
    print(Colors.BOLD + f"Project was created succesfully: {project.uuid}")
    return project


def find_process_in_new_project(project_uuid: str):
    client = ArvadosClient()
    return client.get_container_request_by_parent_uuid(project_uuid)


def save_file(collection_uuid: str, filename: str, output_filename: str = None):
    client = ArvadosClient()
    collection = client.get_collection(collection_uuid)
    if not os.path.exists("./logs"):
        os.makedirs("./logs")
    with collection.reader.open(filename, 'r') as file_reader:
        with open(f"./logs/{output_filename}" or f"./logs/{filename}", 'w') as file:
            file.write(file_reader.read())


def check_if_process_is_finished(process: Process):
    if process.status in [
        ProcessStatus.COMPLETED,
        ProcessStatus.FAILED,
        ProcessStatus.CANCELLED
    ]:
        print(Colors.OKBLUE + "Process is finished!")
        return True
    
    print(process.log_uuid.stderr)
    return False


def check_if_project_is_completed(process: Process):
    if process.status == ProcessStatus.COMPLETED:
        print(Colors.OKGREEN + "Process was completed successfully :-) !")
        return True
    log_name = f"{process.uuid}_stderr.txt"
    print(Colors.ERROR + f"Process failed or cancelled :(, saving logs to {log_name}")
    save_file(process.log_uuid, 'stderr.txt', log_name)
    return False


def check_if_collection_output_not_empty(process: Process):
    """
    Checks if output collection in provided process is not an empty collection
    Arguments:
        process: class Process
    Returns:
        boolean - True if collection contains some files, false if is empty
    """
    client = ArvadosClient()
    output = client.get_collection(process.output_uuid)
    if output.file_count > 0:
        print(Colors.OKGREEN + "Output collection is not empty.")
        return True
    print(Colors.ERROR + "Output collection is empty :/")
    return False
    

FILES = None
VARIABLES = None
DIRECTORIES = None
UUIDS = None

if os.path.isfile("./test/variables.json"):
    VARIABLES = load_json("./test/variables.json")
    
    FILES = VARIABLES["resources"]["files"]
    UUIDS = VARIABLES["testing_projects"]
    DIRECTORIES = VARIABLES["resources"]["directories"]


def basic_arvados_test(target_project:str, test_name: str, cwl_path: str, inputs_dictionary: dict=None) -> Process:
    """
    Run process, return process object (class Process)
    Check if project is finished, check if project is completed.
    Arguments:
        target_project: str, uuid of project when process will be executed. Example: arkau-ecds9343fdscdsdcd
        test_name: str, name of the test
        cwl_path: str, path to cwl file that will be executed
        inputs_dictionary: dict, containing cwl inputs. This is optional, because sometimes cwl doesn't require input.
    Returns:
        class Process
    """
    
    new_created_project = create_new_project(target_project, test_name)
    run_cwl_arvados(cwl_path, inputs_dictionary, new_created_project.uuid, new_created_project.name)

    process = find_process_in_new_project(new_created_project.uuid)

    assert check_if_process_is_finished(process)
    assert check_if_project_is_completed(process)
    return process


def create_ouputs_dict(process: Process) -> dict:
    """
    Create dictionary with outputs from process
    Arguments:
        process: class Process
    Returns:
        Dictionary containing outputs filenames as keys and dictionaries as values, with following fields: 'size', 'basename' and 'location'' 
    """
    client = ArvadosClient()
    collection = client.get_collection(process.output_uuid)
    data_hash = collection.portable_data_hash

    outputs = {}
    for file in collection.reader.all_files():
        outputs[file.name()] = {
            "size": file.size(),
            "basename": file.name(),
            "location": f"{data_hash}/{file.name()}"
        }
    return outputs

# def run_pipeline_on_outputs():
#     # just idea
