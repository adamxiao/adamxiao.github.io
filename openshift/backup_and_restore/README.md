# 备份与恢复

例如etcd的备份和恢复

修改时间导致证书过期的恢复等

#### 恢复kubelet证书

首先恢复journal日志输出
由于时间前后乱调，导致journal日志时间错乱，使用`journalctl -f -u kubelet`无法查看日志, 需要恢复一下

手工删除日志文件，则在删除前需要先轮转一次journal日志
```
systemctl kill --kill-who=main --signal=SIGUSR2 systemd-journald.service
```
然后删除/var/log/journal目录下的旧的错误日志

然后参考openshift的恢复控制平面的证书, 来恢复kubelet的证书
```
# 在 master 主机上停止 kubelet。
systemctl stop kubelet

# 删除旧的 kubelet 数据。
rm -rf /var/lib/kubelet/pki /var/lib/kubelet/kubeconfig

# 重新启动 kubelet。
systemctl start kubelet

# 最后通过kubelet申请的csr证书
oc adm certificate approve <csr_name>

# 这个csr通过之后, 生成了kubelet-client-current.pem证书
csr-6zgx6   10m   kubernetes.io/kube-apiserver-client-kubelet   system:serviceaccount:openshift-machine-config-operator:node-bootstrapper   <none>              Pending
# 这个证书通过之后，生成了kubelet-server-current.pem证书
csr-cjvlw   45s   kubernetes.io/kubelet-serving                 system:node:worker1.kcp1-arm.iefcu.cn                                       <none>              Pending
```

当然遇到过通过kubelet申请csr证书，没有生成pem证书, 以后再看看

## 参考资料

* [journalctl 清理journal日志](https://www.cnblogs.com/jiuchongxiao/p/9222953.html)
* [3.4. 从 control plane 证书已过期的情况下恢复](https://access.redhat.com/documentation/zh-cn/openshift_container_platform/4.3/html/backup_and_restore/dr-recovering-expired-certs#dr-scenario-3-recovering-expired-certs_dr-recovering-expired-certs)
