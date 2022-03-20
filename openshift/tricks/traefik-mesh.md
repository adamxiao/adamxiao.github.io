# traefik mesh安装配置使用

Traefik Mesh: Simpler Service Mesh

![](https://doc.traefik.io/traefik-mesh/assets/img/after-traefik-mesh-graphic.png)

## 基本安装

#### 安装要求

* Kubernetes 1.11+
* CoreDNS installed as Cluster DNS Provider (versions 1.3+ supported)
* Helm v3

#### 安装使用helm

参考 https://blog.csdn.net/weixin_43902588/article/details/104585541
```bash
wget https://mirror.openshift.com/pub/openshift-v4/x86_64/clients/helm/3.7.1/helm-linux-arm64.tar.gz
```

#### 离线安装traefik mesh

关键字《helm install offline》



```
helm repo add traefik-mesh https://helm.traefik.io/mesh

helm pull <chart name>
helm pull traefik-mesh/maesh

# 解压并修改traefik-mesh里面的镜像名称
tar -tzf traefik-mesh-4.0.2.tgz
# 修改values.yaml里面的镜像名称

# 安装
helm install traefik-mesh traefik-mesh

# 卸载
helm uninstall traefik-mesh traefik-mesh
```

![](2022-03-19-19-36-54.png)

发现traefik-mesh-controller容器运行不正常
![](2022-03-20-19-12-08.png)

使用cricrl查看init容器日志报错如下：
```
2022/03/20 09:44:46 command prepare error: unable to find suitable DNS provider: no supported DNS service available for installing traefik mesh
```

安装traefik mesh带coredns参数
```bash
helm install traefik-mesh traefik-mesh --set kubedns=true
```

TODO: openshift和traefik mesh的dns适配，需要处理。
关键字《openshift install extra coredns》

https://docs.okd.io/4.9/networking/dns-operator.html#nw-dns-forward_dns-operator

还不能伪造这个东西。。。
```bash
oc new-project kube-system
Error from server (Forbidden): project.project.openshift.io "kube-system" is forbidden: cannot request a project starting with "kube-"

cat << EOF | oc create -f -
apiVersion: v1
kind: Namespace
metadata:
  name: kube-system
EOF

Error from server (AlreadyExists): error when creating "create-kube-system.yaml": namespaces "kube-system" already exists
```

伪造了一个coredns之后，系统服务pod都正常了。
```bash
oc -n kube-system get pods
NAME                       READY   STATUS    RESTARTS   AGE
coredns-546ddf8bd9-4kmkd   1/1     Running   0          3m47s
coredns-546ddf8bd9-d5t59   1/1     Running   0          3m47s

[core@master1 templates]$ oc get pods
NAME                                      READY   STATUS    RESTARTS        AGE
glusterfs-d9sms                           1/1     Running   0               5h11m
grafana-core-5dd97947d-z4kz7              1/1     Running   1 (4h34m ago)   4h36m
heketi-7d855c7597-qgwrs                   1/1     Running   0               5h4m
jaeger-65f69db59f-f9nzm                   1/1     Running   0               4h36m
prometheus-core-868cfc8454-7fkn4          2/2     Running   0               4h36m
traefik-mesh-controller-8d775494d-krkln   1/1     Running   0               4h36m
traefik-mesh-proxy-s2pz8                  1/1     Running   0               4h36m
```

## 参考文档

* [traefik-mesh](https://doc.traefik.io/traefik-mesh/)
* [[Hands-on Lab (2) - 使用Helm部署OpenShift应用](https://blog.csdn.net/weixin_43902588/article/details/104585541)
