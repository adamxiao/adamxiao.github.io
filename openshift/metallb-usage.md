# MetalLB安装以及使用方法

## metallb 重做支持arm64页面安装

mkdir -p /tmp/metallb-test/metallb-bundle-rootfs
oc image extract --confirm \
  --path /:/tmp/metallb-test/metallb-bundle-rootfs \
  hub.iefcu.cn/kcp/metallb-operator-bundle@sha256:549947c734afbb4fa16aa09293a92f30191270db67c3248847c58adcd7d54549

根据里面的dockerfile, 创建新的镜像, 注意修改支持arm64即可
hub.iefcu.cn/kcp/metallb-operator-bundle:v4.9

然后再做一个新的operator index镜像

可以在x86下制作arm64的operator index 镜像
```
opm index add \
    --bundles hub.iefcu.cn/kcp/metallb-operator-bundle@sha256:74da72dd402e5a85b2ece72695c6772dd56d771fc4e482719a9ffefe9fed89bc \
    --tag hub.iefcu.cn/kcp/kylin-operator-index:v4.9 \
    --binary-image hub.iefcu.cn/public/redhat-operator-index:v4.9@sha256:fd45ebb5619656628b84266793ddf24ef6a393cd3a85bc1b5315d5500c0bf067

    --bundles hub.iefcu.cn/kcp/metallb-operator-bundle:v4.9 \
```

使用镜像构建
```
docker run -it --privileged --rm hub.iefcu.cn/xiaoyun/podman-opm:amd64
```

或者使用docker构建, 需要下载opm二进制包

## 问题

#### 如何查看一个operator index有多少operator镜像(bundle)?

1.通过安装operator index之后再查看?
2.提取operator index的sqlite数据库文件查看? => 最准确, 核心就是整理
```bash
oc image extract --confirm \
  --path /database/index.db:/tmp \
  hub.iefcu.cn/public/redhat-operator-index:v4.9

sqlite3 ./index.db 'select * from main.related_image;' | grep pipelines | grep bundle
```
3.运行operator, 使用grpcurl查看

* hub.iefcu.cn/kcp/kylin-operator-index:v4.9
  openshift-jenkins-operator
* hub.iefcu.cn/kcp

#### 如何查看bundle镜像的related image?

#### 如何通过operator index的镜像?

oc adm catalog

## 简明安装部署步骤

#### 1. 同步镜像

TODO: 重要!!!
* xx
* xx


需要同步的镜像列表
* catalogsource镜像 => 很小
* bundle镜像 => 小
* operator相关镜像 => 大,重要

#### 2. 创建catalogSource

注意: 使用容器云平台能够拉取到的镜像仓库地址(因为这个镜像会频繁拉取更新的!)
例如: registry.kcp.local:5000

TODO: 可以直接通过页面的方式创建, 简单
进入 管理->自定义资源定义: 搜索catalogsource:
创建 CatalogSource:
* CatalogSource 名称: kylin
* 镜像: hub.iefcu.cn/kcp/kylin-operator-index:v4.9


```bash
cat << EOF | oc apply -f -
apiVersion: operators.coreos.com/v1alpha1
kind: CatalogSource
metadata:
  name: adam
  namespace: openshift-marketplace
spec:
  displayName: adam
  #image: 'hub.iefcu.cn/public/redhat-operator-index:v4.9'
  #image: 'hub.iefcu.cn/kcp/adam-operatorhub:20220224'
  image: 'registry.kcp.local:5000/kcp/redhat-operator-index:v4.9'
  publisher: adam
  sourceType: grpc
EOF
```

#### 3. 安装operator

通过页面安装, 不同的operator安装方法略有差别

## 安装方法

web控制台安装暂时还没弄好, 先用CLI安装

### CLI命令行安装

#### 1. 首先基于catalogSource镜像，创建catalogSource

```bash
cat << EOF | oc apply -f -
apiVersion: operators.coreos.com/v1alpha1
kind: CatalogSource
metadata:
  name: adam
  namespace: openshift-marketplace
spec:
  displayName: adam
  #image: 'hub.iefcu.cn/public/redhat-operator-index:v4.9'
  #image: 'hub.iefcu.cn/kcp/adam-operatorhub:20220224'
  image: 'registry.kcp.local:5000/kcp/redhat-operator-index:v4.9'
  publisher: adam
  sourceType: grpc
EOF
```

检查安装情况
```bash
oc -n openshift-marketplace get pod
oc -n openshift-marketplace get CatalogSource adam
```

#### 2. 然后创建镜像mirror策略

```bash
cat <<EOM | oc apply -f -
apiVersion: operator.openshift.io/v1alpha1
kind: ImageContentSourcePolicy
metadata:
  name: redhat-openshift4
spec:
  repositoryDigestMirrors:
  - mirrors:
    - hub.iefcu.cn/kcp
    - registry.kcp.local:5000/kcp
    source: registry.redhat.io/openshift4
EOM

cat <<EOM | oc apply -f -
apiVersion: operator.openshift.io/v1alpha1
kind: ImageContentSourcePolicy
metadata:
  name: hub-iefcu-cn-kcp
spec:
  repositoryDigestMirrors:
  - mirrors:
    - registry.kcp.local:5000/kcp
    source: hub.iefcu.cn/kcp
EOM
```

