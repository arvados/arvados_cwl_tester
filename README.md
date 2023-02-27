# Arvados CWL Tester
## Framework for testing Common Workflow Language on Arvados

![Beta](https://img.shields.io/badge/Status-Beta-yellow)

The **Arvados CWL Tester** is an open-source testing framework that lets you write and manage reproducible e2e CWL tests in Python and execute on Arvados. Arvados is an open source platform for managing and processing large biomedical data (more information you can find [here](https://arvados.org/)).
The framework supports parallel execution of multiple e2e tests using pytest. 

## Introduction

**Arvados CWL Tester** API allows to write tests using python code and organize them in python script. 

Every test runs process on Arvados in temporary subproject which will be removed after one week automatically. When you execute first test during specific day new project is created authomaticly and all tests executed during this day will be placed there. That will keep your testing space clean and tidy. 

## Installation


```
git clone git@github.com:arvados/arvados_cwl_tester.git
cd arvados_cwl_tester
pip install .
```

## Write your first test

Define all tests you need in `test_<your_name>.py` file. Here you can see an example how this file can look like:

```python
from arvados_cwl_tester import *

# Set global variable with project uuid where all your tests will be executed:
arvados_project_uuid("pirca-*******************82")

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
    assert result.command == ["touch", "example.txt"]

```

## Execute the test

Run in command line:

```bash
$ pytest -k single_step
```

Run multiple tests in parallel - it will execute your tests as separated processes on arvados and you will save time: 

```bash
$ pytest --workers 10 --tests-per-worker auto
```

## Variables

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

## Playground

[Arvados CWL Tester Playground](https://github.com/monigenomi/arvados-cwl-tester-playground) is a sample project to help you learn how to use **Arvados CWL Tester**. You can use this project as a starting point to create your own tests for your own CWL workflows. 

## Contributing

We welcome contributions to the Arvados CWL Tester project! If you find any issues or have suggestions for improvements please create a new issue or pull request. 


To activate development environment run a command:
```bash
$ bash setup.sh
$ source venv/bin/activate
```

## Authors

**Monika Krzyzanowska** [monigenomi](https://github.com/monigenomi), e-mail: monigenomi@gmail.com
**Joana Butkiewicz** [joanna-butkiewicz]https://github.com/joanna-butkiewicz

## Licensing

This project is licensed under Apache 2.0
