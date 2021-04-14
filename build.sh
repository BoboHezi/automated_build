#!/usr/bin/env bash

build_project=$1
build_variant=$2
build_action=$3
if [ "$4" == "true" ]; then
    is_sign="-s";
fi
if [[ "$5" == "true" || "$build_variant" == "ota" ]]; then
    is_verity="true";
fi
if [[ "$6" == "true" && "$build_variant" != "ota" ]]; then
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

# status: init(1)
if [ $is_test != "true" ]; then
    python notify_status.py $devops_compile_id 1
fi

# pre-check
# check params
if [ -z "$build_project" ] || [ -z "$build_variant" ] || [ -z "$build_action" ] ; then
    echo -e "\nThere is a problem with the incoming parameters, please check\n"
    # status: check_fail(2)
    if [ $is_test != "true" ]; then
        python notify_status.py $devops_compile_id 2
    fi
    exit 2;
fi

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

echo -e "\n---------------------sync---------------------\n"
# sync code
if [[ "$is_test" != "true" && "$build_action" != "r" ]]; then
    repo sync
fi

echo -e "\n---------------------find---------------------\n"
# find project
find=$(find droi/ -maxdepth 3 -mindepth 3 -type d -name $build_project)

if [ ! $find ]; then
    # status: project_notfound(3)
    if [ $is_test != "true" ]; then
        python notify_status.py $devops_compile_id 3
    fi
    echo -e "\n$build_project not found\n"
    exit 3
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
if [ $is_test != "true" ]; then
    echo "overview"
    echo --------------------------------------------------------------------------
    repo overview
    echo --------------------------------------------------------------------------
    echo ""
else
    echo -e "\nrepo overview\n"
fi

# database option
# status: compiling(4)
if [ $is_test != "true" ]; then
    python notify_status.py $devops_compile_id 4
fi
# table devops_server server status
if [ $is_test != "true" ]; then
    python update_db.py -t devops_server -k server_status -v 1 -w id -e $devops_host_id
fi
# table devops_compile infos
job_name=`echo $build_url | awk -F"/" '{print $5}'`
build_id=`echo $build_url | awk -F"/" '{print $6}'`
build_time=`date "+%Y-%m-%d %H:%M:%S"`
if [ $is_test != "true" ]; then
    python update_db.py -t devops_compile \
        -k compile_jenkins_job_name,compile_jenkins_job_id,compile_log_url,compile_server_ip,compile_build_time \
        -v "$job_name","$build_id","$build_url/consoleText","$host_ip","$build_time" \
        -w id -e $devops_compile_id
fi

echo -e "\n---------------------build---------------------\n"
# echo build script
echo -e "\nmk -f -$build_variant $is_sign $build_project $build_action\n"
# build
if [ $is_test == "true" ]; then
    ./test_script.sh ; build_rst=$?
else
    ./mk -f -$build_variant $is_sign $build_project $build_action ; build_rst=$?
fi

# build result
if test $build_rst = "0"; then
    # status: build_success(0)
    if [ $is_test != "true" ]; then
        python notify_status.py $devops_compile_id 0
    fi
    echo -e "\nbuild success\n"
else
    # status: build_failed(5)
    if [ $is_test != "true" ]; then
        python notify_status.py $devops_compile_id 5
    fi
    echo -e "\nbuild failed\n"
    exit 5
fi

# database option
# table devops_server server status
if [ $is_test != "true" ]; then
    python update_db.py -t devops_server -k server_status -v 0 -w id -e $devops_host_id
fi
# table devops_compile infos
build_finish_time=`date "+%Y-%m-%d %H:%M:%S"`
if [ $is_test != "true" ]; then
    python update_db.py -t devops_compile \
        -k compile_build_finish_time -v "$build_finish_time" \
        -w id -e $devops_compile_id
fi

echo -e "\n---------------------publish---------------------\n"
# publish
if [ "$is_publish" == "true" ]; then
    echo -e "\npublish\n"
    ./publish
fi
