# Jenkins使用

## 安装&启动

1. 从官网下载jenkins.war包，使用命令```java -jar jenkins.war --httpPort=8080```

2. 安装docker，使用命令```docker run -p 8080:8080 -p 50000:50000 -v /your/home:/var/jenkins_home jenkins/jenkins:lts```

## 配置Jenkins

1. 首次进入Jenkins 根据提示进入系统，安装插件

2. Manage Jenkins -> Security -> Manage user，创建用户

3. Manage Jenkins -> System Configuration -> Manage Plugins，管理插件

> 安装pipeline，git等相关插件

4. Manage Jenkins -> System Configuration -> global attributes -> Environment variable， 添加属性

```
DEVOPS_TOKEN_FILE: /home/server/.jenkins/dhuerki
LOCAL_SCRIPT_PATH: /home/server/.jenkins/script/
REMOTE_SCRIPT_PATH: /home/server/.jenkins/script/
python3: /usr/bin/python3
```

## 配置主机

1. 安装sshpass: ```sudo apt-get install sshpass```

2. 安装pip: ```sudo apt-get install python3-pip```

3. 安装mysql-connector: ```sudo pip3 install mysql-connector```

4. 安装requests: ```sudo pip3 install requests```

5. 安装gitpython: ```sudo pip3 install gitpython```

6. 安装fuzzywuzzy: ```sudo pip3 install fuzzywuzzy```

## 配置Remote-trigger

### 第一步需要给所属用户添加token

1. Manage Jenkins -> Security -> Manage user -> 点击对应user -> 设置 -> 添加新Token

> 创建成功后需要复制秘钥

2. 后续通过http创建Jenkins任务时，http请求需要使用以下格式：

```
http://<user>:<user-token>@host:port/
```

### Reset API

1. 触发job

```shell
curl -X POST http://<user>:<user-token>@<jenkins-host>/job/<job-name>/build?token=<job-token>
curl -X POST http://<user>:<user-token>@<jenkins-host>/job/<job-name>/buildWithParameters?key=value
```

2. 查询job

```shell
# 查询所有任务
curl -X GET http://<user>:<user-token>@<jenkins-host>/job/<job-name>/api/json
# 查询指定任务
curl -X GET http://<user>:<user-token>@<jenkins-host>/job/<job-name>/<job-number>/api/json
```

3. 停止job

```shell
curl -X POST http://<user>:<user-token>@<jenkins-host>/job/<job-name>/<job-number>/<stop/term>
```

4. 创建job

```shell
curl -X POST --user "<user>:<user-token>" --data-binary "@/data/config.xml" -H "Content-Type: text/xml" http://<jenkins-host>/createItem\?name\=<job-name>

curl -X POST http://<user>:<user-token>@<jenkins-host>/createItem\?name\=<job-name> --data-binary "@/data/config.xml" -H "Content-Type: text/xml"
```

5. 修改job

```shell
curl -X POST http://<user>:<user-token>@<jenkins-host>/job/<job-name>/config.xml --data-binary "@/<job-name>/config.xml"
```

## Job可用环境变量

|KEY|说明|eg|
|:---|:---|:---|
|BUILD_NUMBER |The current build number          |12|
|JOB_NAME     |Name of the project of this build |foo|
|JENKINS_URL  |Full URL of Jenkins               |http://server:port|
|BUILD_URL    |Full URL of this build            |http://server:port/job/foo/15|
|JOB_URL      |Full URL of this job              |http://server:port/job/foo|

---

# 配置Jenkins service

1. 创建脚本jenkins.sh，内容大致如下。

```shell
JENKINS_PID=`ps -ef | grep jenkins.war | grep -v 'grep' | awk '{print $2}'`

if [ "$1" = "start" ]; then
    nohup java -jar jenkins.war --httpPort=$LISTENING_PORT 2>&1 &
elif [ "$1" = "stop" ]; then
    kill -9 $JENKINS_PID
fi
```

2. 创建文件jenkins.service，内容大致如下，并将文件放置在/usr/lib/systemd/system下。

```buildoutcfg
[Unit]
Description=Jenkins
After=network.target

[Service]
Type=forking
ExecStart=/.../jenkins.sh start
ExecReload=
ExecStop=/.../jenkins.sh stop
PrivateTmp=true

[Install]
WantedBy=multi-user.target
```

3. 执行```systemctl daemon-reload```加载systemd管理器配置。之后就可以通过```systemctl start/top/status jenkins```管理Jenkins服务了。

4. 执行```systemctl enable jenkins```将Jenkins服务设置为开机启动。可通过```systemctl list-units --type=service```查看是否生效。

---

# Jenkins Job

列出了build-line(编译任务)，otadiff(OTA任务)，仅供参考。

## build-line

### 字段说明

