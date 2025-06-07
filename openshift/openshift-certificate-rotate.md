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

安装时, bootstrap默认就生成了只有1年有效期的, 改apiserver-operator没有影响到这里。。。
  => 但是可以让它删除重建!(安装完后尝试成功)
  bootstrap节点上的证书位置: /etc/kubernetes/bootstrap-secrets/kube-control-plane-signer.crt

修改openshift-install源码, 将bootstrap.ign证书有效期延长
```
// Generate generates the root-ca key and cert pair.
func (c *KubeControlPlaneSignerCertKey) Generate(parents asset.Parents) error {
    cfg := &CertCfg{
        Subject:   pkix.Name{CommonName: "kube-control-plane-signer", OrganizationalUnit: []string{"openshift"}},
        KeyUsages: x509.KeyUsageKeyEncipherment | x509.KeyUsageDigitalSignature | x509.KeyUsageCertSign,
        Validity:  Validity99Years,
        IsCA:      true,
    }

    return c.SelfSignedCertKey.Generate(cfg, "kube-control-plane-signer")
}
```

=> 为啥变为两个月有效期了?
```
=> 是自签名的tls.crt, tls.key
oc get secret kube-control-plane-signer -n openshift-kube-apiserver-operator -o jsonpath='{.data.tls\.crt}' | base64 -d | openssl x509 -noout -text | head
        Version: 3 (0x2)
        Serial Number: 2048834006936142688 (0x1c6eebac932b4360)
        Signature Algorithm: sha256WithRSAEncryption
        Issuer: CN = openshift-kube-apiserver-operator_kube-control-plane-signer@1780668001
        Validity
            Not Before: Jun  5 14:00:01 2026 GMT
            Not After : May 25 14:00:02 2028 GMT
        Subject: CN = openshift-kube-apiserver-operator_kube-control-plane-signer@1780668001
```

安装节点是: /etc/kubernetes/bootstrap-secrets/kube-control-plane-signer.crt
=> 估计需要修改openshift-install，或者可以配置吗? 点火文件里面已经生成了这个证书

#### 根证书10年

```
[ssh_10.90.3.21] root@localhost: manifests$openssl x509 -noout -text -in kube-system-configmap-root-ca.yaml | head
Certificate:
    Data:
        Version: 3 (0x2)
        Serial Number: 5797259221592292138 (0x5074008bfdddbb2a)
    Signature Algorithm: sha256WithRSAEncryption
        Issuer: OU=openshift, CN=root-ca
        Validity
            Not Before: Jun  6 03:26:15 2025 GMT
            Not After : Jun  4 03:26:15 2035 GMT
        Subject: OU=openshift, CN=root-ca
```

签发证书 machine-config-server-tls-secret.yaml => 也是10年

#### oc 访问 apiserver证书

#### scheduler证书

```
oc get secret kube-scheduler-client-cert-key -n openshift-kube-scheduler -o jsonpath='{.data.tls\.crt}' | base64 -d | openssl x509 -noout -text | head
```

证书有效期上限: **不能超过签发ca证书的上限**
cluster-kube-apiserver-operator : vendor/github.com/openshift/library-go/pkg/operator/certrotation/target.go
```
func setTargetCertKeyPairSecret(targetCertKeyPairSecret *corev1.Secret, validity time.Duration, signer *crypto.CA, certCreator TargetCertCreator) error {
...
    // our annotation is based on our cert validity, so we want to make sure that we don't specify something past our signer
    targetValidity := validity
    remainingSignerValidity := signer.Config.Certs[0].NotAfter.Sub(time.Now())
    if remainingSignerValidity < validity {
        targetValidity = remainingSignerValidity
    }
```

#### controller-manager

=> 删除ca证书secret, 删除自己secret? => 验证可以!
```
oc delete secret kube-control-plane-signer -n openshift-kube-apiserver-operator
=> 然后确认证书生效
oc delete secret kube-controller-manager-client-cert-key -n openshift-config-managed
oc delete secret kube-scheduler-client-cert-key -n openshift-config-managed
```

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

## csr机制

- kubelet发起csr请求?
- oc 主动通过csr请求, 或者xxx自动通过csr请求?
- controller-manager 请求签发证书?
  证书请求有效期, controller-manager的参数 `experimental-cluster-signing-duration`, 由operator拉起定制的
  NewCertRotationController => operator中这个controller同样控制了证书论转策略

