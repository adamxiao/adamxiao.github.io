# machine config配置节点使用以及原理

## TODO: 疑问，待验证

* registry.conf配置了，那imagemirrorsource怎么融合呢？
* 配置冲突的场景(手动修改了)
* 禁止配置更新重启功能，有必要开启这个功能吗？
* 安装时就禁用selinux?

## machine config原理架构

![](../imgs/machine-config-arch.png)

主要组件
* MC-operator: 管理MC相关组件
* MC-Server: master节点上的daemonset, 提供ign给新节点使用
* MC-Controller: deployment, 只有一个副本，有Template, Render, Update, Kubelet等控制器
* MC-Daemon: 每个节点都有，处理MC升级重启等操作

![](../imgs/machine-config-pool.png)

相关MC配置对象
* MC-Pool: 连接一类配置与一类节点
* MC-config: 一个个小配置
* Node: 节点, 有不同的角色等

## 可以修改的配置项目

* crio配置
* kubelet配置
* ssh key
* 修改内核参数，禁用selinux

## 其他技巧

#### 禁止配置更新重启

在OpenShift中，节点配置是放在MachineConfig对象中，当MachineConfigPool发现MachineConfig就会将新的配置实施于对应节点上，随后重启节点使其生效。OpenShift的MachineConfigPool自动发现更新并重启的特性是缺省的，不过我们可以关闭其重启节点的特性，以允许在自定义时间窗口任工手动重启节点来生效配置的变更。

先获取到所有的mcp
```bash
 oc get machineconfigpool
NAME     CONFIG                                             UPDATED   UPDATING   DEGRADED   MACHINECOUNT   READYMACHINECOUNT   UPDATEDMACHINECOUNT   DEGRADEDMACHINECOUNT   AGE
master   rendered-master-9fdc47376528cf0bc9a62cb0ace3ca02   True      False      False      3              3                   3                     0                      5d1h
worker   rendered-worker-c5c84aa7ee855b4fc508fc82527efbf5   True      False      False      2              2                   2                     0                      5d1h
```

然后禁用自动重启的功能
```
oc patch --type=merge--patch='{"spec":{"paused":true}}' machineconfigpool/master
oc patch --type=merge--patch='{"spec":{"paused":true}}' machineconfigpool/worker
```

#### 禁用selinux

(selinux在点火文件中，还是machineconfig配置)
```
cat << EOF > 05-worker-kernelarg-selinuxoff.yaml
apiVersion: machineconfiguration.openshift.io/v1
kind: MachineConfig
metadata:
  labels:
    machineconfiguration.openshift.io/role: worker
  name: 05-worker-kernelarg-selinuxoff
spec:
  config:
    ignition:
      version: 3.2.0
  kernelArguments:
    - selinux=0
EOF
```

启用实时核
```
cat << EOF > 99-worker-realtime.yaml
apiVersion: machineconfiguration.openshift.io/v1
kind: MachineConfig
metadata:
  labels:
    machineconfiguration.openshift.io/role: "worker"
  name: 99-worker-realtime
spec:
  kernelType: realtime
EOF
```

## 参考文档

* [OpenShift 4 - 如何用Machine Config Operator修改集群节点CoreOS的配置](https://blog.csdn.net/weixin_43902588/article/details/108309209)
* [OpenShift 4 - 定制 RHCOS Linux的Kernal参数](https://blog.csdn.net/weixin_43902588/article/details/117198142)
* [OpenShift 4 - 设置集群节点和Pod容器的时间和时区](https://blog.csdn.net/weixin_43902588/article/details/108298517)
