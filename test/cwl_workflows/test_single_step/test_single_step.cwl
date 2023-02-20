cwlVersion: v1.2
class: CommandLineTool

hints:
  DockerRequirement:
    dockerPull: ubuntu:18.04
  InlineJavascriptRequirement: {}


inputs:
  name:
    type: string
    inputBinding:
      position: 0

baseCommand: [touch]

arguments:
  - valueFrom: $(inputs.name).txt

outputs:
  testing_result:
    type: File
    outputBinding:
      glob: "*.txt"

