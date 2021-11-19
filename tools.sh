#!/usr/bin/env bash

set -eo pipefail

buidinging_not_existing_image() {
    name_tag=$1
    sub_dir=$2
    if [[ "$(docker images -q ${name_tag} 2> /dev/null)" == "" ]]; then
        echo "Buidling ${name_tag}"
        docker build -t ${name_tag} ${PROJECT_DIR}/docker/${sub_dir}
    fi
}

run_cwl () {
    [ -e $OUTPUT ] && rm -rf $OUTPUT
    dt=$(date '+%d.%m.%Y_%H.%M.%S')
    OUTPUT=/tmp/${dt}/
    mkdir -p $OUTPUT
    cwl_path=$1
    printf "\033[1;36mRUNNING COMPONENT ${cwl_path}... \n"
    printf "\033[1;36m OUTPUTS: ${OUTPUT}\n"
    cwl-runner --js-console --move-outputs --basedir /tmp --outdir $OUTPUT \
        ${PROJECT_DIR}/${cwl_path} \
        .input.yml
    tree $OUTPUT
}

check_file_exists() {
    if [ ! -f "$OUTPUT/$1" ]; then
        printf "ERROR: \033[1;31mFile $1 not found! \n"
        exit 1
    fi
    printf "\033[1;32mFile $OUTPUT/$1 exists! \n"
}

check_file_not_exists() {
    if [  -f "$OUTPUT/$1" ]; then
        printf "ERROR: \033[1;31mFile $1 found! \n"
        exit 1
    fi
    printf "\033[1;32mFile $OUTPUT/$1 does not exists! \n"
}

difference() {
    diff "$OUTPUT/$1" $2 > /tmp/difference.txt
    if [ -s /tmp/difference.txt ]; then
        printf "ERROR: \033[1;31mFile $1 is not as expected\n"
        rm -f /tmp/difference.txt
        exit 1
    fi
    printf "\033[1;32mFile $OUTPUT/$1 is as expected! \n"
}
