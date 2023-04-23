# console镜像构建方法

## 从源码一键构建镜像

console源码中有Dockerfile，但是都是基于外部的一些基础镜像，以及构建镜像，还有其他的一些依赖。
在我们的内网环境中无法正常构建，我修改了一部分逻辑，使得可以轻松构建。

基于源码 http://192.168.120.13/xiaoyun/kcp-console
(分支 test-build-release-4.9 )
我修改了如下文件

* M Dockerfile => 修改使用内部编译构建镜像，以及修正部分网络依赖逻辑
* M frontend/yarn.lock => 修改使用内部私有npm仓库源
* A node-v14.18.0-headers.tar.gz => 编译npm模块需要
* M build-frontend.sh  => yarn install --network-timeout 1000000 (网络磁盘慢导致yarn install总失败)

编译构建console镜像，只需要一行命令即可

```bash
git clone -b test-build-release-4.9 http://192.168.120.13/xiaoyun/kcp-console
cd kcp-console

docker build -t hub.iefcu.cn/xiaoyun/xiaoyun-console:20220301 .
```

修改逻辑，主要是使用自己的内部镜像进行编译，以及去除网络下载依赖

* 1.Dockerfile中，使用私有镜像仓库的镜像来构建
* 2.修改yarn.lock，配置为使用私有npm镜像仓库
* 3.新增node-v14.18.0-headers.tar.gz代码，构建npm某个包需要
* 4.修改yarn install增加超时时间, 因为网络磁盘慢导致yarn install总报网络失败

还可以通过openshift平台，基于S2I自动构建部署console镜像

目前还有一点小问题, 需要配置放开crio的pids limit限制，从1024增大为4096

```bash
oc new-project console-test
oc new-app http://192.168.120.13/xiaoyun/kcp-console.git#test-build-release-4.9
```

#### 修改yarn.lock的镜像仓库

目前我是通过手动修改的
```
export YOUR_CI_REGISTRY=http://docker.iefcu.cn:5565/repository/npm-group/
sed -i -e "s#https://registry.yarnpkg.com/#${YOUR_CI_REGISTRY}#g" yarn.lock
sed -i -e "s#https://registry.npmjs.org/#${YOUR_CI_REGISTRY}#g" yarn.lock
```

关键字《yarn.lock resolved change registry》

https://stackoverflow.com/questions/48258087/how-to-use-different-yarn-registry-regardless-of-registry-in-the-yarn-lock-file
=> 待尝试这个方法 => 不行
```
sed -i -e "/resolved:* .*$/d" yarn.lock
yarn config set registry <YOUR_REGISTRY>
yarn install
```

