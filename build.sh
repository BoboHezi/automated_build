#!/usr/bin/env bash

build_project=$1
build_variant=$2
build_action=$3
if [ "$4" == "true" ]; then
    is_sign="-s";
fi
if [[ "$5" == "true" || "$build_action" == "ota" ]]; then
    is_verity="true";
fi
if [[ "$6" == "true" && "$build_action" != "ota" ]]; then
    is_publish="true";
fi
devops_host_id=$7
devops_compile_id=$8
is_new_project=$9
is_test=${10}
build_url=${11}
host_ip=${12}

function printParams() {
    echo ""
    echo --------------------------------------------------------------------------
    echo "Compilation parameters: " 
    echo "build project: $build_project" 
    echo "build variant: $build_variant" 
    echo "build action: $build_action" 
    echo "is sign: $is_sign" 
    echo "is verity: $is_verity" 
    echo "is publish: $is_publish" 
    echo "devops host id: $devops_host_id" 
    echo "devops compile id: $devops_compile_id" 
    echo "build_url: $build_url" 
    echo "host_ip: $host_ip" 
    echo "is new project: $is_new_project" 
    echo "is test: $is_test" 
    echo --------------------------------------------------------------------------
    echo ""
}

function printRed() {
    echo -e "\033[31$1\033[0m"
}

function printGreen() {
    echo -e "\033[32$1\033[0m"
}

function printYellow() {
    echo -e "\033[33$1\033[0m"
}

function printBlue() {
    echo -e "\033[34$1\033[0m"
}

printParams

# status: repo_processing(12)
python3 notify_status.py $devops_compile_id repo_processing

# pre-check
# check params
if [ -z "$build_project" ] || [ -z "$build_variant" ] || [ -z "$build_action" ] ; then
    echo -e "\nThere is a problem with the incoming parameters, please check\n"
    # status: check_fail(3)
    # python3 notify_status.py $devops_compile_id check_fail
    exit 3;
fi

# table devops_server server status
python3 update_db.py -t devops_server -k server_status -v 1 -w id -e $devops_host_id

# table devops_compile infos
job_name=`echo $build_url | awk -F"/" '{print $5}'`
build_id=`echo $build_url | awk -F"/" '{print $6}'`
python3 update_db.py -t devops_compile \
    -k compile_jenkins_job_name,compile_jenkins_job_id,compile_log_url,compile_server_ip \
    -v "$job_name","$build_id","$build_url""console","$host_ip" \
    -w id -e $devops_compile_id

echo -e "\n---------------------source---------------------\n"
# pre-build
. build/envsetup.sh

echo -e "\n---------------------clean---------------------\n"
# clean
case $build_action in
    n|ota)
        echo -e "\nclean repo first\n"
        if [ "$is_test" != "true" ]; then
            repoclean -a
        else
            echo -e "\nrepoclean -a\n"
        fi
        ;;
esac

echo -e "\n---------------------repo handler---------------------\n"
repo start --all master
# 'clean code'
if [[ "$is_test" != "true" && "$build_action" != "r" ]]; then
    python3 repo_handler.py -c
    # repo sync
fi

echo -e "\n---------------------cherry pick---------------------\n"
# cherry pick
python3 repo_handler.py -p ~/.jenkins/script/cps ; cp_rst=$?
if test $cp_rst != "0"; then
    echo -e "\ncherry-pick failed, exit\n"
    # status: cp_failed failed(9)
    # python3 notify_status.py $devops_compile_id cp_failed
    exit 9
else
    echo -e "\ncherry-pick success\n"
fi

echo -e "\n---------------------find---------------------\n"
# find project
find=$(find droi/ -maxdepth 3 -mindepth 3 -type d -name $build_project)

if [ ! $find ]; then
    # status: project_not_found(4)
    # python3 notify_status.py $devops_compile_id project_not_found
    echo -e "\n$build_project not found\n"
    exit 4
else
    if [ "$is_new_project" == "true" ]; then
        echo "return new_project found"
        # INSERT INTO `jeecg-boot242`.`devops_project` (`project_name`, `project_code_id`) VALUES ('g2030upt_q6506gk_hlt', '71P');

        # (is_new_project ) :  return new_project found
    fi
    echo -e "\n$build_project found\n"
fi

echo -e "\n---------------------overview---------------------\n"
# just overview
repo info -o
echo ""

# database option
# status: compiling(5)
python3 notify_status.py $devops_compile_id compiling

build_time=`date "+%Y-%m-%d %H:%M:%S"`
python3 update_db.py -t devops_compile \
    -k compile_build_time -v "$build_time" \
    -w id -e $devops_compile_id

echo -e "\n---------------------build---------------------\n"
# echo build script
echo -e "\nmk -f -$build_variant $is_sign $build_project $build_action\n"
# build
if [ $is_test == "true" ]; then
    ./test_script.sh ; build_rst=$?
else
    ./mk -f -$build_variant $is_sign $build_project $build_action ; build_rst=$?
    # ./test_script.sh ; build_rst=$?
fi

# publish
if [[ $is_test != "true" && "$is_publish" == "true" && "$build_action" != "ota" && $build_rst = "0" ]]; then
    echo -e "\n---------------------publish---------------------\n"
    ./publish
fi

# database option
# table devops_server server status
# python3 update_db.py -t devops_server -k server_status -v 0 -w id -e $devops_host_id

# table devops_compile infos
# build_finish_time=`date "+%Y-%m-%d %H:%M:%S"`
# python3 update_db.py -t devops_compile \
#     -k compile_build_finish_time -v "$build_finish_time" \
#     -w id -e $devops_compile_id

# build result
if test $build_rst = "0"; then
    # status: build_success(0)
    # python3 notify_status.py $devops_compile_id success
    echo -e "\nbuild success\n"
else
    # status: build_failed(6)
    # python3 notify_status.py $devops_compile_id build_failed
    echo -e "\nbuild failed\n"
    exit 6
fi