csr的ca证书是如下的(由controller-manager-operator处理):
=> 还需要修改apiserver-operator的证书论转控制器 `node-system-admin-signer`
```
oc get secret -A | grep csr
openshift-kube-controller-manager-operator         csr-signer-signer => 自签名
openshift-kube-controller-manager-operator         csr-signer => 由csr-signer-signer签名, 签发csr证书
openshift-kube-controller-manager                  csr-signer
```

## etcd证书延长

gpt《openshift 4.9中etcd的证书有效期默认是3年，延长改为10年，如何改》

https://github.com/openshift/cluster-etcd-operator.git
pkg/tlshelpers/tlshelpers.go
=> 改掉就行, 根据3年有效期这种关键字搜到的
=> 改成10年验证生效，改出99年试试 => 成功!
```
etcdCertValidity = 3 * 365 * 24 * time.Hour
```

## 其他证书

#### oc访问openshift apiserver 证书?

默认只有两年?
=> 后续自动更新了, 不用手动管!
```
oc get nodes
Unable to connect to the server: x509: certificate has expired or is not yet valid: current time 2028-06-06T10:52:08Z is after 2027-06-07T10:44:39Z
```

#### oauth web应用证书

xxx.apps.kcp4.iefcu.cn的证书
=> 由 ingress-operator@1749268763 签发
```
https://oauth-openshift.apps.kcp4.iefcu.cn/healthz
openssl s_client -connect oauth-openshift.apps.kcp4.iefcu.cn:443 -servername oauth-openshift.apps.kcp4.iefcu.cn -showcerts < /dev/null | openssl x509 -noout -text
        Issuer: CN = ingress-operator@1749268763
        Validity
            Not Before: Jun  7 04:05:05 2025 GMT
            Not After : Jun  7 04:05:06 2027 GMT
        Subject: CN = *.apps.kcp4.iefcu.cn
```

对应 openshift-ingress
```
oc get secret router-ca -n openshift-ingress-operator
```
=> 自签名证书, 有效期两年，过期后没有续期?
=> 删除了也没有重新创建?

最后删除pods，让它重新运行，生成了新的!
=> 但是xxx.apps证书还是没有更新。。。
```
oc delete pod -n openshift-ingress-operator -l name=ingress-operator
```

检查xxx.apps证书
```
oc get secret router-certs-default -n openshift-ingress -o jsonpath='{.data.tls\.crt}' | base64 -d | openssl x509 -noout -dates
```

删除secret居然不会续期，删除pod吧
=> 删除pods后证书续期了。。。
```
oc get pods -n openshift-ingress
```

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
```
sudo openssl x509 -noout -text -in /var/lib/kubelet/pki/kubelet-client-current.pem  | head -20
        Version: 3 (0x2)
        Serial Number:
            b0:81:d8:c0:4c:c0:43:4c:9a:32:20:24:73:15:cf:cc
        Signature Algorithm: sha256WithRSAEncryption
        Issuer: CN = kube-csr-signer_@1753952283
        Validity
            Not Before: Sep 27 00:03:48 2025 GMT
            Not After : Sep 29 08:58:03 2025 GMT
        Subject: O = system:nodes, CN = system:node:master1.kcp4.iefcu.cn
```

=> 改为一年生效，但是改为99年无效?
  => 考虑改一下ca证书的
```
Issuer: CN = kube-csr-signer_@1780713160
csr-signer-signer => csr-controller-signer-ca

oc get secret csr-signer-signer -n openshift-kube-controller-manager-operator -o jsonpath='{.data.tls\.crt}' | base64 -d | openssl x509 -noout -text | head
        Subject: CN = openshift-kube-controller-manager-operator_csr-signer-signer@1780711736
=> 好像不对? => 是更上层的自签名ca证书
```

=> 自签名 CN = openshift-kube-controller-manager-operator_csr-signer-signer@1780711736 => oc get secret csr-signer-signer -n openshift-kube-controller-manager-operator
=>  签名 Subject: CN = kube-csr-signer_@1780711737 => oc get secret csr-signer -n openshift-kube-controller-manager-operator

过滤看看是哪个secret
```
oc get secret -A | grep csr
openshift-kube-controller-manager-operator         csr-signer                                                 kubernetes.io/tls                     2      372d
openshift-kube-controller-manager-operator         csr-signer-signer                                          kubernetes.io/tls                     2      371d
openshift-kube-controller-manager                  csr-signer                                                 kubernetes.io/tls                     2      372d
```

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
