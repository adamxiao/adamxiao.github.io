# 镜像搬运工 skopeo

skopeo作用:

1. 拉取镜像

2. 同步镜像

3. 查看镜像manifest等其他数据

缺点：就是skopeo只同步了同一个架构的镜像？

## 安装skopeo

centos 7安装
```bash
yum install -y skopeo
```

### 直接使用镜像

```bash
# 原始镜像: quay.io/skopeo/stable:latest
alias skopeo='docker run --privileged -v $PWD:/data -w /data --rm hub.iefcu.cn/public/skopeo'
# XXX: 要加--privileged才行，不然段错误，为啥?

# 简单使用测试
skopeo copy --help
```

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

首先生成auth认证配置文件
```
skopeo login hub.iefcu.cn
# 或者生成auth文件到指定路径
skopeo login --authfile auth.json hub.iefcu.cn
```

批量同步镜像
```
cat <<'EOF' > skopeo-sync.yml
registry.example.com:
  images:
    busybox: []
    redis:
      - "1.0"
      - "2.0"
      - "sha256:111111"
  images-by-tag-regex:
      nginx: ^1\.13\.[12]-alpine-perl$
  credentials:
      username: john
      password: this is a secret
  tls-verify: true
  cert-dir: /home/john/certs
quay.io:
  tls-verify: false
  images:
    coreos/etcd:
      - latest
EOF

skopeo sync --src yaml --dest docker skopeo-sync.yml my-registry.local.lan/repo/
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

参考： https://stackoverflow.com/questions/39375421/can-i-get-an-image-digest-without-downloading-the-image
```bash
skopeo inspect docker://hub.iefcu.cn/xiaoyun/tmp:0413-4.9.0-rc.6-arm64-console-operator | grep Digest
skopeo inspect --format "{{ .Digest }}" "docker://$image"
```

## 参考文档

[（好）如何使用Skopeo做一个优雅的镜像搬运工](https://www.modb.pro/db/251368)


