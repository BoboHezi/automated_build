
现代化构建：允许程序员通过规范和模块化的任务形式来创建构建脚本，并提供工具来执行这些任务，并完成依赖管理。

# BAZEL
> 参考文档：https://docs.bazel.build/versions/4.0.0/install-ubuntu.html#install-with-installer-ubuntu

## 安装

1. 下载文件bazel-4.0.0-installer-linux-x86_64.sh(https://github-releases.githubusercontent.com/20773773/62d9ea00-5bc7-11eb-8a3b-314d5fb68ae7?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIAIWNJYAX4CSVEH53A%2F20210224%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Date=20210224T013718Z&X-Amz-Expires=300&X-Amz-Signature=5ffc0b26ca3e78b04eba2e93164e6f1043e1396e4641afa2f6bc1fda84d31f46&X-Amz-SignedHeaders=host&actor_id=19927897&key_id=0&repo_id=20773773&response-content-disposition=attachment%3B%20filename%3Dbazel-4.0.0-installer-linux-x86_64.sh&response-content-type=application%2Foctet-stream)

2. ```./bazel-4.0.0-installer-linux-x86_64.sh --user```

## 使用

1. ```bazel build xxx```
编译

2. ```bazel clean```


## remote cache 安装&使用
> 参考文档：https://zhuanlan.zhihu.com/p/265542636

1. 安装docker(Ubuntu 14需要使用17.12.1-ce)
```shell
sudo apt-get install apt-transport-https ca-certificates curl gnupg-agent software-properties-common
curl -fsSL https://mirrors.ustc.edu.cn/docker-ce/linux/ubuntu/gpg | sudo apt-key add -
sudo apt-key fingerprint 0EBFCD88
sudo add-apt-repository "deb [arch=amd64] https://mirrors.ustc.edu.cn/docker-ce/linux/ubuntu/ $(lsb_release -cs) stable"
sudo apt-get update
apt-cache madison docker-ce
sudo apt-get install docker-ce=17.12.1~ce-0~ubuntu
sudo docker run hello-world
```

2. ```docker pull buchgr/bazel-remote-cache```

3. ```docker run -v $path/cache:/data -p 9090:8080 -p 9092:9092 buchgr/bazel-remote-cache```

4. 编译时，添加 --remote_cache=http://host:9090

## remote executor 安装&使用
> 参考文档：https://zhuanlan.zhihu.com/p/266510840

1. 下载
```shell
mkdir buildfarm
cd buildfarm
git clone https://github.com/bazelbuild/bazel-buildfarm.git
cd bazel-buildfarm
```

2. 修改.bazelversion文件内容为bazel的版本号```bazel version```

3. 修改client，examples/worker.config.example
root:					# 把这里改成一个的确存在的路径
cas_cache_directory:	# 把这里要么改成一个对上面root的相对路径，要么改为绝对路径
target:					# 修改为server的ip(eg.192.168.1.5:8980)

4. 配置&启动server
```shell
# 首次编译需使用Python3
bazel run src/main/java/build/buildfarm:buildfarm-server $PWD/examples/server.config.example
```

5. 配置&启动client
```shell
bazel run src/main/java/build/buildfarm:buildfarm-operationqueue-worker $PWD/examples/worker.config.example
```

6. 编译时，添加 --remote_executor=grpc://server-host:8980

## bazel Android项目编译
> 参考文档：https://zhuanlan.zhihu.com/p/263600968

1. 项目根目录添加WORKSPACE，写入内容
```
android_sdk_repository(
	name = "androidsdk",
    path = "/path/to/Android/sdk",
    api_level = 25,
    build_tools_version = "26.0.1"
)
```
> ps. name为必选项，定义SDK，会自动定位环境变量ANDROID_HOME来知道sdk路径

2. 在项目根目录下添加BUILD，写入内容如下
```
android_binary(
    name = "app",
    manifest = "AndroidManifest.xml",
    deps = ["//[path]:[module]"],
)
```
AndroidManifest.xml可以只添加简单信息，application可缺省

3. 在对应的模块根目录下添加BUILD，写入内容如下
```
package(
    default_visibility = ["//src:__subpackages__"],
)

android_library(
    name = "drawer",
    srcs = glob(["**/*.java"]),
    manifest = "AndroidManifest.xml",
    resource_files = glob(["res/**"]),
)
```

## 添加第三方依赖(maven)

1. 在WORKSPACE中添加如下内容：
```
load("@bazel_tools//tools/build_defs/repo:http.bzl", "http_archive")

RULES_JVM_EXTERNAL_TAG = "2.8"
RULES_JVM_EXTERNAL_SHA = "79c9850690d7614ecdb72d68394f994fef7534b292c4867ce5e7dec0aa7bdfad"

http_archive(
    name = "rules_jvm_external",
    strip_prefix = "rules_jvm_external-%s" % RULES_JVM_EXTERNAL_TAG,
    sha256 = RULES_JVM_EXTERNAL_SHA,
    url = "https://github.com/bazelbuild/rules_jvm_external/archive/%s.zip" % RULES_JVM_EXTERNAL_TAG,
)

load("@rules_jvm_external//:defs.bzl", "maven_install")

maven_install(
    artifacts = [
        "androidx.appcompat:appcompat:1.1.0",
        "com.google.android.material:material:1.1.0",
    ],
    repositories = [
        "https://jcenter.bintray.com/",
        "https://repo1.maven.org/maven2",
        "https://maven.google.com",
    ],
)
```

2. 在需要依赖的模块BUILD，添加如下：
```
deps = [
    "@maven//:androidx_appcompat_appcompat",
    "@maven//:com_google_android_material_material",
]
```

