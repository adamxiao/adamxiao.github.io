# bootstrap步骤细化

## 抽象步骤

[参考redhat官方文档](https://access.redhat.com/documentation/zh-cn/openshift_container_platform/4.9/html/installing/ocp-installation-overview#installation-process_ocp-installation-overview)

* 1. bootstrap 机器启动并开始托管 control plane 机器引导所需的远程资源。（如果自己配置基础架构，则需要人工干预）
* 2. bootstrap 机器启动单节点 etcd 集群和一个临时 Kubernetes control plane。
* 3. control plane 机器从 bootstrap 机器获取远程资源并完成启动。（如果自己配置基础架构，则需要人工干预）
* 4. 临时 control plane 将生产环境的 control plane 调度到生产环境 control plane 机器。
* 5. Cluster Version Operator（CVO）在线并安装 etcd Operator。etcd Operator 在所有 control plane 节点上扩展 etcd。
* 6. 临时 control plane 关机，并将控制权交给生产环境 control plane。
* 7. bootstrap 机器将 OpenShift Container Platform 组件注入生产环境 control plane。
* 8. 安装程序关闭 bootstrap 机器。（如果自己配置基础架构，则需要人工干预）
* 9. control plane 设置计算节点。
* 10. control plane 以一组 Operator 的形式安装其他服务。

## 1. bootstrap启动并托管control plane相关资源

#### bootstrap节点通过点火文件安装配置好系统

release-image服务, 下载release版本镜像

bootstrap点火文件配置, 有如下文件:
* /usr/local/bin/bootkube.sh
* /opt/openshift/manifests/...
...

bootstrap主要服务:
* release-image => 下载release镜像，提取相关release信息
* bootkube => 最重要的服务，bootstrap安装逻辑
* approve-csr => 通过node节点注册

## 2. bootstrap启动etcd单节点集群，以及临时k8s control plane

#### 启动etcd单节点集群

首先使用etcd operator镜像，提取出相关etcd yaml配置文件...
以及其他api,control-manager等, render
```
"${CLUSTER_ETCD_OPERATOR_IMAGE}" \
/usr/bin/cluster-etcd-operator render \
```

然后**kubelet**启动运行etcd单节点集群
(相当于kubelet启用运行静态pods?)
```
journalctl -b -u kubelet.service

bootstrap etcd manifest配置
/etc/kubernetes/manifests/etcd-member-pod.yaml

Apr 19 06:15:04 bootstrap.kcp5-arm.iefcu.cn kubelet.sh[2507]: I0419 06:15:04.987596    2519 kubelet.go:2076]
  "SyncLoop ADD" source="file" pods=[openshift-etcd/etcd-bootstrap-member-bootstrap.kcp5-arm.iefcu.cn]
```

手动检查一下bootstrap节点的etcd的状态?
```
podman run --quiet --net=host \
	--rm \
	--env ETCDCTL_API=3 \
	--volume /opt/openshift/tls:/opt/openshift/tls:ro,z \
	--entrypoint etcdctl \
	"hub.iefcu.cn/xiaoyun/openshift4-arm-4.9.15@sha256:aa5775988ff81d0000df88ae8a03121860ebfd8ba71f53171eddd7e6dbfabe57" \
	--dial-timeout=10m \
	--cacert=/opt/openshift/tls/etcd-ca-bundle.crt \
	--cert=/opt/openshift/tls/etcd-client.crt \
	--key=/opt/openshift/tls/etcd-client.key \
	--endpoints="https://localhost:2379" \
	endpoint health

# 或者使用member list命令查看节点集群状态
```

#### 启动临时k8s control plane

其实也是容器把apiserver,controller-manager等manifest放到/etc/kubernetes目录中，由kubelet服务拉起相关容器服务
```bash
echo "Starting cluster-bootstrap..."
run_cluster_bootstrap() {
	record_service_stage_start "cb-bootstrap"
	bootkube_podman_run \
        --name cluster-bootstrap \
        --rm \
        --volume "$PWD:/assets:z" \
        --volume /etc/kubernetes:/etc/kubernetes:z \
        "${CLUSTER_BOOTSTRAP_IMAGE}" \
        start --tear-down-early=false --asset-dir=/assets --required-pods="${REQUIRED_PODS}"
}
```

可以发现/etc/kubernetes/manifests, 会多处apiserver等yaml配置文件
```bash
ls /etc/kubernetes/manifests

# 发现多出controller等yaml配置文件，如果只有etcd，那就只有etcd的manifests
bootstrap-pod.yaml                  etcd-member-pod.yaml     kube-controller-manager-pod.yaml  machineconfigoperator-bootstrap-pod.yaml
cloud-credential-operator-pod.yaml  kube-apiserver-pod.yaml  kube-scheduler-pod.yaml
```

## 3. control plane 机器从 bootstrap 机器获取远程资源并完成启动

同bootstrap的获取点火文件安装配置系统
主要有配置二次启动, 先有machine-config-daemon-firstboot服务处理

##  4. 临时 control plane 将生产环境的 control plane 调度到生产环境 control plane 机器。

首先新的master节点会加入到k8s控制平面中来，bootstrap节点会自动通过加入请求
(approve-csr服务自动处理)

bootstrap节点的cluster version operator会部署apiserver的operator，
apiserver operator来安装部署apiserver容器服务

## 5. Cluster Version Operator（CVO）在线并安装 etcd Operator。etcd Operator 在所有 control plane 节点上扩展 etcd。

etcd operator会调度到
这些都是etcd operator的逻辑，调试查看还需要花很多时间才行。

## 6. 临时 control plane 关机，并将控制权交给生产环境 control plane。

bootstrap监控到生产控制平台apiserver等pod起来后，就会进行后续安装处理

```bash
REQUIRED_PODS="openshift-kube-apiserver/kube-apiserver,openshift-kube-scheduler/openshift-kube-scheduler,openshift-kube-controller-manager/kube-controller-manager,openshift-cluster-version/cluster-version-operator"
if [ "$BOOTSTRAP_INPLACE" = true ]
then
    REQUIRED_PODS=""
fi

echo "Starting cluster-bootstrap..."
run_cluster_bootstrap() {
	record_service_stage_start "cb-bootstrap"
	bootkube_podman_run \
        --name cluster-bootstrap \
        --rm \
        --volume "$PWD:/assets:z" \
        --volume /etc/kubernetes:/etc/kubernetes:z \
        "${CLUSTER_BOOTSTRAP_IMAGE}" \
        start --tear-down-early=false --asset-dir=/assets --required-pods="${REQUIRED_PODS}"
}
```

## 7. bootstrap 机器将 OpenShift Container Platform 组件注入生产环境 control plane。

#### cluster version operator配置override

```bash
oc patch clusterversion.config.openshift.io version \
	--kubeconfig=/opt/openshift/auth/kubeconfig \
	--type=merge \
	--patch-file=/opt/openshift/original_cvo_overrides.patch
```

```
spec:
  channel: stable-4.9
  clusterID: 6c08777b-262d-4a1e-bf30-58932d942266
  overrides:
  - group: ""
    kind: Namespace
    name: openshift-machine-config-operator
    namespace: ""
    unmanaged: true
  - group: ""
    kind: ConfigMap
    name: cluster-config-v1
    namespace: kube-system
    unmanaged: true
  - group: config.openshift.io
    kind: DNS
    name: cluster
    namespace: ""
    unmanaged: true
...
各种配置恢复覆盖配置
```

#### bootstrap etcd节点移除出etcd集群

operator的这个命令wait-for-ceo, 到底做了什么？
```
bootkube_podman_run \
	--name wait-for-ceo \
	--volume "$PWD:/assets:z" \
	"${CLUSTER_ETCD_OPERATOR_IMAGE}" \
	/usr/bin/cluster-etcd-operator \
	wait-for-ceo \
	--kubeconfig /assets/auth/kubeconfig
```

看了一下源码，wait-for-ceo就是等待etcd operator可用
```
func done(etcd *operatorv1.Etcd) (bool, error) {
    if operatorv1helpers.IsOperatorConditionTrue(etcd.Status.Conditions, "EtcdRunningInCluster") {
        klog.Info("Cluster etcd operator bootstrapped successfully")
        return true, nil
    }
}
```

最后没有发现etcd在bootstrap节点中被移除的逻辑代码，而且bootstrap节点还在启动etcd节点(有日志)
可能是etcd operator做的事情!
etcd operator的源码中确实也有移除bootstrap etcd成员的逻辑
```
func (c *BootstrapTeardownController) removeBootstrap(syncCtx factory.SyncContext) error {
    // checks the actual etcd cluster membership API if etcd-bootstrap exists
    safeToRemoveBootstrap, hasBootstrap, err := c.canRemoveEtcdBootstrap()
}
```

最后bootkube服务上报bootkube complete

## 参考文档
* [OPENSHIFT CONTAINER PLATFORM 安装概述](https://access.redhat.com/documentation/zh-cn/openshift_container_platform/4.9/html/installing/ocp-installation-overview#installation-process_ocp-installation-overview)