|key_name | key_value | 说明 |
|---|---|---|
|project_name             |string              |项目名|
|code_dir                 |string              |代码路径|
|server_hostname          |string              |编译服务器用户名|
|server_ip_address        |string              |编译服务器IP|
|server_passwd            |string              |编译服务器密码（SSH）|
|devops_host_id           |string              |服务器ID（DevOps）|
|devops_compile_id        |string              |编译任务ID（DevOps）|
|is_new_project           |[true, false]       |是否是新项目|
|build_variant            |[u, d, e]           |编译类型|
|cherry_picks             |string              |cherry-pick命令|
|build_sign               |[true, false]       |是否签名|
|build_verity             |[true, false]       |是否验收|
|build_action             |[n, r, ota]         |编译动作|
|need_publish             |[true, false]       |是否打包|
|test_pipeline            |[true, false]       |测试pipeline|
|test_host                |[true, false]       |测试脚本|
|script_path              |string              |脚本路径|
|sign_ftp_url             |string              |签名包上传地址（请勿编辑）|
|sign_ftp_upload_username |string              |签名包上传用户名|
|sign_ftp_upload_passwd   |string              |签名包上传用户密码|
|sv_platform_url          |string              |签名验收后台URL，测试：http://192.168.151.31:8084，生产：http://sign.ttddsh.com:8084|
|sv_platform_username     |string              |签名验收后台登录用户名|
|sv_platform_passwd       |string              |签名验收后台登录用户密码|
|sv_platform_terrace      |string              |签名平台，eg:SPRD_T310p_hongxiangyuan|
|sv_platform_board        |string              |主板（用与验收包释放路径），若为空，则使用大写的项目名|
|sv_platform_model        |string              |机型，若为空，则使用大写的项目名|
|sv_platform_brand        |string              |品牌商，若为空，则使用项目客户号|
|sv_platform_odm          |string              |方案商，若为空，则使用项目渠道号最后一段（eg:HONGXIANGYUAN_HONGXIANGYUAN）|
|sv_platform_cclist       |string              |CC list|
|sv_verity_purpose        |[official, factory] |验收用途，official：正式验收，factory：工厂验收|
|publish_username         |string              |验收包释放用户，若为空，则使用项目客户号|

### pipeline 阶段说明

* prepare
> 打印上文参数

* prepare-jenkins-server
> 装备jenkins，主要是安装sshpass,　pip3等工具

* prepare-host-upload-script
> 将用到的脚本从jenkins服务器上传到编译主机

* build
> 通过ssh连接编译主机，开始编译

* file-upload
> 将打包出来的包上传到签名服务器

* sign-verity
> 创建签名验收任务

* post [^定义一个或多个steps，这些阶段根据流水线或阶段的完成情况而运行]

    * always : 释放服务器占用　＆　写入编译停止时间

    * success: 写入编译成功

    * aborted: 写入编译停止

    * failure: 根据失败位置及原因，写入编译状态

## otadiff

### 字段说明

|key_name | key_value | 说明 |
|---|---|---|
|before_target_file    |string |起始包target路径|
|before_ftp_username   |string |起始包登录用户名|
|before_ftp_passwd     |string |起始包登录密码|
|after_target_file     |string |目标包target路径|
|after_ftp_username    |string |目标包登录用户名|
|after_ftp_passwd      |string |目标包登录密码|
|sv_platform_terrace   |string |签名平台|
|ota_factory_host_ip   |string |OTA工厂IP|
|ota_factory_host_user |string |OTA工厂用户名|
|ota_factory_host_pwd  |string |OTA工厂用户密码|
|ota_factory_host_path |string |OTA工厂脚本路径|
|id                    |string |devops task id|

### 原理

1. OTA编译环境主要依赖代码中以下资源(不同平台略有差异)：
    * vendor/freeme/build/target/product/security
    * build/target/product/security
    * build/tools/releasetools
    * 任一编译环境的out/host/linux-x86目录。
> 由于上述代码中的路径并不会经常更新，out/host/linux-x86的内容也相对稳定。因此可将上述资源单独保存在某一地方，用于编译OTA。

2. 编译OTA的命令略有差异，可以在代码中修改ota文件（build/tools/releasetools/ota_from_target_files.py），查看输出参数来确定。

---

# 遇到的问题和解决方法

1. ssh连接某个服务器后，无法对代码进行sync，和git相关的操作均提示无权限。这是因为我在创建秘钥时，将文件名修改成id_rsa_gerrit（目的是管理多个不同的git账号）了，改成默认的id_rsa就好了。

2. 新配置的机器编译N平台代码时，报如下错误：

