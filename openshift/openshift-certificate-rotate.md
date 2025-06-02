# openshift 证书轮换

controller-manager 访问 apiserver, 需要提供客户端证书, 有效期默认为30天

=> 验证升级release => 未成功? => 原来是node没有ready，就不会升级
```
oc adm upgrade --force --to-image hub.iefcu.cn/xiaoyun/ocp-build:tmp-4.9.25-x86-apiserver-operator --allow-explicit-upgrade
oc adm upgrade --force --to-image hub.iefcu.cn/xiaoyun/ocp-build:tmp-4.9.25-x86-controller-manager-operator --allow-explicit-upgrade
oc get clusterversion # 查看升级过程
```

#### 待整理

直接修改这个镜像pods的配置文件，修改容器镜像
/etc/kubernetes/manifests/kube-apiserver-pod.yaml

#### 控制平面ca证书

=> 为啥变为两个月有效期了?
```
oc get secret kube-control-plane-signer -n openshift-kube-apiserver-operator -o yaml
```

#### oc 访问 apiserver证书

#### scheduler证书

```
oc get secret kube-scheduler-client-cert-key -n openshift-kube-scheduler -o jsonpath='{.data.tls\.crt}' | base64 -d | openssl x509 -noout -text | head
```

#### controller-manager

证书路径
(zhouming找到的宿主机路径)
```
sudo openssl x509 -noout -text -in /etc/kubernetes/static-pod-resources/kube-controller-manager-certs/secrets/kube-controller-manager-client-cert-key/tls.crt
    Issuer: CN = openshift-kube-apiserver-operator_kube-control-plane-signer@1826681260
    Subject: CN = system:kube-controller-manager

oc get secret kube-controller-manager-client-cert-key -n openshift-kube-controller-manager -o yaml
oc get secret kube-controller-manager-client-cert-key -n openshift-config-managed -o yaml
```

证书生成(论转)机制
- kube-apiserver-cert-regeneration-controller
  => 生成 secret/kube-controller-manager-client-cert-key -n openshift-config-managed
  源码: https://github.com/openshift/cluster-kube-apiserver-operator.git: certrotationcontroller.go: newCertRotationController
- kube-controller-manager-recovery-controller
  => 同步为 secret/kube-controller-manager-client-cert-key -n openshift-kube-controller-manager
- kube-controller-manager-cert-syncer
  => 同步为证书文件: tls.crt
- kube-controller-manager
  => 最终使用证书文件

#### 证书签名层级

- 10年CA证书
- 1年控制平面ca证书?
  自签名
```
oc get secret kube-control-plane-signer -n openshift-kube-apiserver-operator -o jsonpath='{.data.tls\.crt}' | base64 -d | openssl x509 -noout -text | head
Issuer: CN=openshift-kube-apiserver-operator_kube-control-plane-signer@1794967869
Subject: CN=openshift-kube-apiserver-operator_kube-control-plane-signer@1794967869
```
  => 只有一个? 删除虽然secret会重建，时间也会更新，但是并不会触发真正的重建一系列的证书!
- 1个月controller-manager访问证书?

#### openshift 证书配置

https://docs.redhat.com/en/documentation/openshift_container_platform/4.9/html/security_and_compliance/configuring-certificates

pkg/operator/certrotationcontroller/certrotationcontroller.go
https://github.com/openshift/cluster-kube-controller-manager-operator.git
https://github.com/openshift/cluster-kube-apiserver-operator.git
=> notAfter 关键字去修改?

=> 禁用掉此容器则不会续期! kube-controller-manager-recovery-controller (镜像kube-controller-manager-operator)
   cmd: cert-recovery-controller

猛然间发现，是从这个secret同步过来的吗, openshift-config-managed => openshift-kube-controller-manager
```
oc get secret kube-controller-manager-client-cert-key -n openshift-config-managed -o yaml # apiserver-cert-regenrate 容器会生成它
oc get secret kube-controller-manager-client-cert-key -n openshift-kube-controller-manager -o yaml # 从上面的容器同步过来!
```

考虑变为100年, 一年, 十年?

## FAQ

#### etcd证书都过期了

gpt《openshift节点关机很久之后，证书过期了，没有自动生成》

思路:
- 先在虚拟机中安装好系统, 然后将物理机器节点时间改变，启动虚拟机, 模拟关机很久的场景
- 将时间改回去，然后慢慢加回来? => 不是很合适

查看证书时间
```
openssl x509 -in /etc/kubernetes/static-pod-resources/etcd-certs/secrets/etcd-all-certs/etcd-serving-master1.crt -noout -dates
```

清除旧证书, 重启kubelet, 等待新证书生成
```
mv /etc/kubernetes/static-pod-resources/etcd-certs /etc/kubernetes/static-pod-resources/etcd-certs.bak
systemctl restart kubelet
ls /etc/kubernetes/static-pod-resources/etcd-certs/
```

关键字《openshift etcd certificate expired》

https://www.reddit.com/r/openshift/comments/17x96vh/etcd_certificates_are_expired/
=> 一位老哥就是改机器时间
```
I solved this issue.

1.disable datetime sync
2.set date before certs expiration date on all etcd nodes
3.renew certs https://access.redhat.com/solutions/7025431
4.enable datetime sync
```

https://docs.redhat.com/en/documentation/openshift_container_platform/4.9/html/backup_and_restore/control-plane-backup-and-restore#dr-recovering-expired-certs
redhat官方文档 => 还是不行，上面都是基于oc命令可以用的情况的处理

