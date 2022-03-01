# console镜像构建方法

console源码中有Dockerfile，但是都是基于外部的一些基础镜像，以及构建镜像，还有其他的一些依赖。
在我们的内网环境中无法正常构建，我修改了一部分逻辑，使得可以轻松构建。

基于源码 http://192.168.120.13/xiaoyun/kcp-console
(分支 test-build-release-4.9 )
我修改了如下文件

M       Dockerfile

M       frontend/yarn.lock

A       node-v14.18.0-headers.tar.gz

编译构建console镜像，只需要一行命令即可

```bash
git clone -b test-build-release-4.9 http://192.168.120.13/xiaoyun/kcp-console
cd kcp-console

docker build -t hub.iefcu.cn/xiaoyun/xiaoyun-console:20220301 .
```

修改逻辑，主要是使用自己的内部镜像进行编译，以及去除网络下载依赖

1. Dockerfile中，使用私有镜像仓库的镜像来构建

2. 修改yarn.lock，配置为使用私有npm镜像仓库

3. 新增node-v14.18.0-headers.tar.gz代码，构建npm某个包需要
