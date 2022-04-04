# v2raya源码编译使用

#### 基本使用

```
# run v2raya
docker run -d \
    --restart=always \
    --privileged \
    --network=host \
    --name v2raya \
    -v /etc/v2raya:/etc/v2raya \
    hub.iefcu.cn/public/v2raya
```

#### 构建镜像

* https://github.com/mzz2017/V2RayA.git
* 分支: 42b3e4e 1.5.4

构建命令
```
docker buildx build \
  --build-arg http_proxy=http://proxy.iefcu.cn:20172 \
  --build-arg https_proxy=http://proxy.iefcu.cn:20172 \
  --platform=linux/arm/v6 \
  -t hub.iefcu.cn/xiaoyun/v2raya:armv6 . --push
#docker buildx build  --platform=linux/arm/v6 -t hub.iefcu.cn/xiaoyun/v2raya:armv6 . --push
```

dockerfile修改点:
```diff
diff --git a/Dockerfile b/Dockerfile
index 252b5f4..0fb2298 100644
--- a/Dockerfile
+++ b/Dockerfile
@@ -1,10 +1,10 @@
-FROM mzz2017/git:alpine AS version
+FROM hub.iefcu.cn/public/git:alpine AS version
 WORKDIR /build
 ADD .git ./.git
 RUN git describe --abbrev=0 --tags | tee ./version


-FROM node:lts-alpine AS builder-web
+FROM hub.iefcu.cn/public/node:lts-alpine AS builder-web
 ADD gui /build/gui
 WORKDIR /build/gui
 RUN echo "network-timeout 600000" >> .yarnrc
@@ -12,16 +12,17 @@ RUN echo "network-timeout 600000" >> .yarnrc
 #RUN yarn config set sass_binary_site https://cdn.npm.taobao.org/dist/node-sass -g
 RUN yarn cache clean && yarn && yarn build

-FROM golang:alpine AS builder
+FROM hub.iefcu.cn/public/golang:alpine AS builder
 ADD service /build/service
 WORKDIR /build/service
 COPY --from=version /build/version ./
 COPY --from=builder-web /build/web server/router/web
 RUN export VERSION=$(cat ./version) && CGO_ENABLED=0 go build -ldflags="-X github.com/v2rayA/v2rayA/conf.Version=${VERSION:1} -s -w" -o v2raya .

-FROM v2fly/v2fly-core
+FROM hub.iefcu.cn/public/v2fly-core
 COPY --from=builder /build/service/v2raya /usr/bin/
-RUN wget -O /usr/local/share/v2ray/LoyalsoldierSite.dat https://raw.githubusercontent.com/mzz2017/dist-v2ray-rules-dat/master/geosite.dat
+#RUN wget -O /usr/local/share/v2ray/LoyalsoldierSite.dat https://raw.githubusercontent.com/mzz2017/dist-v2ray-rules-dat/master/geosite.dat
+RUN wget -O /usr/local/share/v2ray/LoyalsoldierSite.dat http://http.iefcu.cn/http/geosite.dat
 RUN apk add --no-cache iptables ip6tables
 EXPOSE 2017
 VOLUME /etc/v2raya
```

## FAQ

1. 树莓派1B上开启透明代理报错
  原因是ipv6有问题，可以修正v2raya镜像的dockerfile，不启用ipv6

## 参考文档

* [v2raya官方文档](https://v2raya.org/docs/prologue/quick-start/)
