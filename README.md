# Framework for testing Common Workflow Language on Arvados - arvados_cwl_tester

Note: This is not the final, official version

Thank you for interest in arvados-cwl-tester framework. Please note that the current version is not the final, official version. While the frameworkk is usable , the work is still in progress. The official version will be released soon. 

## Introduction

**arvados_cwl_tester** framework is dedicated to people, that develop pipelines in CWL and run them on Arvados. It allows to create easy and reproducible tests for CWL CommandLineTools and Workflows and run them in parallel on Arvados, using `pytest`.

**arvados_cwl_tester** API allows to write tests using python code and organize them in python script. 

Every test runs process on Arvados in temporary subproject, that will be removed after some time automaticly that that will keep your testing space clean and tidy. 

## Get started

### Setup environment

1. Create testing environment

```bash
virtualenv venv
source venv/bin/activate
```

2. Install arvados-cwl-tester

```bash
git clone https://github.com/arvados/arvados_cwl_tester.git
cd arvados_cwl_tester
pip install .
```

### Write your first test

Define all tests you need in `test_<your_name>.py` file. Here you can see an example how this file can look like:

```python
from arvados_cwl_tester import create_ouputs_dict, check_if_collection_output_not_empty, basic_arvados_test


def test_single_step():

# run the test and define in variable test_run to use it later
    test_run = basic_arvados_test(
        "ardev-xxxxxxxxxxxxx",
        "Hello World!",
        "./components/single_step/single_step.cwl",
        {
            "name": "example.txt"
            }
            )

# Check if output collection is not empty - for example in cases when File[] or Directory[] is the output
    assert check_if_collection_output_not_empty(test_run)

# Check if there is a specific file in outputs
    assert 'example.txt' in create_ouputs_dict(test_run)

# Be sure if output has some specific size you expect
    assert create_ouputs_dict(test_run)['example.txt']["size"] > 0

```

### Execute the test

Run in commandline:

```bash
pytest -k single_step
```


## Arvados-cwl-tester Functions


**basic_arvados_test()**

This is basic function that you can use to test cwl on arvados. It returns 'Process' object, that is required as input to other testing functions. 

```python
def basic_arvados_test(target_project: str, test_name: str, cwl_path: str, inputs_dictionary: dict=None) -> Process:
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
```

**create_ouputs_dict()**

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

**check_if_collection_output_not_empty()**

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

-----

**variables.json**

Arvados CWL Tester contains implementation that allows to store variables in json file named `./test/variables.json`. Those variables can be imported inside different python testing scripts if you want to organize your tests in seperated python files. 

For example::
```json
{
  "testing_projects": {
    "ardev": "ardev-*******************81",
    "arind": "arind-*******************92",
    "arkau": "arkau-*******************82"
  },
  "resources": {
    "directories": {
      "fastq_collection": {
        "class": "Directory",
        "path": "keep:********************************6185"
      }
    },
    "files": {
      "reference_genome": {
        "class": "File",
        "path": "keep:********************************6184/Homo_sapiens_assembly38.fasta",
        "secondaryFiles": [
          {
            "class": "File",
            "path": "keep:********************************6183/Homo_sapiens_assembly38.fasta.fai"
          }
        ]
      },
      "intervals": {
        "class": "File",
        "path": "keep:********************************6182/wgs_calling_regions.hg38.bed"
      }
    }
  }
}
```

Import `FILES`, `DIRECTORIES` and `UUIDS` in python script and use them in your tests:

```python
from arvados_cwl_tester import FILES, DIRECTORIES, UUIDS, basic_arvados_test

def test_single_step():
    test_run = basic_arvados_test(
        UUIDS["akau"],
        "I am using testing variables!",
        "./my_cwl.cwl",
        {
            "fastq_collection": DIRECTORIES["fastq_collection"],
            "intervals": FILES["intervals"],
            "reference_genome": FILES["reference_genome"]
        }
        )

```

### How to execute tests in parallel


Run multiple tests in parallel - it will execute your tests as separated processes on arvados and you will save time. 

```bash
pytest --workers 10 --tests-per-worker auto
```

*workers* defines how many tetst will be executed in parallel

## Development of the library

To activate development environment:

```bash
bash setup.sh
source venv/bin/activate

```

