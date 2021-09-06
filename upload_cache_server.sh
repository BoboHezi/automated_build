#!/usr/bin/env bash

function get_host_disks() {
    host=$1
    local user=$(echo $host | awk -F "," '{print $1}')
    local ip=$(echo $host | awk -F "," '{print $2}')
    local pwd=$(echo $host | awk -F "," '{print $3}')

    if [[ ! -n "$user" || ! -n "$ip" || ! -n "$pwd" ]]; then
        return
    fi
    # get host df info
    local df=$(sshpass -p "$pwd" ssh -o StrictHostKeyChecking=no "$user@$ip" 'df')
    local lines=($df)

    # dump disk info
    local first_flag=0
    local dks=()
    for line in ${lines[*]}; do
        if [ $first_flag == 0 ]; then
            first_flag=1
            continue
        fi
        total=$(echo $line | awk -F" " '{print $2}')
        if [[ $total -lt `expr 50 \* 1024 \* 1024` ]]; then
            continue
        fi
        free=$(echo $line | awk -F" " '{print $4}')
        path=$(echo $line | awk -F" " '{print $6}')
        dks=(${dks[@]} "$path" "$total" "$free")
    done
    echo "${dks[@]}"
}

function get_platform() {
    folder=$([ ! -n "$1" ] && echo $PWD || echo $1)
    local manifest_file="$folder""/.repo/manifest.xml"

    local PLATFORM=""
    if [[ -L "$manifest_file" ]]; then
        # relative path
        source=$(ls -l $manifest_file | awk '{print $NF}')
        # absolute path
        # source=$(realpath $manifest_file)
        echo $source | grep SPRD > /dev/null 2>&1 && PLATFORM="SPRD"
        [ "$PLATFORM" = "" ] && echo $source | grep ALPS > /dev/null 2>&1 && PLATFORM="MTK"
    elif [[ -f $manifest_file ]]; then
        grep SPRD .repo/manifest.xml > /dev/null 2>&1 && PLATFORM="SPRD"
        [ "$PLATFORM" = "" ] && grep ALPS .repo/manifest.xml > /dev/null 2>&1 && PLATFORM="MTK"
    fi
    [ "$PLATFORM" = "" ] && [ -d $folder"/vendor/sprd" ] && PLATFORM="SPRD"
    [ "$PLATFORM" = "" ] && [ -d $folder"/vendor/mediatek" ] && PLATFORM="MTK"
    [ "$PLATFORM" = "" ] && echo "UNKNOWN" || echo "$PLATFORM"
}

function get_project() {
    BUILD_INFO_FILE=$1

    local PRODUCT=$(get_config_val ${BUILD_INFO_FILE} 'product')
    [ ! -n "$PRODUCT" ] && PRODUCT=$(get_config_val ${BUILD_INFO_FILE} 'project')
    local PROJECT=$(get_project_section 'PROJECT' $PRODUCT)
    echo "$PROJECT"
}

function get_unsigned_publish_file() {
    BUILD_INFO_FILE=$1
    PLATFORM=$2

    local PROJECT=$(get_project $BUILD_INFO_FILE)
    local SW_VERNO=$(get_config_val $BUILD_INFO_FILE 'FREEME_PRODUCT_INFO_SW_VERNO')
    local SW_VERNO_INTERNAL=$(get_config_val $BUILD_INFO_FILE 'FREEME_PRODUCT_INFO_SW_VERNO_INTERNAL')
    # echo -e "PROJECT: $PROJECT\nSW_VERNO: $SW_VERNO\nSW_VERNO_INTERNAL: $SW_VERNO_INTERNAL\n"

    if [[ $PLATFORM == "MTK" ]]; then
        target=$(get_project_info 'PUBLISH' 'TARGET')
        target=${target}/${PROJECT}
        # echo "target: $target"
        if [[ -z "${SW_VERNO_INTERNAL}" || "${SW_VERNO}" == "${SW_VERNO_INTERNAL}" ]] ; then
            name="${SW_VERNO}"
        else
            name="${SW_VERNO}(${SW_VERNO_INTERNAL})"
        fi
        name=($name)
        name=${name}.zip
        echo "${target}/${name}"
    elif [[ $PLATFORM == "SPRD" ]]; then
        pac_out=droi/out/$PROJECT
        pac_name=$SW_VERNO_INTERNAL.pac
        pac_name=($pac_name)
        echo "$pac_out/$pac_name"
    fi

}

