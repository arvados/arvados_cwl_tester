# arvados_cwl_tester - framework for testing Common Workflow Language on Arvados

## Introduction

*arvados_cwl_tester* library is dedicated to people, that develop pipelines in CWL and run them on Arvados. It allows to create easy and reproducible tests for CWL scripts, which you can keep in your repository inside python script and run them using `pytest` package from python (https://docs.pytest.org/en/7.1.x/). Usage of this library requires some basic Python knowledge, but don't be afraid - is super easy. Let's get started!

## Installation

### Set up conda environment

```bash
wget https://repo.anaconda.com/miniconda/Miniconda3-py38_4.12.0-Linux-x86_64.sh
sh Miniconda3-py38_4.12.0-Linux-x86_64.sh
conda install --no-deps pip
pip install virtualenv
```

### Create virtualenv in project directory

```bash
virtualenv venv
```

### Activate virtualenv

``` bash
source venv/bin/activate
```

### Install arvados-cwl-tester

You need to install arvados_cwl_tester via  'pip install', according to this instructions:

```
pip install
```

## Steps

Library contains some set of functions, that allows to run a process on Arvados and later get information about outputs and check if the files are as you expect.
If you run the test from command line following things happen:

. Empty project on Arvados is created.
. `arvados-cwl-runner` creates a process that runs your CWL scripts inside this project.
. Logs for the process are printed out in the terminal window.
. Pytest status is printed out in the terminal window. If workflow status is `completed` pytest passes. If workflow status is `failed` or `cancelled` - it fails.
. If workflow status is `completed`, *you can develop your own tests using included functions* (<<Arvados-cwl-tester Functions>>).
. After one week project including all processes and outputs is removed from Arvados. 


## Arvados-cwl-tester Functions

Arvados Cwl Test is implemented as Python library and can be executed using pytest (https://docs.pytest.org/en/7.1.x/)

*basic_arvados_test*

This is basic function that you can use to test cwl on arvados. It returns 'Process' object, that is required as input to other testing functions. 

```python
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
```

*create_ouputs_dict*

```python
def create_ouputs_dict(process: Process) -> dict:
    """
    Create dictionary with outputs from process
    Arguments:
        process: class Process
    Returns:
        Dictionary containing outputs filenames as keys and dictionaries as values, with following fields: 'size', 'basename' and 'location'' 
    """
```

*check_if_collection_output_not_empty*

```python
def check_if_collection_output_not_empty(process: Process):
    """
    Checks if output collection in provided process is not an empty collection
    Arguments:
        process: class Process
    Returns:
        boolean - True if collection contains some files, false if is empty
    """
```

## Examples of usage

### Create python file

Define all tests you need in `test_some_name.py` file. Here you can see an example how this file can look like:

```python
from arvados_cwl_tester.arvados_connection import utils


def test_single_step():

# run the test and define in variable test_run to use it later
    test_run = basic_arvados_test(
        testing_uuid,
        "Example test",
        "components/single_step/single_step.cwl",
        {
            "name": "example.txt"
            }
            )

# Check if output collection is not empty - for example in cases when File[] or Directory[] is the output
    assert check_if_collection_output_not_empty(test_run)

# There is a repsresentation how output dictionary looks like
    assert create_ouputs_dict(test_run) == {
        'example.txt': {
            'size': 0,
            'basename': 'example.txt',
            'location': '240a2608b2d56bb36d2b3d00ae5fcf41+53/example.txt'
            }
            }
# Check if there is a specific file in outputs
    assert 'example.txt' in create_ouputs_dict(test_run)

# Be sure if output has some specific size you expect
    assert create_ouputs_dict(test_run)['example.txt]["size"] > 0

```

### How to use Input Variables

Sometimes there are multiple testing scripts in single repository and there are some variables, that you would like to share between your python testing scripts, to not repeat them in every place. For this purpose Arvados CWL test contains implementation that allows to store them in json file named `./test/variables.json`

For example::
```json
{
  "testing_projects": {
    "ardev": "ardev-j7d0g-ucckjtjhhp7xq81",
    "arind": "arind-j7d0g-ky58se83cx2wh39",
    "arkau": "arkau-j7d0g-9cs24q86tesl6rm"
  },
  "resources": {
    "directories": {
      "two_1000000_inforR_fastq": {
        "class": "Directory",
        "path": "keep:271cbc530a4fe42173a72d53531ad849+225"
      }
    },
    "files": {
      "reference_genome": {
        "class": "File",
        "path": "keep:570c54e5cc295045cfe9f5b361d63e36+6185/Homo_sapiens_assembly38.fasta",
        "secondaryFiles": [
          {
            "class": "File",
            "path": "keep:570c54e5cc295045cfe9f5b361d63e36+6185/Homo_sapiens_assembly38.fasta.fai"
          }
        ]
      },
      "intervals": {
        "class": "File",
        "path": "keep:11a2a794048a689efb7ecb1e1e66d1e8+12334/wgs_calling_regions.hg38.bed"
      }
    }
  }
}
```

Use `FILES`, `DIRECTORIES` and `UUIDS` in python script importing them as::

```python
from arvados_cwl_tester.arvados_connection.utils import FILES, DIRECTORIES, UUIDS

DIRECTORIES["two_1000000_inforR_fastq"]
UUIDS["akau"]
FILES["intervals"]

```

### How to Execute Tests from Command line

```bash
pytest -s
```

To run single test define `-k keyword` to choose some subset of tests

```bash
pytest -k my_lovely_test
```

To run all tests from specific file run:

```bash
pytest test/test_main.py -s
```

To run more tests in parallel: 

```bash
pytest --workers 5 --tests-per-worker auto
```

And more options you can find in pytest library documentation.

## Development of the library

. Fork or pull and create branch
. Write the code
- write unit tests for your functions
- build package (every commit builds package on Gitlab)
- merge request