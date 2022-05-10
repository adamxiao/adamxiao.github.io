# traefik mesh监控应用api耗时

## traefik mesh安装

参考: [](../tricks/trafik-mesh.md)

#### 安装额外coredns

由于traefik mesh适配的是k8s, 对系统自带coredns做了一些逻辑, openshift安装这里简单取巧处理了.
(注: 这些coredns的部署配置是从traefik mesh helm repo中提取出来的)

```bash
cd openshift-extra-coredns
oc apply -f .

configmap/coredns created
W0509 08:49:43.392012  506353 warnings.go:70] spec.template.spec.nodeSelector[beta.kubernetes.io/os]: deprecated since v1.14; use "kubernetes.io/os" instead
deployment.apps/coredns created
clusterrole.rbac.authorization.k8s.io/traefik-mesh-coredns-role created
clusterrolebinding.rbac.authorization.k8s.io/traefik-mesh-coredns created
serviceaccount/traefik-mesh-coredns created
service/coredns created
```

检查安装结果(确认有coredns容器运行可用)
```bash
oc get pods -n kube-system

[core@master1 openshift-extra-coredns]$ oc get pods -n kube-system
NAME                       READY   STATUS    RESTARTS   AGE
coredns-7749d5679c-27nt6   1/1     Running   0          94s
coredns-7749d5679c-5k4zd   1/1     Running   0          94s
```

#### 配置openshift的dns融合

由于安装的traefik mesh只会适配修改kube-system项目下的coredns,
要想所有pod都能使用traefik mesh的服务, 需要与openshift的dns融合

