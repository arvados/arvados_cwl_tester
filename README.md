# arvados_cwl_tester
## Framework for testing Common Workflow Language on Arvados

![Beta](https://img.shields.io/badge/Status-Beta-yellow)

## Introduction

**arvados_cwl_tester** framework is dedicated to people, that develop pipelines in CWL and run them on Arvados. It allows to create easy and reproducible tests for CWL CommandLineTools and Workflows and run them in parallel on Arvados, using `pytest`.

**arvados_cwl_tester** API allows to write tests using python code and organize them in python script. 

Every test runs process on Arvados in temporary subproject, that will be removed after some time automatically that will keep your testing space clean and tidy. 

## Installation


```
git clone git@github.com:arvados/arvados_cwl_tester.git
cd arvados_cwl_tester
virtualenv venv
source venv/bin/activate
pip install .
```

### Write your first test

Define all tests you need in `test_<your_name>.py` file. Here you can see an example how this file can look like:

```python
from arvados_cwl_tester import *

# Set global variable with project uuid where all your tests will be executed:
arvados_project_uuid("arkau-*******************82")

# Define a test
def test_single_step():
    result = arvados_run(
        "./components/single_step/single_step.cwl",
        {
            "name": "example"
        },
    )
    assert "example.txt" in result.files
    assert result.files["example.txt"]["size"] == 0

```

### Execute the test

Run in command line:

```bash
pytest -k single_step
```

Run multiple tests in parallel - it will execute your tests as separated processes on arvados and you will save time: 

```bash
pytest --workers 10 --tests-per-worker auto
```

### Variables

You can create `./test/variables.json` file which will be used by arvados_cwl_tester to create global variables with matching names. You are free to name and organize your variables in any way you like. It solves problem with repetition of names if you have more testing scripts in your repository and all of them use some common variables. Content of `variables.json` will be imported as dictionary named 'VARIABLES' and uppercase names of main keys. For example you can store project uuids, files, and directories handles, as so:

```json
{
  "arkau": "arkau-*******************82",
  "dirs": {
    "fastq_collection": {
      "type": "Directory",
      "path": "keep:********************************6185"
    }
  },
  "reference_genome": {
    "class": "File",
    "path": "keep:********************************6184/Homo_sapiens_assembly38.fasta",
    "secondaryFiles": [
      {
        "class": "File",
        "path": "keep:********************************6183/Homo_sapiens_assembly38.fasta.fai"
      }
    ]
    }
}
```

Then you can access them in following way:

```python
from arvados_cwl_tester import *

arvados_project_uuid(VARIABLES["akau"])

# using "VARIABLES" that is a dictionary
def test_single_step_variables():
    out = arvados_run(
      "./my_cwl.cwl",
      {
          "fastq_collection": VARIABLES["dirs"]["fastq_collection"],
          "reference_genome": VARIABLES["reference_genome"],
      }
    )

# or uppercase key names from VARIABLES like:
def test_single_step_key_names():
    out = arvados_run(
      "./my_cwl.cwl",
      {
          "fastq_collection": DIRS["fastq_collection"],
          "reference_genome": REFERENCE_GENOME,
          "gene_panel": GENE_PANEL
      }
    )

```

## Development of the library

To activate development environment:

```bash
bash setup.sh
source venv/bin/activate

```


