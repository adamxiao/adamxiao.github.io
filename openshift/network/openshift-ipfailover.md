# 配置 IP 故障转移

关键点
9.3. 关于虚拟 IP 地址
* 可在集群外部配置的主机上访问。
* 不可用于集群中的任何其他目的。
* 最终通过vip访问集群里面的什么服务（或pod）?

这还是没看太懂，有其他使用配置指南文档么？

=> 什么意思, 非云集群?
9.8. ingressIP 的高可用性
在非云集群中，可以将 IP 故障转移和 ingressIP 合并到服务。其结果是，为使用 ingressIP 创建服务的用户提供了高可用性服务。

方法是指定一个 ingressIPNetworkCIDR 范围，然后在创建 ipfailover 配置时使用相同的范围。

由于 IP 故障转移最多可支持整个集群的 255 个 VIP，所以 ingressIPNetworkCIDR 需要为 /24 或更小。

## 其他使用例子

https://medoc.readthedocs.io/en/latest/docs/openshift/doc_reading/ipFailover.html
个人补充
NodePort 类型的服务
对于这类的服务，需要配置OPENSHIFT_HA_MONITOR_PORT为对应端口。

配备 externalIPs 的 ClusterIP 类型的服务
对于这类的服务，需要配置OPENSHIFT_HA_MONITOR_PORT为0。


https://blog.csdn.net/wangjianglinwan/article/details/104303941
就是讲了使用oc adm命令配置...
```
oc adm ipfailover --virtual-ips=<exposed-ip-address> --watch-port=<exposed-port> --replicas=<number-of-pods> --create
```

(好，验证验证吧!) https://docs.huihoo.com/openshift/origin-1.2/admin_guide/high_availability.html
Configuring a Highly-available Routing Service
Configuring a Highly-available Network Service


## 概述

IP 故障转移（IP failover）在一组节点上管理一个虚拟 IP（VIP）地址池。集合中的每个 VIP 都由从集合中选择的节点提供服务。只要单个节点可用，就会提供 VIP。无法将 VIP 显式分发到节点上，因此可能存在没有 VIP 的节点和其他具有多个 VIP 的节点。如果只有一个节点，则所有 VIP 都在其中。
=> 就是使用keepalived实现的

## 配置

创建 IP 故障转移服务帐户：

```
$ oc create sa ipfailover
```
为 hostNetwork 更新安全性上下文约束（SCC）：

```
$ oc adm policy add-scc-to-user privileged -z ipfailover
$ oc adm policy add-scc-to-user hostnetwork -z ipfailover
```

创建部署 YAML 文件来配置 IP 故障转移：
```
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ipfailover-keepalived
  labels:
    ipfailover: hello-openshift
spec:
  strategy:
    type: Recreate
  replicas: 2
  selector:
    matchLabels:
      ipfailover: hello-openshift
  template:
    metadata:
      labels:
        ipfailover: hello-openshift
    spec:
      serviceAccountName: ipfailover
      privileged: true
      hostNetwork: true
      nodeSelector:
        node-role.kubernetes.io/worker: ""
      containers:
      - name: openshift-ipfailover
        image: quay.io/openshift/origin-keepalived-ipfailover
        ports:
        - containerPort: 63000
          hostPort: 63000
        imagePullPolicy: IfNotPresent
        securityContext:
          privileged: true
        volumeMounts:
        - name: lib-modules
          mountPath: /lib/modules
          readOnly: true
        - name: host-slash
          mountPath: /host
          readOnly: true
          mountPropagation: HostToContainer
        - name: etc-sysconfig
          mountPath: /etc/sysconfig
          readOnly: true
        - name: config-volume
          mountPath: /etc/keepalive
        env:
        - name: OPENSHIFT_HA_CONFIG_NAME
          value: "ipfailover"
        - name: OPENSHIFT_HA_VIRTUAL_IPS # TODO: 为什么弄多个vip?
          value: "1.1.1.1-2"
        - name: OPENSHIFT_HA_VIP_GROUPS
          value: "10"
        - name: OPENSHIFT_HA_NETWORK_INTERFACE
          value: "ens3" #The host interface to assign the VIPs
        - name: OPENSHIFT_HA_MONITOR_PORT # TODO: 原因
          value: "30060"
        - name: OPENSHIFT_HA_VRRP_ID_OFFSET
          value: "0"
        - name: OPENSHIFT_HA_REPLICA_COUNT
          value: "2" #Must match the number of replicas in the deployment
        - name: OPENSHIFT_HA_USE_UNICAST
          value: "false"
        #- name: OPENSHIFT_HA_UNICAST_PEERS
          #value: "10.0.148.40,10.0.160.234,10.0.199.110"
        - name: OPENSHIFT_HA_IPTABLES_CHAIN
          value: "INPUT"
        #- name: OPENSHIFT_HA_NOTIFY_SCRIPT
        #  value: /etc/keepalive/mynotifyscript.sh
        - name: OPENSHIFT_HA_CHECK_SCRIPT
          value: "/etc/keepalive/mycheckscript.sh"
        - name: OPENSHIFT_HA_PREEMPTION
          value: "preempt_delay 300"
        - name: OPENSHIFT_HA_CHECK_INTERVAL
          value: "2"
        livenessProbe:
          initialDelaySeconds: 10
          exec:
            command:
            - pgrep
            - keepalived
      volumes:
      - name: lib-modules
        hostPath:
          path: /lib/modules
      - name: host-slash
        hostPath:
          path: /
      - name: etc-sysconfig
        hostPath:
          path: /etc/sysconfig
      # config-volume contains the check script
      # created with `oc create configmap keepalived-checkscript --from-file=mycheckscript.sh`
      - configMap:
          defaultMode: 0755
          name: keepalived-checkscript
        name: config-volume
      imagePullSecrets:
        - name: openshift-pull-secret
```

## 参考文档

* [配置 IP 故障转移](https://access.redhat.com/documentation/zh-cn/openshift_container_platform/4.9/html/networking/nw-ipfailover-configuration_configuring-ipfailover)
