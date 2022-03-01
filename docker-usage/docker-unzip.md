# 使用容器unzip解压文件

## 使用方法

```bash
podman run --rm -v $(pwd):/unzip unzip quay私有镜像仓库镜像同步.zip
alias uz='podman run --rm -v $(pwd):/unzip unzip'
uz ./quay私有镜像仓库镜像同步.zip

# 需要注意的是，在selinux环境下，要配置selinux
podman run --rm -v $(pwd):/unzip:Z unzip quay私有镜像仓库镜像同步.zip
```

![](2022-03-01-11-21-46.png)
![](2022-03-01-11-10-35.png)

这个命令没有指定镜像，到底用的是哪个镜像呢？
![](2022-03-01-11-27-17.png)


## 构建unzip镜像方法

创建Dockerfile, 内容如下

```dockerfile
#FROM alpine:latest
FROM hub.iefcu.cn/public/alpine:latest

RUN apk --no-cache add unzip

WORKDIR /unzip

#CMD ["unzip"]
ENTRYPOINT ["unzip"]
```

```bash
# 使用docker buildx构建多架构镜像
docker buildx build \
    --build-arg http_proxy=http://proxy.iefcu.cn:20172 \
    --build-arg https_proxy=http://proxy.iefcu.cn:20172 \
    --build-arg no_proxy=yumrepo.unikylin.com.cn,192.0.0.0/8 \
    --platform=linux/arm64,linux/amd64,linux/arm/v6 \
    -t hub.iefcu.cn/xiaoyun/unzip . --push

# 或者使用docker直接构建
docker build \
    --build-arg http_proxy=http://proxy.iefcu.cn:20172 \
    --build-arg https_proxy=http://proxy.iefcu.cn:20172 \
    --build-arg no_proxy=yumrepo.unikylin.com.cn,192.0.0.0/8 \
    -t hub.iefcu.cn/xiaoyun/unzip .
```
