cwlVersion: v1.1
class: Workflow

hints:
  DockerRequirement:
    dockerPull: ubuntu:18.04
  MultipleInputFeatureRequirement: {}

inputs:
  name:
    type: string

steps:
  single_step_1:
    run: "./test_single_step/test_single_step.cwl"
    in:
      name: name
    out: [testing_result]
  
  single_step_2:
    run: "./test_single_step/test_single_step.cwl"
    in:
      name: name
    out: [testing_result]
  
  single_step_3:
    run: "./test_single_step/test_single_step.cwl"
    in:
      name: name
    out: [testing_result]

outputs:
  testing_result:
    type: File[]
    outputSource: [single_step_1/testing_result, single_step_2/testing_result, single_step_3/testing_result]