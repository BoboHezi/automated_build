#!/usr/bin/env bash

project_name=$1
sv_platform_url=$2
sv_platform_username=$3
sv_platform_passwd=$4
sv_platform_terrace=$5
sv_platform_board=$6
sv_platform_cclist=$7
sv_platform_model=$8
sv_platform_brand=$9
sv_platform_odm=${10}
publish_username=${11}
build_verity=${12}

if [ -f ftp_url.txt ]; then
    ftp_url=$(cat ftp_url.txt)
    echo -e "\nftp_url: $ftp_url\n"

    argv="-p '$project_name' -f '$ftp_url' -u '$sv_platform_url' \
    -s '$sv_platform_username' -c '$sv_platform_passwd' \
    -t '$sv_platform_terrace' -b '$sv_platform_board' \
    -l '$sv_platform_cclist' -m '$sv_platform_model' \
    -r '$sv_platform_brand' -o '$sv_platform_odm' \
    -i '$publish_username'"

    if [ "$build_verity" == "true" ]; then
        argv="$argv -v"
    fi

    echo -e "\n./commit_sign_verify.py $argv\n"
    echo $argv | python -c "import os, sys; os.system('./commit_sign_verify.py %s' % sys.stdin.readline())"
else
    echo -e "\nftp_url.txt not exist!\n"
    exit 1
fi