# k8s安装使用

## 准备软件

- docker-ce-18.09.6-3.el7.x86_64.rpm
- docker-ce-cli-18.09.6-3.el7.x86_64.rpm
- containerd.io-1.2.5-3.1.el7.x86_64.rpm

- cri-tools-1.13.0-0.x86_64.rpm
- kubernetes-cni-0.8.7-0.x86_64.rpm
- kubelet-1.22.0-0.x86_64.rpm
- kubeadm-1.22.0-0.x86_64.rpm
- kubectl-1.22.0-0.x86_64.rpm

## 参考资料

- [简单了解一下K8S，并搭建自己的集群](https://zhuanlan.zhihu.com/p/97605697)

- [k8s高可用集群搭建-kubeadm方式](https://www.jianshu.com/p/3de558d8b57a)

- [离线安装k8s方法](https://docs.genesys.com/Documentation/GCXI/latest/Dep/DockerOffline)

- [kubernetes集群离线安装包. 一条命令高可用 支持国产化](https://www.sealyun.com/instructions)

#### 离线安装k8s

Execute the following commands to install the Kubernetes repository:
```
cat <<EOF > /etc/yum.repos.d/kubernetes.repo
[kubernetes]
name=Kubernetes
baseurl=https://packages.cloud.google.com/yum/repos/kubernetes-el7-x86_64
enabled=1
gpgcheck=1
repo_gpgcheck=1
gpgkey=https://packages.cloud.google.com/yum/doc/yum-key.gpg https://packages.cloud.google.com/yum/doc/rpm-package-key.gpg
EOF
```

Execute the following command to download the Kubernetes utilities:
```
yumdownloader --assumeyes --destdir=<your_rpm_dir> --resolve yum-utils kubeadm-1.21.* kubelet-1.21.* kubectl-1.21.* ebtables
```

Execute the following command to run kubeadm, which returns a list of required images:
```
kubeadm config images list
```

A list of the required images appears, similar to the following:

```
k8s.gcr.io/kube-apiserver:v1.21.2 
k8s.gcr.io/kube-controller-manager:v1.21.2 
k8s.gcr.io/kube-scheduler:v1.21.2
k8s.gcr.io/kube-proxy:v1.21.2
k8s.gcr.io/pause:3.4.1
k8s.gcr.io/etcd:3.4.13-0
k8s.gcr.io/coredns/coredns:v1.8.0
```
