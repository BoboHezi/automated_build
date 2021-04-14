
# Jenkins使用

## 安装&启动

1. 从官网下载jenkins.war包，使用命令```java -jar jenkins.war --httpPort=8080```

2. 安装docker，使用命令```docker run -p 8080:8080 -p 50000:50000 -v /your/home:/var/jenkins_home jenkins/jenkins:lts```

## 配置Jenkins

1. 首次进入Jenkins 根据提示进入系统，安装插件

2. Manage Jenkins -> Security -> Manage user，创建用户

3. Manage Jenkins -> System Configuration -> Manage Plugins，管理插件


## 配置主机

1. 同目录下build.sh文件拷贝到主机每个repo仓库根目录下

2. 安装sshpass: ```sudo apt-get install sshpass```

3. 安装pip: ```sudo apt-get install python pip```

4. 安装mysql-connector: ```sudo pip install mysql-connector```

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
```
curl -X POST http://<user>:<user-token>@<jenkins-host>/job/<job-name>/build?token=<job-token>
curl -X POST http://<user>:<user-token>@<jenkins-host>/job/<job-name>/buildWithParameters?token=<job-token>&key=value
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

## Job可用环境变量
|KEY|说明|eg|
|:---|:---|:---|
|BUILD_NUMBER |The current build number          |12|
|JOB_NAME     |Name of the project of this build |foo|
|JENKINS_URL  |Full URL of Jenkins               |http://server:port|
|BUILD_URL    |Full URL of this build            |http://server:port/job/foo/15|
|JOB_URL      |Full URL of this job              |http://server:port/job/foo|

## jenkins job build-line

### 字段说明
|key_name | key_value | 说明 |
|--|--|--|
|project_name      |string        |项目名|
|code_dir          |string        |代码路径|
|server_hostname   |string        |编译服务器用户名|
|server_ip_address |string        |编译服务器IP|
|server_passwd     |string        |编译服务器密码（SSH）|
|devops_host_id    |string        |服务器ID（DevOps）|
|devops_compile_id |string        |编译任务ID（DevOps）|
|is_new_project    |[true, false] |是否是新项目|
|build_variant     |[u, d, e]     |编译类型|
|build_sign        |[true, false] |是否签名|
|build_verity      |[true, false] |是否验收|
|build_action      |[n, r, ota]   |编译动作|
|need_publish      |[true, false] |是否打包|
|is_test_pipeline  |[true, false] |测试pipeline|
|is_test_host      |[true, false] |测试脚本|

