
# 安装

1. 首先需要安装autoconf alien rpm
```shell
sudo apt-get install autoconf alien rpm python-dev
```

2. 下载 distcc-3.2rc1.tar.gz，解压

3. 编译&安装
```shell
cd distcc-3.2rc1/
./autogen.sh
./configure --with-avahi
grep -lr " -Wall " | xargs sed -i 's/-Wall//g'
grep -lr " -Werror " | xargs sed -i 's/-Werror//g'
sudo make deb/install-deb
cd packaging/
sudo dpkg -i distcc_3.2rc1-1_amd64.deb distcc-server_3.2rc1-1_amd64.deb
```

# 配置（58N）

## server & client

1. 复制一份prebuilts到/opt/下(路径可任意)

2. /etc/distcc/clients.allow
```
#Indicates that the IP of 192.168. * Can be sent to compile tasks
192.168.0.0/16
10.20.0.0/16
```
> 多个域可通过第5条配置，添加多个'--allow [ip]/[mask]'

3. /etc/distcc/commands.allow.sh
```diff
numwords=1
allowed_compilers="
/usr/bin/cc
/usr/bin/c++
/usr/bin/c89
/usr/bin/c99
/usr/bin/gcc
/usr/bin/g++
/usr/bin/*gcc-*
/usr/bin/*g++-*
+/opt/prebuilts/gcc/linux-x86/aarch64/aarch64-linux-android-4.9/bin/aarch64-linux-android*
+/opt/prebuilts/gcc/linux-x86/host/x86_64-linux-glibc2.15-4.8/bin/x86_64-linux*
"
```

4. /etc/distcc/hosts
```
localhost 192.168.48.92 192.168.151.14
```
> ps. 可修改的文件如下（按照优先级顺序） ```~/.distcc/hosts & /etc/hosts & /etc/distcc/hosts```
> 设置完后可通过```distcc --show-hosts```查看是否生效
> IP的顺序为主机性能顺序

5. /etc/init.d/distcc
```
OPTIONS="--verbose --log-file=/var/log/distccd.log --daemon --stats --job-lifetime=1200"
```

6. /etc/default/distcc
```
STARTDISTCC=true
```

7. 启动服务
```shell
sudo /etc/init.d/distcc reload
```

## client

1.
```shell
export PATH=/usr/bin/distcc:$PATH
```

2. [code]/build/core/combo/select.mk
```diff
@@ -47,3 +47,15 @@ $(combo_var_prefix)STATIC_LIB_SUFFIX := .a
 
 # Now include the combo for this specific target.
 include $(BUILD_COMBOS)/$(combo_target)$(combo_os_arch).mk
+
+ifeq (,$(findstring distcc,$($(combo_target)CC)))
+$(combo_target)CC := distcc $($(combo_target)CC)
+endif
+
+ifeq (,$(findstring distcc,$($(combo_target)CXX)))
+$(combo_target)CXX := distcc $($(combo_target)CXX)
+endif
+$(warning elifli $(combo_target)CC : $($(combo_target)CC))
+$(warning elifli $(combo_target)CXX : $($(combo_target)CXX))
```

3. [code]/build/core/combo/HOST_linux-x86_64.mk
```diff
@@ -18,7 +18,7 @@
 # Included by combo/select.mk
 
 ifeq ($(strip $(HOST_TOOLCHAIN_PREFIX)),)
-HOST_TOOLCHAIN_PREFIX := prebuilts/gcc/linux-x86/host/x86_64-linux-glibc2.15-4.8/bin/x86_64-linux-
+HOST_TOOLCHAIN_PREFIX := /opt/prebuilts/gcc/linux-x86/host/x86_64-linux-glibc2.15-4.8/bin/x86_64-linux-
 endif
 HOST_CC  := $(HOST_TOOLCHAIN_PREFIX)gcc
 HOST_CXX := $(HOST_TOOLCHAIN_PREFIX)g++
```

