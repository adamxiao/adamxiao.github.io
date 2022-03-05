# 搭建私有镜像仓库

使用harbor，quay，registry等搭建,
registry搭建最简单, quay复杂，harbor没搭建过

## 使用registry搭建

参考 [docker官方文档](https://docs.docker.com/registry/deploying/)

最简单，一行命令搞定
```
mkdir -p /data/registry
docker run -d --name registry --restart=always \
  -p 80:5000 \
  -v /data/registry:/var/lib/registry \
  registry:2
```

### 搭建安全证书镜像仓库

创建目录/data/registry, 以下操作都是在此目录下执行

准备工作
```bash
mkdir -p certs registry
# 创建https证书文件, certs/ssl.key, certs/ssl.cert
```

创建私有证书，参考[redhat quay配置私有证书](https://access.redhat.com/documentation/en-us/red_hat_quay/3/html/manage_red_hat_quay/using-ssl-to-protect-quay)

创建docker-compose.yml文件，内容如下：
```yaml
version: '3.2'
services:
  registry:
    image: docker.io/library/registry:2
    container_name: registry
    restart: always
    environment:
      REGISTRY_HTTP_TLS_CERTIFICATE: /certs/ssl.cert
      REGISTRY_HTTP_TLS_KEY: /certs/ssl.key
      REGISTRY_HTTP_ADDR: 0.0.0.0:9443
    volumes:
      - ./registry:/var/lib/registry:Z
      - ./certs:/certs:Z
    ports:
      - 5000:5000
      - 9443:9443
    logging:
      driver: json-file
      options:
        max-file: '3'
        max-size: 100m
```

注意事项：
* 证书是为域名quay.iefcu.cn创建的，具体创建方法见其他文档
* registry配置服务域名为quay.iefcu.cn, 需要和证书匹配

XXX: 配置镜像仓库只读

./config.yml:/etc/docker/registry/config.yml:Z
```yaml
  maintenance:
    readonly:
      enabled: false
```

### 测试私有镜像仓库使用

```bash
docker tag registry:2 quay.iefcu.cn:9443/public/registry:2
docker push quay.iefcu.cn:9443/public/registry:2
docker pull quay.iefcu.cn:9443/public/registry:2
```


## 使用quay搭建

TODO:

## 参考文档

* https://docs.docker.com/registry/deploying/
