#!/usr/bin/python


def check_if_file_exists(path) -> bool:
    exist = os.path.isfile(path)
    if exist:
        print(colors.OKGREEN + f"File {path} exists.")
        return exist
    print(colors.ERROR + f"File {path} does not exist. List of files:")
    for file in glob.glob(os.path.dirname(path) + "/*"):
        print(" - " + os.path.basename(file))
    return exist


def check_file_does_not_exists(path) -> bool:
    return not os.path.isfile(path)


def check_file_is_not_empty(outdir, path) -> bool:
    file = os.path.join(outdir, path)
    if os.path.getsize(file) > 0:
        return True
    return False


def compare_result_with_expected(result_path, expected_path) -> bool:
    return filecmp.cmp(result_path, expected_path)


def check_files_in_out_dir(outdir: str, files: list) -> bool:
    # TODO does it check all list for sure?

    for file in files:
        assert check_if_file_exists(os.path.join(outdir, f"{file}")) == True
        # assert check_file_is_not_empty == True # TODO debug


def how_many_variants_in_vcf(outdir: str, filename: str):
    # TODO after setup py is completed lets do it by pysam
    # TODO implement gzipped files
    with open(os.path.join(outdir, filename), "r") as file:
        variants = 0
        for line in file:
            if not "#" in line[0]:
                variants += 1
    print(colors.OKBLUE + f"{filename} contains {variants} variants.")
    return variants