参考: [redhat官方文档: 使用 DNS 转发](https://access.redhat.com/documentation/zh-cn/openshift_container_platform/4.9/html-single/networking/index#nw-dns-forward_dns-operator)

注意修改upstream的ip地址为coredns服务的ip地址
```bash
oc edit dns.operator/default

# 注意配置upstream的地址为新的coredns的svc地址
# XXX: 使用 coredns.kube-system.svc.cluster.local 试试?
# 不行: plugin/forward: not an IP address or file: "coredns.kube-system.svc.cluster.local"

  servers:
  - forwardPlugin:
      upstreams:
      - 172.30.201.135
    name: traefik-mesh
    zones:
    - traefik.mesh
```

#### helm安装traefik mesh

我已经提前下载好traefik mesh的repo配置文件了, 并修改了镜像地址
(前提: 安装[helm](https://mirror.openshift.com/pub/openshift-v4/x86_64/clients/helm/3.7.1/helm-linux-arm64.tar.gz))

```bash
helm install traefik-mesh traefik-mesh

[core@master1 traefik-mesh-asserts]$ ~/helm install traefik-mesh traefik-mesh
WARNING: Kubernetes configuration file is group-readable. This is insecure. Location: /var/home/core/.kube/config
W0509 09:05:32.031118  527555 warnings.go:70] policy/v1beta1 PodDisruptionBudget is deprecated in v1.21+, unavailable in v1.25+; use policy/v1 PodDisruptionBudget
W0509 09:05:32.034013  527555 warnings.go:70] policy/v1beta1 PodDisruptionBudget is deprecated in v1.21+, unavailable in v1.25+; use policy/v1 PodDisruptionBudget
W0509 09:05:32.036307  527555 warnings.go:70] policy/v1beta1 PodDisruptionBudget is deprecated in v1.21+, unavailable in v1.25+; use policy/v1 PodDisruptionBudget
W0509 09:05:32.038708  527555 warnings.go:70] policy/v1beta1 PodDisruptionBudget is deprecated in v1.21+, unavailable in v1.25+; use policy/v1 PodDisruptionBudget
W0509 09:05:32.142365  527555 warnings.go:70] policy/v1beta1 PodDisruptionBudget is deprecated in v1.21+, unavailable in v1.25+; use policy/v1 PodDisruptionBudget
W0509 09:05:32.143464  527555 warnings.go:70] policy/v1beta1 PodDisruptionBudget is deprecated in v1.21+, unavailable in v1.25+; use policy/v1 PodDisruptionBudget
W0509 09:05:32.143488  527555 warnings.go:70] policy/v1beta1 PodDisruptionBudget is deprecated in v1.21+, unavailable in v1.25+; use policy/v1 PodDisruptionBudget
W0509 09:05:32.143748  527555 warnings.go:70] policy/v1beta1 PodDisruptionBudget is deprecated in v1.21+, unavailable in v1.25+; use policy/v1 PodDisruptionBudget
NAME: traefik-mesh
LAST DEPLOYED: Mon May  9 09:05:31 2022
NAMESPACE: default
STATUS: deployed
REVISION: 1
TEST SUITE: None
NOTES:
Thank you for installing traefik-mesh.

Your release is named traefik-mesh.

To learn more about the release, try:

  $ helm status traefik-mesh
  $ helm get traefik-mesh
```

检查安装情况, 看traefik-mesh-proxy pod正常运行么
```bash
oc get pods

[core@master1 traefik-mesh-asserts]$ oc get pods
NAME                                      READY   STATUS    RESTARTS   AGE
grafana-core-5dd97947d-m2tqs              0/1     Pending   0          66s
jaeger-65f69db59f-44t4s                   1/1     Running   0          66s
prometheus-core-868cfc8454-44fdj          0/2     Pending   0          66s
traefik-mesh-controller-8d775494d-ss5tp   1/1     Running   0          66s
traefik-mesh-proxy-hn2nq                  1/1     Running   0          66s
```

#### 测试traefik mesh

使用client, server服务进行测试

```bash
cd mesh-test
oc new-project test
oc adm policy add-scc-to-user anyuid -n test -z default
oc apply -f .
```

检查pod运行情况
```bash
[core@master1 mesh-test]$ oc -n test get pods
NAME                      READY   STATUS    RESTARTS   AGE
client-9647d9c88-5w4qs    1/1     Running   0          6m58s
server-64dc98f695-t27hb   1/1     Running   0          4s
server-64dc98f695-v5tmf   1/1     Running   0          4s
```

进入client pod, 访问server的服务
```bash
oc -n test rsh client-9647d9c88-5w4qs

sh-4.2$ curl server.test.svc.cluster.local
Hostname: server-64dc98f695-v5tmf
IP: 127.0.0.1
IP: ::1
IP: 10.128.0.108
IP: fe80::f0bf:20ff:fe76:dde0
RemoteAddr: 10.128.0.105:39504
GET / HTTP/1.1
Host: server.test.svc.cluster.local
User-Agent: curl/7.29.0
Accept: */*

sh-4.2$ curl server.test.traefik.mesh
Hostname: server-64dc98f695-t27hb
IP: 127.0.0.1
IP: ::1
IP: 10.128.0.20
IP: fe80::60cd:aaff:fe01:6fb2
RemoteAddr: 10.128.0.71:41500
GET / HTTP/1.1
Host: server.test.traefik.mesh
User-Agent: curl/7.29.0
Accept: */*
Accept-Encoding: gzip
Uber-Trace-Id: 0a0f1323b031565c:21ea016b63b027fa:0a0f1323b031565c:1
X-Forwarded-For: 10.128.0.18
X-Forwarded-Host: server.test.traefik.mesh
X-Forwarded-Port: 80
X-Forwarded-Proto: http
X-Forwarded-Server: traefik-mesh-proxy-hn2nq
X-Real-Ip: 10.128.0.18
```

在client pod里面循环请求client刷数据
```bash
while true; do curl server.test.traefik.mesh; done
```

#### 配置promethues抓取traefik mesh监控数据

前提条件: 开启用户应用监控

创建一个ServiceMonitor以便于prometrics发现这个target
(创建一个监控service)

```yaml
apiVersion: v1
kind: Service
metadata:
  labels:
    app: traefik-monitor
  name: traefik-monitor
  #namespace: default
spec:
  ports:
  - port: 8080
    protocol: TCP
    targetPort: 8080
    name: metrics
  selector:
    component: maesh-mesh
  type: ClusterIP
---
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  labels:
    k8s-app: traefik-monitor
  name: traefik-monitor
  #namespace: default
spec:
  endpoints:
  - interval: 30s
    port: metrics
    path: /metrics
    scheme: http
  selector:
    matchLabels:
      app: traefik-monitor
```

#### 查询traefik mesh监控数据

更多监控统计用法, 参考[promethues查询语句](./promethues-usage.md)

```bash
# 服务请求总数
traefik_service_requests_total
# 服务请求总耗时(单位: 秒)
traefik_service_request_duration_seconds_sum
# 以及更多监控数据
# traefik_service_request_duration_seconds_count
# traefik_service_request_duration_seconds_bucket
```

然后简单粗暴的通过总时间/总请求量, 得到接口平均耗时
```bash
traefik_service_request_duration_seconds_sum / traefik_service_request_duration_seconds_count

# 使用变量统计不同的service的接口平均耗时
rate(traefik_service_request_duration_seconds_sum{exported_service="$service"}[1m]) / rate(traefik_service_request_duration_seconds_count{exported_service="$service"}[1m])
```

## 同步traefik mesh等相关镜像

待同步的镜像就是traefik mesh的所有镜像

同步镜像脚本如下：
```bash
src_hub="hub.iefcu.cn"
dst_hub="127.0.0.1:5000"

cat > image-sync.json << EOF
{
    "${src_hub}": {
        "username": "TODO:username",
        "password": "TODO:passwd"
    }
    ,"${dst_hub}": {
        "username": "TODO:username",
        "password": "TODO:passwd"
        ,"insecure": true
    }
}
EOF

cat > image-sync-list.json << EOF
{
"${src_hub}/public/coredns:1.7.0":"${dst_hub}/traefik-mesh/coredns"
,"${src_hub}/public/traefik:v2.5":"${dst_hub}/traefik-mesh/traefik"
,"${src_hub}/public/traefik-mesh:v1.4.5":"${dst_hub}/traefik-mesh/traefik-mesh"
,"${src_hub}/public/jaegertracing-all-in-one:1.32":"${dst_hub}/traefik-mesh/jaegertracing-all-in-one"

,"${src_hub}/library/centos:7":"${dst_hub}/traefik-mesh/centos"
,"${src_hub}/public/containous-whoami:latest":"${dst_hub}/traefik-mesh/containous-whoami"
}
EOF

image-syncer --proc=6 --auth=./image-sync.json --images=./image-sync-list.json --namespace=public \
--registry=hub.iefcu.cn --retries=3
```

由于是同步到registry服务中, 还可以通过直接拷贝目录的方法进行处理, 最简单
```bash
# 首先停止目的registry服务
sudo systemctl stop kcp-registry

# 然后解压镜像包到regitry数据目录中
sudo tar -C /var/lib/registry -xzf traefik-mesh-img.tgz
```

#### 配置镜像mirror配置文件

TODO: 使用machine config配置
目前先直接手动配置
配置使用之前同步到的镜像

注意编写mirror配置文件后，要通知crio生效`systemctl reload crio`
```bash
# 切到root执行
cat > /etc/containers/registries.conf.d/traefik-mesh-mirror.conf << EOF
[[registry]]
  prefix = ""
  location = "hub.iefcu.cn/public/coredns"

  [[registry.mirror]]
    location = "registry.kcp.local:5000/traefik-mesh/coredns"
    insecure = true

[[registry]]
  prefix = ""
  location = "hub.iefcu.cn/public/traefik"

  [[registry.mirror]]
    location = "registry.kcp.local:5000/traefik-mesh/traefik"
    insecure = true

[[registry]]
  prefix = ""
  location = "hub.iefcu.cn/public/traefik-mesh"

  [[registry.mirror]]
    location = "registry.kcp.local:5000/traefik-mesh/traefik-mesh"
    insecure = true

[[registry]]
  prefix = ""
  location = "hub.iefcu.cn/public/jaegertracing-all-in-one"

  [[registry.mirror]]
    location = "registry.kcp.local:5000/traefik-mesh/jaegertracing-all-in-one"
    insecure = true

[[registry]]
  prefix = ""
  location = "hub.iefcu.cn/library/centos"

  [[registry.mirror]]
    location = "registry.kcp.local:5000/traefik-mesh/centos"
    insecure = true

[[registry]]
  prefix = ""
  location = "hub.iefcu.cn/public/containous-whoami"

  [[registry.mirror]]
    location = "registry.kcp.local:5000/traefik-mesh/containous-whoami"
    insecure = true

EOF
```
