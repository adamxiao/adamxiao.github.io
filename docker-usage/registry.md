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
      # 个性化配置registry，例如可以配置registry只读
      #- ./config.yml:/etc/docker/registry/config.yml:Z
    ports:
      - 9443:9443
    logging:
      driver: json-file
      options:
        max-file: '3'
        max-size: 10m
```

注意事项：
* 证书是为域名quay.iefcu.cn创建的，具体创建方法见其他文档
* registry配置服务端口为9443, 是因为已经了占用443端口的服务了

XXX: 配置镜像仓库只读

./config.yml:/etc/docker/registry/config.yml:Z
```yaml
storage:
  maintenance:
    readonly:
      enabled: false
```

附上config.yml全文
```yaml
version: 0.1
log:
  fields:
    service: registry
storage:
  cache:
    blobdescriptor: inmemory
  filesystem:
    rootdirectory: /var/lib/registry
  maintenance:
    readonly:
      enabled: false
http:
  addr: :5000
  headers:
    X-Content-Type-Options: [nosniff]
health:
  storagedriver:
    enabled: true
    interval: 10s
    threshold: 3
```

### 测试私有镜像仓库使用

```bash
docker tag registry:2 quay.iefcu.cn:9443/public/registry:2
docker push quay.iefcu.cn:9443/public/registry:2
docker pull quay.iefcu.cn:9443/public/registry:2
```

## 配置registry

参考[官方配置文档](https://docs.docker.com/registry/configuration/)
Override specific configuration options
In a typical setup where you run your Registry from the official image, you can specify a configuration variable from the environment by passing -e arguments to your docker run stanza or from within a Dockerfile using the ENV instruction.

To override a configuration option, create an environment variable named REGISTRY_variable where variable is the name of the configuration option and the _ (underscore) represents indention levels. For example, you can configure the rootdirectory of the filesystem storage backend:

```
storage:
  filesystem:
    rootdirectory: /var/lib/registry
```
To override this value, set an environment variable like this:

```
REGISTRY_STORAGE_FILESYSTEM_ROOTDIRECTORY=/somewhere
```

#### 配置只读仓库

docker-compose配置环境变量
```
REGISTRY_STORAGE_MAINTENANCE_READONLY_ENABLED: 'true'
```
报错: panic: readonly config key must contain additional keys

查找资料验证发现配置如下即可: https://github.com/distribution/distribution/issues/1736
```
REGISTRY_STORAGE_MAINTENANCE_READONLY: "{'enable': 'true'}"
```

#### 配置权限认证

生成htpasswd认证文件, 然后配置registry开启htpasswd认证
```
htpasswd -c -B -b users.htpasswd admin xxx
```

使用docker-compose参数
```
- ./registry/users.htpasswd:/auth/users.htpasswd:Z

REGISTRY_AUTH: 'htpasswd'
REGISTRY_AUTH_HTPASSWD_REALM: 'Registry Realm'
REGISTRY_AUTH_HTPASSWD_PATH: /auth/users.htpasswd
```

使用命令行参数
```
-v /var/lib/registry_auth/:/auth/ \
-e "REGISTRY_AUTH=htpasswd" \
-e "REGISTRY_AUTH_HTPASSWD_REALM=Registry Realm" \
-e "REGISTRY_AUTH_HTPASSWD_PATH=/auth/users.htpasswd" \
```

## docker registry v2协议使用

```
curl http://127.0.0.1:5000/v2

# 查询分类
curl http://127.0.0.1:5000/v2/_catalog
```

* 查询镜像标签列表

curl http://127.0.0.1:5000/v2/kcp/kylin-operator-index/tags/list

#### 删除镜像

搜索关键字《curl 删除registry镜像》《skopeo 删除registry镜像》
https://m.tongfu.net/home/35/blog/513697.html

思路
* 使用registry v2 api来处理
* 使用skopeo工具处理
* 新建registry, 只保留需要的镜像?

https://codeleading.com/article/9341997515/
3、使用delete-docker-registry-image进行删除镜像


配置registry允许删除
https://github.com/distribution/distribution/issues/1573

REGISTRY_STORAGE_DELETE_ENABLED=true

https://m.tongfu.net/home/35/blog/513697.html
2.8 垃圾回收
```
docker exec registry bin/registry garbage-collect /etc/docker/registry/config.yml
```

设置config.yml，在storage节点添加delete配置设置为true。
```
storage:
  delete:
    enabled: true
```

关键字《curl 删除registry镜像》

坑挺多, 尝试用skopeo来删除

(注意: 可能需要配置信任http仓库)
```
skopeo delete docker://localhost:5000/kcp/kylin-operator-index:v4.9
```

https://dockone.io/question/1227
registry v2 删除镜像后，catalog仍然可以看到，如何解决


暴力方法

## 使用quay搭建

TODO:

## 参考文档

* https://docs.docker.com/registry/deploying/
