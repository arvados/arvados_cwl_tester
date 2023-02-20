# Framework for testing Common Workflow Language on Arvados - arvados_cwl_tester

Note: This is not the final, official version

Thank you for interest in arvados-cwl-tester framework. Please note that the current version is not the final, official version. While the frameworkk is usable , the work is still in progress. The official version will be released soon. 

## Introduction

**arvados_cwl_tester** framework is dedicated to people, that develop pipelines in CWL and run them on Arvados. It allows to create easy and reproducible tests for CWL CommandLineTools and Workflows and run them in parallel on Arvados, using `pytest`.

**arvados_cwl_tester** API allows to write tests using python code and organize them in python script. 

Every test runs process on Arvados in temporary subproject, that will be removed after some time automaticly that that will keep your testing space clean and tidy. 

## Installation

### Setup environment

```
pip install arvados_cwl_tester
```

### Write your first test

Define all tests you need in `test_<your_name>.py` file. Here you can see an example how this file can look like:

```python
from arvados_cwl_tester import *

def test_single_step():
    result = arvados_run(
        UUID["ardev"],
        "./components/single_step/single_step.cwl",
        {
            "name": "example.txt"
        }
    )
    assert "example.txt" in result.files
    assert result.files["example.txt"]["size"] == 0
```

### Execute the test

Run in commandline:

```bash
pytest -k single_step
```

### Variables

You can create `./test/variables.json` file which will be used by arvados_cwl_tester to create global variables with matching names. You are free to name and organize your variables in any way you like. For example you can store project uuids, file, and directory handles, as so:

For example::
```json
{
  "projects": {
    "ardev": "ardev-*******************81",
    "arind": "arind-*******************92",
    "arkau": "arkau-*******************82"
  },
  "dirs": {
    "fastq_collection": "keep:********************************6185"
  },
  "files": {
    "reference_genome": "keep:********************************6184/Homo_sapiens_assembly38.fasta",
    "reference_genome_secondary": "keep:********************************6183/Homo_sapiens_assembly38.fasta.fai",
    "intervals": "keep:********************************6182/wgs_calling_regions.hg38.bed",
    "small_vcf": "./testing_data/small.vcf"
  }
}
```

Then you can access them in following way:

```python
from arvados_cwl_tester import *

def test_single_step():
    out = arvados_run(
      PROJECTS["akau"],
      "./my_cwl.cwl",
      {
          "fastq_collection": arvados_dir(DIRS["fastq_collection"]),
          "intervals": arvados_file(FILES["intervals"]),
          "reference_genome": arvados_file(FILES["reference_genome"], FILES["reference_genome_secondary"])
      }
    )

```

### How to execute tests in parallel


Run multiple tests in parallel - it will execute your tests as separated processes on arvados and you will save time. 

```

## Development of the library

To activate development environment:

```bash
bash setup.sh
source venv/bin/activate

```

