cwlVersion: v1.0
class: Workflow
doc: some documentation
label: Example pipeline
hints:
  DockerRequirement:
    dockerPull: ubuntu:20.04

inputs:
  name:
    type: string
    doc: Some description needed as obligatory in pipeline

steps:
  single_step:
    run: components/single_step/single_step.cwl
    in:
      name: name
    out: testing_result

outputs:
  testing_result:
    type: File
    outputSource: single_step/testing_result
