# Keycloak认证安装使用

统一认证sso登录使用的

## 安装

有几种安装方式：
* docker
* docker-compose
* template方式
  keycloak官方文档指导这样安装到openshift平台上的
* operator (operatorhub)
  openshift operator好像没有!
* openshift sso(keycloak) => 建议使用这种！！

#### docker安装

docker 简单使用
```bash
docker run -d --name keycloak \
    -p 8090:8080 \
    -e KEYCLOAK_USER=admin \
    -e KEYCLOAK_PASSWORD=admin \
    hub.iefcu.cn/public/keycloak:10.0.0
```

为什么使用keycloak 10.0.0呢？
=> docker hub的有arm64平台的镜像

#### 使用docker-compose安装

初始化需要做的事情
* 1.证书配置
```bash
mkdir -p data/certs
tls.crt  tls.key
chmod 755 data/certs
chmod 604 data/certs/*
```

* 2.mysql数据目录初始化?
```
mkdir -p data/keycloak_db
```

* 3.其他docker-compose.yaml自定义配置
域名，密码等

```yaml
version: '3.7'

networks:
  keycloak:
    name: keycloak
    external: false

services:
  keycloak:
    container_name: keycloak_app
    image: hub.iefcu.cn/public/tmp-keycloak:10.0.2
    depends_on:
      - mariadb
    restart: always
    ports:
      - "80:8080"
      - "443:8443"
    volumes:
      - "/data/keycloak/data/certs/:/etc/x509/https"   # map certificates to container
    environment:
      KEYCLOAK_USER: admin
      KEYCLOAK_PASSWORD: admin
      KEYCLOAK_HTTP_PORT: 80
      KEYCLOAK_HTTPS_PORT: 443
      KEYCLOAK_HOSTNAME: keycloak.iefcu.cn
      DB_VENDOR: mariadb
      DB_ADDR: mariadb
      DB_USER: keycloak
      DB_PASSWORD: password
    networks:
      keycloak:
        aliases:
          - keycloak

  mariadb:
    container_name: keycloak_db
    image: hub.iefcu.cn/public/mariadb
    volumes:
      - "/data/keycloak/data/keycloak_db:/var/lib/mysql"
    restart: always
    environment:
      MYSQL_ROOT_PASSWORD: password
      MYSQL_DATABASE: keycloak
      MYSQL_USER: keycloak
      MYSQL_PASSWORD: password
    networks:
      keycloak:
        aliases:
          - mariadb
```

#### template安装(yaml)

```bash
oc new-project keycloak

oc process -f https://raw.githubusercontent.com/keycloak/keycloak-quickstarts/latest/openshift-examples/keycloak.yaml \
    -p KEYCLOAK_ADMIN=admin \
    -p KEYCLOAK_ADMIN_PASSWORD=admin \
    -p NAMESPACE=keycloak \
| oc create -f -
```

#### operator安装

```yaml
apiVersion: keycloak.org/v1alpha1
kind: Keycloak
metadata:
  name: example-keycloak
  labels:
   app: example-keycloak
spec:
  instances: 1
  externalAccess:
    enabled: True
```

#### openshift sso operator安装

=> 没有源码?

##### 订阅catalogSource(可选?)

订阅openshift的默认的operatorhub:
hub.iefcu.cn/public/redhat-operator-index:v4.9

可能需要先禁用已有的catalogSource
```bash
oc patch OperatorHub cluster --type json \
     -p '[{"op": "add", "path": "/spec/disableAllDefaultSources", "value": true}]'
```

然后开启自己的operatorhub
```yaml
cat << EOF | oc apply -f -
apiVersion: operators.coreos.com/v1alpha1
kind: CatalogSource
metadata:
  name: tmp
  namespace: openshift-marketplace
spec:
  displayName: tmp
  image: 'hub.iefcu.cn/public/redhat-operator-index:v4.9'
  #image: 'hub.iefcu.cn/kcp/logging-operator-index:v4.9'
  publisher: tmp
  sourceType: grpc
EOF
```

##### 获取到bundle镜像，然后xxx

获取到operator的名字: rhsso-operator

##### 尝试裁剪同步相关镜像

裁剪镜像
```bash
# 只保留logging，elasticserach operator
opm index prune -f hub.iefcu.cn/public/redhat-operator-index:v4.9 \
    -p rhsso-operator \
    -t hub.iefcu.cn/kcp/sso-operator-index:v4.9

# 并上传裁剪过后的hub镜像
podman push hub.iefcu.cn/kcp/sso-operator-index:v4.9
```

同步镜像
```bash
# 先同步到本地目录
mkdir mirror-sso-operator && cd mirror-sso-operator
oc adm catalog mirror \
    hub.iefcu.cn/kcp/sso-operator-index:v4.9 \
    -a /home/adam/tmp/pull-secret.json \
    file:///local/index

## info: Mirroring completed in 49m33.81s (3.559MB/s)
## error mirroring image: one or more errors occurred
## wrote mirroring manifests to manifests-sso-operator-index-1649916179
## 
## To upload local images to a registry, run:
## 
##         oc adm catalog mirror file://local/index/kcp/sso-operator-index:v4.9 REGISTRY/REPOSITORY


# 然后同步到私有镜像仓库
oc adm catalog mirror \
  file://local/index/kcp/sso-operator-index:v4.9 \
  192.168.120.44/kcp/sso-operator-index:v4.9 \
  -a /home/adam/tmp/pull-secret.json \
  --insecure
```

## 配置keycloak

## 配置作为openshift的认证源

openshift console使用keycloak认证

关键字《openshift use keycloak auth》 => 好

[Keycloak (as an Identity Provider) to secure Openshift](https://medium.com/keycloak/using-keycloak-identity-provider-to-secure-openshift-f929a7a0f7f1)

必须

## 参考资料

* [keycloak官方文档 - 安装到openshift](https://www.keycloak.org/getting-started/getting-started-openshift)