[The Ultimate Guide to yarn.lock Lockfiles](https://www.arahansen.com/the-ultimate-guide-to-yarn-lock-lockfiles/)
=> 了解yarn.lock文件使用

https://www.npmjs.com/package/swap-lock-registry
=> 还有人写了一个工具修改yarn.lock的registry地址...
```
swap-lock-registry -u https://registry.npmjs.com [lock-files...]
```

## 从二进制手动构建镜像

console镜像主要包括两个程序：
1. bridge二进制文件
2. dist前端打包文件

可以先手动构建出这两个文件，然后再基于原始console镜像，简单构建新的console镜像

编写Dockerfile.adam如下:
```dockerfile
FROM hub.iefcu.cn/xiaoyun/openshift4-aarch64:4.9.0-rc.6-arm64-console

USER 0
COPY ./bridge /opt/bridge/bin/bridge
COPY ./oc /opt/bridge/bin/oc
COPY ./get_token.sh /opt/bridge/bin/get_token.sh
RUN rm -rf /opt/bridge/static/ && mkdir /opt/bridge/static/
ADD ./dist.tgz /opt/bridge/static/

USER 1001
```

然后通过构建命令构建
```bash
docker build -f ./Dockerfile.adam -t hub.iefcu.cn/xiaoyun/ocp-build:4.9.0-rc.6-arm64-console-0125 .
```

#### 构建dist前端文件的方法

```bash
# 到console源码目录
docker run -it -v $PWD:/opt/app-root/src -w /opt/app-root/src --entrypoint bash hub.iefcu.cn/public/node:14
# 进入容器后，执行./build-frontend.sh
# 编译完成可以找到前端打包dist文件: /opt/app-root/src/frontend/public/dist
```

配置如下环境变量，能够节省一些不必要的资源下载
```
export CHROMEDRIVER_SKIP_DOWNLOAD=true
export GECKODRIVER_SKIP_DOWNLOAD=true
export SKIP_SASS_BINARY_DOWNLOAD_FOR_CI=true
export CYPRESS_INSTALL_BINARY=0
export NPM_CONFIG_TARBALL=/opt/app-root/src/node-v14.18.0-headers.tar.gz
```

## console编译调试

单号: 49462

4. 安装依赖

4.1 安装docker, git

    运行 dnf install docker git jq

4.2 安装golang包

    golang.tar ，资源在 ftp://10.0.0.5》02-研发二部》01-仅部门可见》chenzheng

4.3 更换yarn 源

    yarn config set registry https://registry.npm.taobao.org/

4.4 上传console源码到云服务器上

    资源传在 ftp://10.0.0.5》02-研发二部》01-仅部门可见》chenzheng
    或者 git clone https://github.com/PJYang/console.git -b release-4.9

4.5 上传kube config文件到云服务器

    上传config.tar ，资源附在此单下
    解压并重命名为~/.kube/config

5. 初始化容器云，/root/console 目录下运行

docker run -it --name node -v $PWD:/opt/app-root/src -w /opt/app-root/src hub.iefcu.cn/public/node:14 bash

编译前端：./build-frontend.sh

编译后端：此时需要退出容器, 再运行：

    exit
    ./build-backend.sh

6. 启动，/root/console 目录下运行 

    oc process -f examples/console-oauth-client.yaml | oc apply -f -
    oc get oauthclient console-oauth-client -o jsonpath='{.secret}' > examples/console-client-secret
    oc get secrets -n default --field-selector type=kubernetes.io/service-account-token -o json | \
        jq '.items[0].data."ca.crt"' -r | python -m base64 -d > examples/ca.crt
    ./examples/run-bridge.sh

7. 查看效果

    进入vnc，打开浏览器输入 127.0.0.1:9000 (admin/ksvd2020)



## 其他资料

发现官网另外一个项目对console项目做的离线包处理。
![](../imgs/2022-03-02-09-38-37.png)

## FAQ

#### yarn run build exit 1

=> 最后发现是因为有两个未使用的变量导致的, 去除掉即可，是某人最近引入的

关键字《yarn ts-node exit 1》

```
    [34] ./node_modules/monaco-editor/esm/vs/editor/editor.worker.js 1.07 KiB {0} [built]
        + 23 hidden modules
error Command failed with exit code 1.
info Visit https://yarnpkg.com/en/docs/cli/run for documentation about this command.
error Command failed with exit code 1.
info Visit https://yarnpkg.com/en/docs/cli/run for documentation about this command.
```

猜测:
- 可能是docker run没有privilage权限啦? 以前不需要，现在需要了?

思路:
- strace看看进程怎么退出-1了?


#### yarn run build编译内存不足

发现8g内存不够，居然内存不足，编译失败
```
css-loader-parser: postcss.plugin was deprecated. Migration guide:
https://evilmartians.com/chronicles/postcss-8-plugin-migration
Killed
error Command failed with exit code 137.
info Visit https://yarnpkg.com/en/docs/cli/run for documentation about this command.
error Command failed with exit code 137.
info Visit https://yarnpkg.com/en/docs/cli/run for documentation about this command.
root@fa0b2b80ba6f:/opt/app-root/src/frontend# Error: write EPIPE
```

使用free定时监控，发现内存真的消耗完了
```
Fri Apr 21 08:47:33 UTC 2023
              total        used        free      shared  buff/cache   available
Mem:           7629        6871         500          23         256          30
Swap:             0           0           0
Fri Apr 21 08:47:34 UTC 2023
-bash: fork: Cannot allocate memory

while true ; do free -m ;date;sleep 1; done
```
