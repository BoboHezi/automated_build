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
python notify_status.py $devops_compile_id 1

# pre-check
# check params
if [ -z "$build_project" ] || [ -z "$build_variant" ] || [ -z "$build_action" ] ; then
    echo -e "\nThere is a problem with the incoming parameters, please check\n"
    # status: check_fail(2)
    python notify_status.py $devops_compile_id 2
    exit 2;
fi

# pre-build
if [ "$is_test" != "true" ]; then
    . build/envsetup.sh
else
    echo -e "\nsource build/envsetup.sh\n"
fi

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

# sync code
if [[ "$is_test" != "true" && "$build_action" != "r" ]]; then
    repo sync
fi

# find project
find=$(find droi/ -maxdepth 3 -mindepth 3 -type d -name $build_project)

if [ ! $find ]; then
    # status: project_notfound(3)
    python notify_status.py $devops_compile_id 3
    echo -e "\n$build_project not found\n"
    exit 3
else
    if [ "$is_new_project" == "true" ]; then
        echo "return new_project found"
        # (is_new_project ) :  return new_project found
    fi
    echo -e "\n$build_project found\n"
fi

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

# echo build info
echo -e "\nmk -f -$build_variant $is_sign $build_project $build_action\n"

# build
# status: compiling(4)
python notify_status.py $devops_compile_id 4
# return jenkins_id & status by devops_host_id devops_compile_id
if [ $is_test == "true" ]; then
    ./test_script.sh ; build_rst=$?
else
    ./mk -f -$build_variant $is_sign $build_project $build_action ; build_rst=$?
fi

if test $build_rst = "0"
then
    # status: build_success(0)
    python notify_status.py $devops_compile_id 0
    echo -e "\nbuild success\n"
else
    # status: build_failed(5)
    python notify_status.py $devops_compile_id 5
    echo -e "\nbuild failed\n"
    exit 5
fi