function check_install() {
    program=$1
    password=$2

    if ! type $program >/dev/null 2>&1; then
        echo -e "\nupload_cache_server install $program"

        if type apt-get >/dev/null 2>&1; then
            sudo -S apt-get update >/dev/null 2>&1 << EOF
$password
EOF
            sudo -S apt-get install $program -y << EOF
$password
EOF
        elif type yum >/dev/null 2>&1; then
            yum install $program -y
        fi
    fi
}

my_password=$1
devops_compile_id=$2
jenkins_build_number=$3
build_sign=$4
sign_ftp_url=$5
sign_ftp_upload_username=$6
sign_ftp_upload_passwd=$7

ID_STAMP="${devops_compile_id}_${jenkins_build_number}"
MY_INET_ADDR=$(ip a | grep "\(192.168\)\|\(10.20\)" | awk '{print $2}' | awk -F/ '{print $1}')

# check paramter
if [[ ! -n "$my_password" || ! -n "$devops_compile_id" || ! -n "$jenkins_build_number" ]]; then
    echo -e "wrong paramter, exit."
    exit 1
fi

# find jenkins script path
SCRIPT_BASE=$(ls -l upload_cache_server.sh | awk '{print $NF}')
SCRIPT_BASE=${SCRIPT_BASE%/*}

# define avalible cache hosts
CACHE_HOSTS=($(python3 -c """
import os;
os.chdir('$SCRIPT_BASE');
import utils;
print(str(utils.CACHE_HOSTS).replace('\'','').replace(', ', ' ').replace('(', '').replace(')', ''));
"""
))

# define cache path name in remote
REMOTE_CACHE_FOLDER="jenkins_cache"

source build/envsetup.sh > /dev/null 2>&1

# dump platform
PLATFORM=$(get_platform)
echo -n "upload_cache_server PLATFORM: $PLATFORM"
if [[ ! -n "$PLATFORM" || ! -n "$PLATFORM" ]]; then
    echo -e " error, exit."
    exit 2
fi
echo -e "\n"

# create cache folder cache_$devops_compile_id_$jenkins_build_number_$time_stamp
# time_stamp=$(date '+%y-%m-%d-%H-%M')
time_stamp=`date -d "$(date '+%y-%m-%d %H:%M:%S')" +%s`
cache_base=cache_"$ID_STAMP"_$time_stamp
cache_folder="$SCRIPT_BASE"/"$cache_base"
echo -e "upload_cache_server cache_folder: $cache_folder"
mkdir $cache_folder

# cp manifest.xml file with tag to $cache_folder
manifest_tag_file="$SCRIPT_BASE"/tag_"$ID_STAMP".xml
echo -e "\nupload_cache_server manifest_tag_file: $manifest_tag_file"
if [[ ! -f $manifest_tag_file ]]; then
    repo manifest -r -o $manifest_tag_file
fi
mv $manifest_tag_file $cache_folder

# create ProjectConfig.mk & copy to $cache_folder
build_info_file=$(grep "readonly BUILD_INFO_FILE" mk | awk -F"=" '{print $2}')
build_info_file=${build_info_file//\'/}
project_name=$(get_project $build_info_file)
project_path=$(find droi/ -maxdepth 3 -mindepth 3 -type d -name $project_name)
build_utils="vendor/freeme/build/tools/build_utils.py"
merged_config="$cache_folder/ProjectConfig.mk"
if [[ -f "$project_path/ProjectConfig.mk" && -f "$build_utils" ]]; then
    echo -e "\nupload_cache_server merge $merged_config"
    python $build_utils "merge-config" "$project_path/ProjectConfig.mk" > "$merged_config"
fi

# copy vmlinux to $cache_folder
vmlinux_file="out/target/product/$project_name/obj/KERNEL/vmlinux"
if [[ ! -f $vmlinux_file ]]; then
    vmlinux_file=$(find out/ -type f -name vmlinux)
fi
if [[ -f $vmlinux_file ]]; then
    echo -e "\nupload_cache_server copy $vmlinux_file"
    zip -j -q $cache_folder/vmlinux.zip $vmlinux_file
    # cp $vmlinux_file $cache_folder
fi

# copy publish file to $cache_folder
if [[ "$build_sign" != "true" ]]; then
    echo -e "\nupload_cache_server build_info_file: $build_info_file"
    if [[ -n "$build_info_file" && -f $build_info_file ]]; then
        # find unsigned publish file
        publish_file=$(get_unsigned_publish_file $build_info_file $PLATFORM)

        if [[ -n "$publish_file" && -f $publish_file ]]; then
            echo -e "\nupload_cache_server publish_file: $publish_file"
            if [[ ${publish_file##*.} == "pac" ]]; then
                zip_name=${publish_file##*/}
                zip_name=${zip_name/.pac/.zip}
                zip -j -q $cache_folder/$zip_name $publish_file # -m
            else
                cp $publish_file $cache_folder
            fi
            rm -rf droi/out/$project_name
        fi
    fi
