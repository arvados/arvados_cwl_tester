cwlVersion: v1.2
class: CommandLineTool

hints:
  DockerRequirement:
    dockerPull: ubuntu:18.04
  InlineJavascriptRequirement: {}


inputs:
  file:
    type: File

baseCommand: [cat]
arguments: [$(inputs.file)]

outputs:
  an_output_name:
    type: stdout

stdout: a_stdout_file

