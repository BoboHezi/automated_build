
## 安装
[server & client]
```shell
sudo apt-get install distcc python-dev libiberty-dev
```

[client]
```shell
sudo apt-get install distccmon-gnome
```

## 配置
[server]
```shell
sudo subl /etc/default/distcc
```
```
STARTDISTCC="true"            //这项允许distccd启动
ALLOWEDNETS="192.168.0.0/16"  //这项指出里允许那些IP的distcc连接上来
LISTENER="192.168.16.183"     //这项应该填本机的IP地址，即需要监听的IP地址
ZEROCONF="false"              //这项指出不开启zeroconf
JOBS="10"                     //同时可承担的编译任务数目，一般设置为CPU个数+2
```

[server]
```shell
cp -rf [repo_path]/prebuilts /opt/
```

[client]
```shell
sudo ln -s /home/jenkins/android/prebuilts /opt/prebuilts
```

[server & client]
```shell
sudo subl /etc/init.d/distcc
```
```
PATH=***:/opt/prebuilts/gcc/linux-x86/arm/arm-linux-androideabi-[version]/bin:
```

```shell
sudo subl /etc/profile
```
```
export PATH=/usr/local/lib/distcc:/opt/prebuilts/gcc/linux-x86/arm/arm-linux-androideabi-[version]/bin:/opt/prebuilts/gcc/linux-x86/arm/arm-eabi-[version]/bin:$PATH
```

```shell
source /etc/profile
```

```shell
sudo mkdir /usr/local/lib/distcc
cd /usr/local/lib/distcc

sudo ln -s ../../../bin/distcc arm-linux-androideabi-addr2line
sudo ln -s ../../../bin/distcc arm-linux-androideabi-ar
sudo ln -s ../../../bin/distcc arm-linux-androideabi-c++
sudo ln -s ../../../bin/distcc arm-linux-androideabi-c++filt
sudo ln -s ../../../bin/distcc arm-linux-androideabi-cpp
sudo ln -s ../../../bin/distcc arm-linux-androideabi-strip
sudo ln -s ../../../bin/distcc arm-linux-androideabi-as
sudo ln -s ../../../bin/distcc arm-linux-androideabi-elfedit
sudo ln -s ../../../bin/distcc arm-linux-androideabi-g++
sudo ln -s ../../../bin/distcc arm-linux-androideabi-gcc
sudo ln -s ../../../bin/distcc arm-linux-androideabi-gcc-4.7
sudo ln -s ../../../bin/distcc arm-linux-androideabi-gcc-ar
sudo ln -s ../../../bin/distcc arm-linux-androideabi-gcc-nm
sudo ln -s ../../../bin/distcc arm-linux-androideabi-gcc-ranlib
sudo ln -s ../../../bin/distcc arm-linux-androideabi-gcov
sudo ln -s ../../../bin/distcc arm-linux-androideabi-gdb
sudo ln -s ../../../bin/distcc arm-linux-androideabi-gdbtui
sudo ln -s ../../../bin/distcc arm-linux-androideabi-gprof
sudo ln -s ../../../bin/distcc arm-linux-androideabi-ld
sudo ln -s ../../../bin/distcc arm-linux-androideabi-ld.bfd
sudo ln -s ../../../bin/distcc arm-linux-androideabi-ld.gold
sudo ln -s ../../../bin/distcc arm-linux-androideabi-nm
sudo ln -s ../../../bin/distcc arm-linux-androideabi-objcopy
sudo ln -s ../../../bin/distcc arm-linux-androideabi-objdump
sudo ln -s ../../../bin/distcc arm-linux-androideabi-ranlib
sudo ln -s ../../../bin/distcc arm-linux-androideabi-readelf
sudo ln -s ../../../bin/distcc arm-linux-androideabi-run
sudo ln -s ../../../bin/distcc arm-linux-androideabi-size
sudo ln -s ../../../bin/distcc arm-linux-androideabi-strings
sudo ln -s ../../../bin/distcc arm-eabi-ar
sudo ln -s ../../../bin/distcc arm-eabi-as
sudo ln -s ../../../bin/distcc arm-eabi-c++
sudo ln -s ../../../bin/distcc arm-eabi-c++filt
sudo ln -s ../../../bin/distcc arm-eabi-cpp
sudo ln -s ../../../bin/distcc arm-eabi-elfedit
sudo ln -s ../../../bin/distcc arm-eabi-g++
sudo ln -s ../../../bin/distcc arm-eabi-gcc
sudo ln -s ../../../bin/distcc arm-eabi-gcc-4.6.x-google
sudo ln -s ../../../bin/distcc arm-eabi-gcov
sudo ln -s ../../../bin/distcc arm-eabi-gdb
sudo ln -s ../../../bin/distcc arm-eabi-gdbtui
sudo ln -s ../../../bin/distcc arm-eabi-gprof
sudo ln -s ../../../bin/distcc arm-eabi-ld
sudo ln -s ../../../bin/distcc arm-eabi-ld.bfd
sudo ln -s ../../../bin/distcc arm-eabi-nm
sudo ln -s ../../../bin/distcc arm-eabi-objcopy
sudo ln -s ../../../bin/distcc arm-eabi-objdump
sudo ln -s ../../../bin/distcc arm-eabi-ranlib
sudo ln -s ../../../bin/distcc arm-eabi-readelf
sudo ln -s ../../../bin/distcc arm-eabi-run
sudo ln -s ../../../bin/distcc arm-eabi-size
sudo ln -s ../../../bin/distcc arm-eabi-strings
sudo ln -s ../../../bin/distcc arm-eabi-strip
```

[server]
```shell
distccd --allow 192.168.0.0/16 --daemon
# /etc/rc.d/rc.local 以开机启动
```

[client]
```shell
sudo subl /usr/local/etc/distcc/hosts
```
```
192.168.151.14/4
# server的ip地址和任务限制数
```

```shell
distccmon-text 3
# 查看整个编译任务的进度
```

## 编译
[server & client]
```
修改编译脚本
make -j[] CC=distcc ....
```
```shell
sudo service distcc start
export TARGET_TOOLS_PREFIX=/usr/local/lib/distcc/arm-linux-androideabi-
export CC=distcc
export CXX="distcc g++"
```


## server端配置，或许可用
```shell
sudo apt-get install python3-dev binutils-dev alien libavahi-client-dev libiberty-dev
./configure --without-libiberty
./configure --with-avahi

export PATH=/opt/prebuilts/gcc/linux-x86/arm/arm-linux-androideabi-4.9/bin:$PATH
export PATH=/usr/local/lib/distcc:$PATH
export DISTCC_HOSTS="192.168.151.14 [client]"
```

## 编译时间统计

|服务器 |1.5 |151.14 |
|--|--|--|
|new|51:23|02:04:28|
|new|51:07||


