# 定制安装部署kcp技巧

可以在安装阶段就配置好集群的时间同步服务器，
以及禁用selinux等配置

## 安装阶段配置好时间同步服务器

参考: [OpenShift 4 - 设置集群节点和Pod容器的时间和时区](https://blog.csdn.net/weixin_43902588/article/details/108298517)

生成时间同步chrony的machineconfig配置yaml文件,

在OpenShift的BareMetal的安装过程中可以在创建manifests目录和相关文件后，将上一节生成的“masters-chrony-configuration.yaml”和“99_workers-chrony-configuration.yaml”覆盖由以下“openshift-install create manifests 。。。”命令生成的缺省文件。

## kylin coreos禁用selinux简化安装步骤

参考: [OpenShift 4 - 定制 RHCOS Linux的Kernal参数](https://blog.csdn.net/weixin_43902588/article/details/117198142)

#### 生成master，worker的内核配置文件，放到点火文件的openshift目录中
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

#### 安装bootstrap节点, 使用selinux=0

livecd进入, 使用coreos-install安装, 添加selinux=0的内核参数

#### 安装master节点, 第一次启动grub界面增加selinux=0

livecd进入，正常安装系统，然后第一次启动grub界面添加selinux=0的参数

## 修改机器时间安装kcp

* 安装部署一个chronyd时间同步服务器，修改成指定时间, 提供时间同步服务
* 堡垒机使用时间同步服务器的时间进行同步，并生成点火文件
* 使用livecd进入系统，修改chronyd配置，同步成指定时间
* 修改bootstrap的点火文件，修改chronyd配置，同步成指定时间
* 修改ocp集群的时间同步服务器配置
* 最后安装系统即可，所有的节点时间都是预期的时间

## 参考文档
