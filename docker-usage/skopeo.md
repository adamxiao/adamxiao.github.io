# 镜像搬运工 skopeo

skopeo作用:

1. 拉取镜像

2. 同步镜像

3. 查看镜像manifest等其他数据

缺点：就是skopeo只同步了同一个架构的镜像？

## 安装skopeo

TODO:

## 使用入门


### 拉取镜像

```bash
# 下载指定一个镜像到本地
skopeo --insecure-policy copy docker://nginx:1.17.6 docker-archive:/tmp/nginx.tar

# 拉取前，检查镜像是否arm64
skopeo --insecure-policy --override-arch arm64 inspect docker://hub.iefcu.cn/xiaoyun/unzip:latest

# 指定拉取arm64镜像
skopeo --insecure-policy --override-arch arm64 copy docker://hub.iefcu.cn/xiaoyun/unzip:latest docker-archive:/tmp/unzip.tar
```

### 同步镜像

TODO: 能不能节省同步镜像到本地目录blob的空间？

```bash
skopeo copy --insecure-policy --src-tls-verify=false --dest-tls-verify=false --dest-authfile /root/.docker/config.json docker://docker.io/busybox:latest docker://harbor.weiyigeek.top/devops/busybox:latest
```

#### 查看镜像Digest值

关键字《docker command to get image digest》

https://stackoverflow.com/questions/32046334/where-can-i-find-the-sha256-code-of-a-docker-image

TODO: 找更好的方法， 这里需要使用docker拉到镜像才能使用。。。
```bash 
docker inspect --format='{{index .RepoDigests 0}}' hub.iefcu.cn/kcp/cluster-logging-operator:20220406

# 这个有些镜像居然没有显示?
docker images --digests
```

## 参考文档

[（好）如何使用Skopeo做一个优雅的镜像搬运工](https://www.modb.pro/db/251368)