4. [code]/device/mediatek/mt6758/BoardConfig.mk
```diff
@@ -36,10 +36,10 @@ TARGET_2ND_ARCH := arm
 TARGET_2ND_ARCH_VARIANT := armv7-a-neon
 TARGET_2ND_CPU_ABI := armeabi-v7a
 TARGET_2ND_CPU_ABI2 := armeabi
-TARGET_TOOLCHAIN_ROOT := prebuilts/gcc/$(HOST_PREBUILT_TAG)/aarch64/aarch64-linux-android-4.9
+TARGET_TOOLCHAIN_ROOT := /opt/prebuilts/gcc/$(HOST_PREBUILT_TAG)/aarch64/aarch64-linux-android-4.9
 TARGET_TOOLS_PREFIX := $(TARGET_TOOLCHAIN_ROOT)/bin/aarch64-linux-android-
 
-KERNEL_CROSS_COMPILE:= $(abspath $(TOP))/$(TARGET_TOOLS_PREFIX)
+KERNEL_CROSS_COMPILE:= $(TARGET_TOOLS_PREFIX)
 
 endif
```

## 关于如何不用增加prebuilts的猜想1（验证成功）

1. ln -s 增加一个相同的link，指向各自的prebuilts。

## 关于如何不用增加prebuilts的猜想2（待验证）

1. 服务端&客户端源码的绝对路径相同

2. 配置 -> server & client -> 3 中，修改为源码里面的路径（绝对路径）

3. 配置 -> client -> 3 中，修改TARGET_TOOLCHAIN_ROOT为源码里的prebuilts路径（绝对路径）


# 安装dmucs

1. 下载dmucs-0.6.tar.bz2(https://versaweb.dl.sourceforge.net/project/dmucs/dmucs/0.6/dmucs-0.6.tar.bz2)

2. 解压，安装
```shell
bzip2 -d dmucs-0.6.tar.bz2
tar -xvf dmucs-0.6.tar
cd dmucs/
./configure
```

修改Makefile文件，在CFLAGS和CXXFLAGS里添加-fpermissive

```shell
sudo make CPPFLAGS=-DSERVER_MACH_NAME=\\\"192.168.1.5\\\"
sudo make install
```

# 配置dmucs

1. 安装之后，确保 loadavg 在每台主机上都可以执行
```shell
server@droi:/home/share/58N$ loadavg 
Could not open client: Transport endpoint is not connected
```

2. 安装之后，确保 dmucs 可以再server上执行
```shell
server@droi:/home/share/58N$ dmucs 
[Sat Feb 20 16:11:52 2021] Hosts Served: 0  Max/Avail: 0/0
```

3. 在每台主机上创建文件/usr/local/share/dmucs/hosts-info
#Format：host-name number-of-cpus power-index
[ip-1] 32 4
[ip-2] 16 3
[ip-3] 16 2
[ip-4] 8 1

4. 确保每台loadavg主机的/etc/hosts文件，第一条记录是本机IP地址

5. 编译主机上，[code]/build/core/combo/select.mk
```diff
@@ -47,3 +47,15 @@ $(combo_var_prefix)STATIC_LIB_SUFFIX := .a
 
 # Now include the combo for this specific target.
 include $(BUILD_COMBOS)/$(combo_target)$(combo_os_arch).mk
+
+ifeq (,$(findstring distcc,$($(combo_target)CC)))
+$(combo_target)CC := gethost distcc $($(combo_target)CC)
+endif
+
+ifeq (,$(findstring distcc,$($(combo_target)CXX)))
+$(combo_target)CXX := gethost distcc $($(combo_target)CXX)
+endif
```

# 编译时间统计

|服务器 |1.5 |151.14 |
|--|--|--|
|no distcc   |51:23|02:04:28|
|no distcc   |51:07||
|no distcc   |48:34||
|with distcc |53:29||
|with distcc |53:29||
|with distcc |54:07||
|with distcc |55:37||
|with distcc |48:42||
|with distcc |51:25||



## 记录

1. 1.5上
```shell
server@droi:/home/share/distcc$ distcc --show-hosts
localhost
red
green
blue
```

ps. 原因1
/etc/hosts 包含如下内容
```
localhost red green blue
192.168.151.14 red green blue
```
ps. 原因2(主因)
/home/server/.distcc/hosts
```
localhost red green blue
```

2. /var/log/distccd.log可用tag
* "connection from"
> 来自client的连接请求
* "changed input from"
> 需要编译的文件
* "job complete"
> 工作完成
* "COMPILE_ERROR"
> 编译失败
* "COMPILE_OK"
> 编译完成

3. 综合上面编译时间统计来看，distcc的效果并不理想。
查阅资料找到谷歌官方有Goma和RBE两种分布式编译工具，但是目前官方不建议使用Gome，理由是对于AOSP编译不是特别好！

4. RBE属于BAZEL构建系统的一部分，具体在文档bazel.md中说明