```
FAILED: /bin/bash -c "(prebuilts/sdk/tools/jack-admin install-server prebuilts/sdk/tools/jack-launcher.jar prebuilts/sdk/tools/jack-server-4.8.ALPHA.jar  2>&1 || (exit 0) ) && (JACK_SERVER_VM_ARGUMENTS=\"-Dfile.encoding=UTF-8 -XX:+TieredCompilation\" prebuilts/sdk/tools/jack-admin start-server 2>&1 || exit 0 ) && (prebuilts/sdk/tools/jack-admin update server prebuilts/sdk/tools/jack-server-4.8.ALPHA.jar 4.8.ALPHA 2>&1 || exit 0 ) && (prebuilts/sdk/tools/jack-admin update jack prebuilts/sdk/tools/jacks/jack-2.28.RELEASE.jar 2.28.RELEASE || exit 47; prebuilts/sdk/tools/jack-admin update jack prebuilts/sdk/tools/jacks/jack-3.36.CANDIDATE.jar 3.36.CANDIDATE || exit 47; prebuilts/sdk/tools/jack-admin update jack prebuilts/sdk/tools/jacks/jack-4.7.BETA.jar 4.7.BETA || exit 47 )"
Jack server already installed in "/home/server/.jack-server"
Launching Jack server java -XX:MaxJavaStackTraceDepth=-1 -Djava.io.tmpdir=/tmp -Dfile.encoding=UTF-8 -XX:+TieredCompilation -cp /home/server/.jack-server/launcher.jar com.android.jack.launcher.ServerLauncher
Jack server failed to (re)start, try 'jack-diagnose' or see Jack server log
SSL error when connecting to the Jack server. Try 'jack-diagnose'
SSL error when connecting to the Jack server. Try 'jack-diagnose'
```

经过google后找到了问题原因（https://stackoverflow.com/questions/67330554/is-openjdk-upgrading-to-8u292-break-my-aosp-build-system）。
新配置的机器，openjdk版本是1.8.0_292，java Security默认打开了TLSv1, TLSv1.1（/etc/java-8-openjdk/security/java.security），关闭即可解决。

3. 新配置的机器编译P平台代码时，报如下错误：

```
FAILED: /home/server/codes/SPRD-P0-HXY-T310/vendor/sprd/proprietories-source/sprdtrusty/vendor/sprd/modules/faceid/faceid.elf 
/bin/bash -c "(rm /home/server/codes/SPRD-P0-HXY-T310/vendor/sprd/proprietories-source/sprdtrusty/vendor/sprd/modules/faceid/faceid.elf ; true ) && (python /home/server/codes/SPRD-P0-HXY-T310/vendor/sprd/proprietories-source/packimage_scripts/signimage/dynamicTA/signta.py --uuid f4bc36e68ec246e2a82ef7cb6cdc6f72 --key /home/server/codes/SPRD-P0-HXY-T310/vendor/sprd/proprietories-source/packimage_scripts/signimage/sprd/config/dynamic_ta_privatekey.pem --in /home/server/codes/SPRD-P0-HXY-T310/vendor/sprd/proprietories-source/sprdtrusty/vendor/sprd/modules/faceid/full/ta/ums312/faceid.elf --out /home/server/codes/SPRD-P0-HXY-T310/vendor/sprd/proprietories-source/sprdtrusty/vendor/sprd/modules/faceid/faceid.elf ) && (echo \"sign faceid ta end\" )"
rm: 无法删除"/home/server/codes/SPRD-P0-HXY-T310/vendor/sprd/proprietories-source/sprdtrusty/vendor/sprd/modules/faceid/faceid.elf": 没有那个文件或目录
Traceback (most recent call last):
  File "/home/server/codes/SPRD-P0-HXY-T310/vendor/sprd/proprietories-source/packimage_scripts/signimage/dynamicTA/signta.py", line 77, in <module>
    main()
  File "/home/server/codes/SPRD-P0-HXY-T310/vendor/sprd/proprietories-source/packimage_scripts/signimage/dynamicTA/signta.py", line 31, in main
    from Crypto.Signature import PKCS1_v1_5
ImportError: No module named Crypto.Signature
```

```shell
sudo pip install pycryptodome
```

---

# 需要优化和修改的地方

1. 建议在上传完成后，自动将out产生的包删除（0508）

* done(0510)

2. 可将out目录的vmlinux自动上传某一地址（0508）

* done(0909)


3. 优化build.sh脚本，修改更新数据库操作（0508）

* done(0508)


4. 配合devops实现“闲时清环境 & 下载代码”功能（0512）


5. 自动cherry-pick & clean（清除高于服务器的提交节点）（0512）

* done(0525)


6. 统计服务器平均编译时间，自动化性能评估（0512）


7. 主机重启(0603)

* done(0603)


8. 编译OTA(0603)

* done(0611)


9. 为python文件添加＂main＂函数(0621)

* done(0622)


10. 回传OTA编译错误原因(0708)

* done(0714)


11. 记录编译时，项目ProjectConfig.mk(0806)

* done(0909)


12. 记录编译时，所有git仓库信息(0806)

* done(0909)


13. 非签名编译版本，刷机包保存(0831)

* done(0909)