改了时间，kubeapi本来还是过期的，过一会儿，自己好了，继期新证书了!
=> 但是oc get nodes还是NotReady
```
oc get csr | grep pending -i | awk '{print $1}' | sed 's/^/kubectl certificate approve /' | bash
oc adm certificate approve csr-jb97k # => kubelet的正式是用这个!
csr-5c4cg
```

只要etcd证书正常，这个证书会轮转更新的!
```
[core@master1 ~]$ oc get pods
Unable to connect to the server: x509: certificate has expired or is not yet valid: current time 2025-05-21T06:59:54Z is after 2025-01-26T12:03:13Z
[core@master1 ~]$ oc get pods
No resources found in 1020-test namespace.
```

## kubelet证书

systemctl cat kubelet , 发现参数中这个证书有效期只有1个月!
/var/lib/kubelet/pki/kubelet-client-current.pem

openshift中的kubelet源码是这个?
https://github.com/openshift/machine-config-operator

TODO: 根据approve作为入口，看逻辑?

可以查看oc get csr -o yaml 里面的信息
如下命令可以查看 csr `CERTIFICATE REQUEST`的信息
```
openssl req -in your_request.csr -noout -text
```

journalctl -b看到这样的日志
```
certificate signing request csr-kthh7 is approved
...
master1.kcp4.iefcu.cn hyperkube[1960]: I0531 03:00:20.131352    1960 certificate_manager.go:270] kubernetes.io/kube-apiserver-client-kubelet: Certificate expiration is 2025-06-30 02:55:19 +0000 UTC, rotation deadline is 2025-06-25 17:17:56.868848081 +0000 UTC
master1.kcp4.iefcu.cn hyperkube[1960]: I0531 03:00:20.131403    1960 certificate_manager.go:270] kubernetes.io/kube-apiserver-client-kubelet: Waiting 614h17m36.737448699s for next certificate rotation
```

自动approve的，是这样? 到底是哪个源码通过的, 签发的?
```
csr-sznjl                                        18m     kubernetes.io/kube-apiserver-client-kubelet   system:node:master1.kcp4.iefcu.cn                                                 <none>              Approved,Issued                                                                                                                                                                                          
```

源码发现 https://github.com/openshift/kubernetes : pkg/controller/certificates/signer/signer.go
```
NewKubeletClientCSRSigningController
==> 发现controller-manager的启动参数中，有这个参数，指定了30天?
--experimental-cluster-signing-duration=720h
```

发现是在这个configmap中
```
/etc/kubernetes/static-pod-resources/kube-controller-manager-pod-4/configmaps/config/config.yaml
oc get configmap config -n openshift-kube-controller-manager
oc edit configmap config -n openshift-kube-controller-manager # 尝试修改, 会被覆盖
```

AI说是controller-manager 签发的kubelet证书，停止controller-manager容器，确实没有签发了!
=> 但是改了那个参数，居然只签发了两天有效期的证书。。。

关键点：SigningPolicy 限制了最大证书 TTL

## apiserver容器中的证书

- 自己?
```
/etc/kubernetes/static-pod-resources/kube-apiserver-certs/secrets/service-network-serving-certkey/tls.crt
=> /etc/kubernetes/static-pod-certs/secrets/service-network-serving-certkey/tls.crt
```

- kubelet-client
```
/etc/kubernetes/static-pod-resources/kube-apiserver-certs/secrets/kubelet-client/tls.crt
=> 容器内 /etc/kubernetes/static-pod-certs/secrets/kubelet-client/tls.crt
```

- aggregator-client (proxy-client)
```
/etc/kubernetes/static-pod-resources/kube-apiserver-certs/secrets/aggregator-client/tls.crt
=> 容器内 /etc/kubernetes/static-pod-certs/secrets/aggregator-client/tls.crt
```

其他(都容器内路径)
```
sudo openssl x509 -noout -dates -in /etc/kubernetes/static-pod-resources/kube-apiserver-certs/secrets/localhost-serving-cert-certkey/tls.crt
"certFile": "/etc/kubernetes/static-pod-certs/secrets/localhost-serving-cert-certkey/tls.crt",
"certFile": "/etc/kubernetes/static-pod-certs/secrets/service-network-serving-certkey/tls.crt",
"certFile": "/etc/kubernetes/static-pod-certs/secrets/external-loadbalancer-serving-certkey/tls.crt",
"certFile": "/etc/kubernetes/static-pod-certs/secrets/internal-loadbalancer-serving-certkey/tls.crt",
"certFile": "/etc/kubernetes/static-pod-resources/secrets/localhost-recovery-serving-certkey/tls.crt",
```

## 单节点静态pods列表

```
etcd-health-monitor
etcd-metrics
etcd
etcdctl
kube-apiserver-check-endpoints
kube-apiserver-insecure-readyz
kube-apiserver-cert-regeneration-controller
kube-scheduler-recovery-controller
kube-scheduler-cert-syncer
kube-apiserver-cert-syncer
kube-controller-manager-recovery-controller
kube-scheduler
kube-apiserver
kube-controller-manager-cert-syncer
cluster-policy-controller
kube-controller-manager

kube-controller-manager-master1.kcp4.iefcu.cn    openshift-kube-controller-manager
openshift-kube-scheduler-master1.kcp4.iefcu.cn   openshift-kube-scheduler
kube-apiserver-master1.kcp4.iefcu.cn             openshift-kube-apiserver
etcd-master1.kcp4.iefcu.cn                       openshift-etcd

etcd-pod.yaml  kube-apiserver-pod.yaml  kube-controller-manager-pod.yaml  kube-scheduler-pod.yaml
```
