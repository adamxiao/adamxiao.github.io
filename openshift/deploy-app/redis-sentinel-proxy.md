# redis sentinel proxy提供master对外服务

## 构建redis-sentinel-proxy镜像

源码:
https://github.com/flant/redis-sentinel-proxy

TODO: 还有一些配置需要修改

修改dockerfile
```
-FROM golang:1.17 AS builder
+FROM hub.iefcu.cn/public/golang:1.16 AS builder

-FROM alpine:3.14
+FROM hub.iefcu.cn/public/alpine:3.14
```

简单命令构建
```
docker build \
  --build-arg http_proxy=http://proxy.iefcu.cn:20172 \
  --build-arg https_proxy=http://proxy.iefcu.cn:20172 \
  -t hub.iefcu.cn/xiaoyun/redis-sentinel-proxy:arm64 .
```

原始镜像:
docker pull flaccid/redis-sentinel-proxy

## 部署sentinel proxy

yaml源码:
https://github.com/shishirkh/redis-ha

```
kubectl apply -f proxy/proxy.yml

kubectl exec -it deployment/deployment-redis-instance-1 -- redis-cli -h svc-redis-sentinel-proxy -p 6379 -c info replication
```

## 参考资料

* [Creating a Redis cluster in Kubernetes](https://www.linkedin.com/pulse/creating-redis-cluster-kubernetes-shishir-khandelwal)
