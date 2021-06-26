#!/usr/bin/env bash

function random_range {
   shuf -i $1-$2 -n1
}

function Listening {
   TCPListeningnum=`netstat -an | grep ":$1 " | awk '$1 == "tcp" && $NF == "LISTEN" {print $0}' | wc -l`
   UDPListeningnum=`netstat -an | grep ":$1 " | awk '$1 == "udp" && $NF == "0.0.0.0:*" {print $0}' | wc -l`
   (( Listeningnum = TCPListeningnum + UDPListeningnum ))
   if [ $Listeningnum == 0 ]; then
       echo "0"
   else
       echo "1"
   fi
}

function get_random_port {
   PORT=0
   while [[ $PORT == 0 ]]; do
       temp1=`random_range $1 $2`
       if [ `Listening $temp1` == 0 ] ; then
              PORT=$temp1
       fi
   done
   echo "$PORT"
}

# argv_str=$*
# argv=(${argv_str//,/ })
# code_dir=${argv[0]}

code_dir=$1
stop_terminal=$2
ttyd_file=$3
id=$4
ip=$5
url='http://192.168.48.105:8080/jeecg-boot/server/devopsServer/jenkinsRequestServer'

echo -e "\n*******web terminal*******\n"

echo "code_dir      : $code_dir"
echo "stop_terminal : $stop_terminal"
echo "ttyd_file     : $ttyd_file"
echo "id            : $id"
echo "ip            : $ip"
echo "url           : $url"
echo "token         : $DEVOPS_TOKEN"

# kill ttyd
ttyd_pid=$(ps -ef | grep ttyd | grep -v 'grep' | grep -v 'web_terminal' | awk '{print $2}')
echo -e "\nttyd pid: $ttyd_pid"
if [[ $ttyd_pid -gt 0 ]]; then
    echo -e "\nkill -9 $ttyd_pid"
    kill -9 $ttyd_pid
fi

status=1

# just kill
if [[ "$stop_terminal" == "true" ]]; then
    full_url=$url"?id=$id&status=$status&ServerDir="
    echo "full_url: $full_url"
    curl -H X-Access-Token:"$DEVOPS_TOKEN" -X GET $full_url
    exit 0
fi

# cd code_dir if exist
if [ -d $code_dir ]; then
    cd $code_dir
fi

# find ttyd
if [ ! -f $ttyd_file ]; then
    echo "$ttyd_file not exist!"
    exit 1
fi

# random port
ttyd_port=$(get_random_port 1000 65535)

echo '------------start tydd------------'
echo "$ttyd_file -p $ttyd_port -m 2 bash &"
$ttyd_file -p $ttyd_port -m 2 bash &

sleep 5s

ttyd_pid=$(ps -ef | grep ttyd | grep -v 'grep' | grep -v 'web_terminal' | awk '{print $2}')
echo -e "pid: $ttyd_pid"
status=$([[ $ttyd_pid -gt 0 ]] && echo 0 || echo 5)

ServerDir=$([[ $status == 0 ]] && echo "http://$ip:$ttyd_port" || echo "")
full_url=$url"?id=$id&status=$status&ServerDir=$ServerDir"
echo "full_url: $full_url"
curl -H X-Access-Token:"$DEVOPS_TOKEN" -X GET $full_url

exit 0
