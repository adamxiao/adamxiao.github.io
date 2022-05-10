# openshift用内置的Prometheus监控应用

openshift默认promethues只是用来监控系统服务，监控用户应用需要配置启用新的内置promethues

## 配置Prometheus环境

#### 打开enableUserWorkload功能

创建一个ConfigMap对象，打开“enableUserWorkload”功能。
```yaml
cat << EOF | oc apply -f -
apiVersion: v1
kind: ConfigMap
metadata:
  name: cluster-monitoring-config
  namespace: openshift-monitoring
data:
  config.yaml: |
    enableUserWorkload: true
EOF
```


查看openshift-user-workload-monitoring项目中增加的Pod，这3个Pod就是OpenShift用来对项目级的应用进行监控的Prometheus环境。
```bash
[core@master1 traefik-mesh-asserts]$ oc get pod -n openshift-user-workload-monitoring
NAME                                   READY   STATUS    RESTARTS   AGE
prometheus-operator-5dcbd9b9db-pbngh   2/2     Running   0          17s
prometheus-user-workload-0             5/5     Running   0          13s
thanos-ruler-user-workload-0           3/3     Running   0          10s
```

## 部署被监控应用

XXX: TODO:

## 创建收集指标的角色，并为用户赋予该角色

#### 创建收集指标的角色

```bash
cat << EOF | oc apply -f -
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: monitor-crd-edit
rules:
- apiGroups: ["monitoring.coreos.com"]
  resources: ["prometheusrules", "servicemonitors", "podmonitors"]
  verbs: ["get", "list", "watch", "create", "update", "patch", "delete"]
EOF
```

#### TODO: xxx

进入OpenShift 控制台的“管理员”视图，进入“用户管理” → “角色绑定”菜单。在确认当前是“所有项目”后点击“创建绑定”按钮。

在“创建 RoleBinding”页面中先将“绑定类型”设为“命名空间角色绑定（RoleBinding）”。然后为RoleBinding提供“名称”（例如my-role-binding-monitor）；再为“命名空间”选择刚刚部署应用的“monitored-app”项目。随后为“角色名称”选择“monitor-crd-edit”；为“主题”（Subject）选择“用户”类型，最后为“主题名称”（Subject Name）提供一个已有的OpenShift用户名（这里使用的是集群管理员）。随后点击“创建”按钮创建项目级RoleBinding对象。

## 其他

#### 查看内置user workload promethues页面

在新prome, thanos pod中可以看到配置生效了!
* /etc/prometheus/rules/prometheus-user-workload-rulefiles-0
* /etc/thanos/rules/thanos-ruler-user-workload-rulefiles-0

refer https://access.redhat.com/documentation/zh-cn/openshift_container_platform/4.9/html-single/monitoring/index
```bash
$ oc port-forward -n openshift-user-workload-monitoring pod/prometheus-user-workload-0 9090
$ oc port-forward -n openshift-user-workload-monitoring pod/prometheus-user-workload-0 --address 0.0.0.0 9090
```

可以在 Web 浏览器中打开 http://localhost:9090/targets，并在 Prometheus UI 中直接查看项目的目标状态。检查与目标相关的错误消息。
=> 可以看这个promethues的Rules等信息

## 参考资料

* [OpenShift 4 - 用内置的Prometheus监控应用](https://blog.csdn.net/weixin_43902588/article/details/105523603)
