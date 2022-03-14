# 容器pid max limit限制配置

之前通过s2i构建console镜像时，发现有pid limit有1024这个限制，导致build失败。

关键字《openshift build pid limits》

找到openshift有pidsLimit这个配置，可以修改，待验证一下。

https://computingforgeeks.com/change-pids-limit-value-in-openshift/

## 通过machine config修改crio默认pid limit限制

还可以直接修改/etc/crio/crio.conf配置生效，但不推荐这么做

#### 查看当前crio的pid limit限制

```bash
sudo crio-status config | grep pid
```

#### 1. 配置ContainerRuntimeConfig资源

```bash
cat <<EOF | oc apply -f -
apiVersion: machineconfiguration.openshift.io/v1
kind: ContainerRuntimeConfig
metadata:
 name: custom-pidslimit
spec:
 machineConfigPoolSelector:
   matchLabels:
     custom-crio: custom-pidslimit
 containerRuntimeConfig:
   pidsLimit: 4096
EOF
```

确认资源创建成功
```bash
oc get ctrcfg
NAME               AGE
custom-pidslimit   44s
```

#### 2. 配置machineConfigPool使用ctrcfg资源

目前仅仅对worker配置池配置了这个资源，只会影响到worker节点
```bash
oc edit machineconfigpool worker

apiVersion: machineconfiguration.openshift.io/v1
kind: MachineConfigPool
metadata:
  creationTimestamp: "2020-07-15T08:29:58Z"
  generation: 7
  labels:
    custom-crio: custom-pidslimit      #add this line
```

确保一个新的99-worker-XXX-containerruntime资源创建成功
```bash
oc get machineconfigs | grep containerruntime

99-worker-generated-containerruntime               d2d236b1952843821602ec36cd5817e72fd0a407   3.2.0             20s
```

检查mcp是否应用成功
```
oc get mcp

NAME     CONFIG                                             UPDATED   UPDATING   DEGRADED   MACHINECOUNT   READYMACHINECOUNT   UPDATEDMACHINECOUNT   DEGRADEDMACHINECOUNT   AGE
master   rendered-master-bcb9ae07a69c839a0ae8926ec597a5e1   True      False      False      3              3                   3                     0                      25d
worker   rendered-worker-b102b400a1c9bdc23344988e3c24a4d2   False     True       False      2              0                   0                     0                      25d
```

* UPDATING值为True，表示正在处理
* MACHINECOUNT值为2，表示总共有2个worker节点需要处理


## 参考资料

* [change-pids-limit-value-in-openshift](https://computingforgeeks.com/change-pids-limit-value-in-openshift/)
* [redhat machine config tasks](https://docs.openshift.com/container-platform/4.7/post_installation_configuration/machine-configuration-tasks.html)
* [redhat container machine config](https://docs.openshift.com/container-platform/4.6/rest_api/machine_apis/containerruntimeconfig-machineconfiguration-openshift-io-v1.html)
* [cri-o change default pid limit to 4096](https://github.com/cri-o/cri-o/issues/1921)
