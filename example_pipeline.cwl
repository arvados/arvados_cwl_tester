cwlVersion: v1.0
class: Workflow

hints:
  DockerRequirement:
    dockerPull: ubuntu:20.04

inputs:
  name:
    type: string

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