fi

# check & install sshpass
check_install "sshpass" "$my_password"

# define cache location, default local
cache_location=$(whoami)@${MY_INET_ADDR}:${cache_folder}

# collecting folder size
cache_size=$(du $cache_folder | awk '{print $1}')
echo -e "\nupload_cache_server cache_size: $cache_size"

# scp to cache host
if type sshpass >/dev/null 2>&1; then
    # define host:disk map
    declare -A avalible_disks
    OLD_IFS="$IFS"
    IFS=$'\n'
    for (( i = 0; i < ${#CACHE_HOSTS[*]}; i++ )); do
        host=${CACHE_HOSTS[$i]}

        dks=$(get_host_disks $host)
        # echo -e "$i disk info: ${dks[@]}\n"
        avalible_disks[$i]=${dks[@]}
    done
    IFS="$OLD_IFS"

    # get cache host for this time
    declare -A max_free_space=0
    declare -A max_free_path
    declare -A max_free_space_host=-1
    for host_index in ${!avalible_disks[@]}; do
        disks=(${avalible_disks[$host_index]})
        for (( i = 2; i < ${#disks[@]}; i+=3 )); do
            if [ ${disks[$i]} -gt $max_free_space ]; then
                max_free_space=${disks[$i]}
                max_free_path=${disks[$i - 2]}
                max_free_space_host=$host_index
            fi
        done
    done
    user=$(echo ${CACHE_HOSTS[$max_free_space_host]} | awk -F "," '{print $1}')
    ip=$(echo ${CACHE_HOSTS[$max_free_space_host]} | awk -F "," '{print $2}')
    pwd=$(echo ${CACHE_HOSTS[$max_free_space_host]} | awk -F "," '{print $3}')
    path=$max_free_path

    # if free space is 300M greater than required
    if [[ $max_free_space -gt `expr $cache_size + 300 \* 1024` ]]; then
        # change to home if necessary
        if [ ${path} = "/" ]; then
            path="~"
        fi

        echo -e "\nupload_cache_server ${user}@${ip}:${path}"

        # mkdir in remote
        sshpass -p "${pwd}" ssh -o StrictHostKeyChecking=no "${user}@${ip}" """
        cd ${path}
        echo -e "now in ${ip}"

        pwd

        if [ ! -d ${REMOTE_CACHE_FOLDER} ]; then
            sudo -S mkdir ${REMOTE_CACHE_FOLDER} << EOF
${pwd}
EOF
            sudo -S chmod -R a+rw ${REMOTE_CACHE_FOLDER} << EOF
${pwd}
EOF
        fi
        """
        # scp to remote
        sshpass -p "${pwd}" scp -r ${cache_folder} "${user}@${ip}":${path}/${REMOTE_CACHE_FOLDER}

        cache_location="${user}@${ip}":${path}/${REMOTE_CACHE_FOLDER}/${cache_base}

        rm -rf $cache_folder
    fi
fi

echo -e "\nupload_cache_server cache_location: $cache_location\n\n"

echo -e '\n./upload_ftp.py -p "$project_name" -h "$sign_ftp_url" -u "$sign_ftp_upload_username" -c "$sign_ftp_upload_passwd"\n'
python3 upload_ftp.py -p "$project_name" -h "$sign_ftp_url" -u "$sign_ftp_upload_username" -c "$sign_ftp_upload_passwd"

exit 0