检查/etc/containers/registries.conf
是否有相应mirror配置

#### 3. 确认 MetalLB Operator 可用：

```
oc get packagemanifests -n openshift-marketplace metallb-operator
```

输出示例
```
NAME               CATALOG                AGE
metallb-operator   adam                   9h
```

#### 4. 创建 metallb-system 命名空间：

```
cat << EOF | oc apply -f -
apiVersion: v1
kind: Namespace
metadata:
  name: metallb-system
EOF
```

或者直接使用oc project命令创建
```
oc new-project metallb-system
```

#### 5. 在命名空间中创建一个 Operator 组自定义资源：

因为metallb operator必须要安装到一个指定的namespace中去。

```bash
cat << EOF | oc apply -f -
apiVersion: operators.coreos.com/v1
kind: OperatorGroup
metadata:
  name: metallb-operator
  namespace: metallb-system
spec:
  targetNamespaces:
  - metallb-system
EOF
```

#### 确认 Operator 组已安装在命名空间中：

```
oc get operatorgroup -n metallb-system
```

#### 订阅 MetalLB Operator。

```
cat << EOF| oc apply -f -
apiVersion: operators.coreos.com/v1alpha1
kind: Subscription
metadata:
  name: metallb-operator-sub
  namespace: metallb-system
spec:
  channel: stable
  name: metallb-operator
  source: adam
  sourceNamespace: openshift-marketplace
EOF
```

#### 确认安装计划位于命名空间中

```
oc get installplan -n metallb-system
```

如果没有出现installplane，就要查查olm operator的日志？

例如订阅到空的operator的日志
```
oc -n openshift-operator-lifecycle-manager logs -f catalog-operator-6565788966-rfzp7

I0403 03:32:33.072628       1 event.go:282] Event(v1.ObjectReference{Kind:"Namespace", Namespace:"", Name:"openshift-operators-redhat", UID:"5a
de5ab6-4a91-4372-acc4-19e99432c051", APIVersion:"v1", ResourceVersion:"129988", FieldPath:""}): type: 'Warning' reason: 'ResolutionFailed' cons
traints not satisfiable: no operators found from catalog redhat-operators in namespace openshift-marketplace referenced by subscription elastic
search-operator, subscription elasticsearch-operator exists
```

#### 要验证是否已安装 Operator，请输入以下命令：

```
oc get clusterserviceversion -n metallb-system \
  -o custom-columns=Name:.metadata.name,Phase:.status.phase
```

如果没有就，则看installplan的状态
可能是bundle任务失败，就会一直卡着。
oc -n openshift-marketplace get jobs d5d6cba0f745806d76d87f36482c281b250abd2eff473959d55d606b40d231a -o yaml
删除这个jobs是否可行？=> 确实可行!!!

## 在集群中启动 METALLB

#### 1. 创建 MetalLB 自定义资源的单一实例

**注意在metallb-system项目下运行此命令? 否则会没有作用！！！**
```bash
cat << EOF | oc apply -f -
apiVersion: metallb.io/v1beta1
kind: MetalLB
metadata:
  name: metallb
  namespace: metallb-system
EOF
```

#### 2. 检查控制器的部署是否正在运行：

```
oc get deployment -n metallb-system controller
```

#### 3. 检查 speaker 的守护进程集是否正在运行：

```
oc get daemonset -n metallb-system speaker
```

## 使用方法

#### 1. 首先配置地址池

```bash
cat << EOF | oc apply -f -
apiVersion: metallb.io/v1alpha1
kind: AddressPool
metadata:
  namespace: metallb-system
  name: doc-example
spec:
  protocol: layer2
  addresses:
  - 10.90.3.27-10.90.3.29
EOF
```

#### 2. 然后在service中使用这个地址池

```bash
cat << EOF | oc apply -f -
apiVersion: v1
kind: Service
metadata:
  name: traefik-ingress
  namespace: grzs-traefik
  labels:
    app: traefik
  annotations:
    metallb.universe.tf/address-pool: doc-example
spec:
  ports:
  - name: https
    protocol: TCP
    port: 443
    targetPort: 443
  - name: http
    protocol: TCP
    port: 80
    targetPort: 80
  type: LoadBalancer
  selector:
    app: traefik
EOF
```

#### 3. 最后查看svc自动分配的ip地址，以及访问

```bash
oc -n grzs-traefik get svc traefik-ingress
```

![](2022-03-01-15-41-29.png)


## 参考资料

[openshift官方文档 - 配置 METALLB 地址池](https://access.redhat.com/documentation/zh-cn/openshift_container_platform/4.9/html/networking/metallb-configure-address-pools)
