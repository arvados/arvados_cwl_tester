cwlVersion: v1.1
class: CommandLineTool

hints:
  DockerRequirement:
    dockerPull: ubuntu:18.04

baseCommand: [touch]

inputs:
  name:
    type: string
    inputBinding:
      position: 0

outputs:
  testing_result:
    type: File
    outputBinding:
      glob: $(inputs.name)