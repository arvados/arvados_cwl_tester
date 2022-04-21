from cProfile import run
from tools import *


# Define inputs

resources = "./test/data/resources"
reference_genome = "./test/data/resources/Homo_sapiens_assembly38.fasta"

reference_genome = {
    "class": "File",
    "path": reference_genome
}

# Run tests 

def test_generate_shards():
    output_dir = run_cwl("./components/joint_genotyping/generate_shards/generate_shards.cwl", {
        "reference_genome": reference_genome,
        "dirs_with_gvcfs": [
            {
                "class": "Directory",
                "path": os.path.join(resources, "reads/")
            },
            {
                "class": "Directory",
                "path": os.path.join(resources, "reads_2/")
            }
        ],
    })
    
    check_file_is_not_empty(output_dir, "shard_1")
    

def test_VarCal_apply():
    outputs = run_cwl(
        "./components/joint_genotyping/VarCal_apply/VarCal_apply.cwl",
        {
          "vcf": {"class": "File", "path": "./test/data/vcf/2000.vcf"},

          "SNP_tranches_file_csv": {"class": "File", "path": "./test/data/csv/testing_varcal_SNP_tranches.csv"},
          "SNP_recalibrated_vcf": {"class": "File", "path": "./test/data/vcf/testing_varcal_SNP_recalibrated.vcf"},

          "INDEL_tranches_file_csv": {"class": "File", "path": "./test/data/csv/testing_varcal_INDEL_tranches.csv"},
          "INDEL_recalibrated_vcf": {"class": "File", "path": "./test/data/vcf/testing_varcal_INDEL_recalibrated.vcf"},

          "reference_genome": reference_genome,
          "output_name": "test"

        }
    )
    assert check_file_is_not_empty(outputs, "test_recalibrated_applied.vcf")
    assert how_many_variants_in_vcf(outputs, "test_recalibrated_applied.vcf") == 1604



