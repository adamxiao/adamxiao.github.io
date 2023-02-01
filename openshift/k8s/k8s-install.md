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

## 安装k8s

install.sh
```
# 需要自己先配置软件源;
# eg. baseurl=http://192.168.120.89/repos/KY3.3-6/aarch64/base/latest/
# 以及静态ip;
# 主机名;
# eg. sudo hostnamectl set-hostname master-node
# 控制节点和计算节点分别要做的事


# 1. 安装docker
# 2. 安装kubelet等
sudo yum install -y *.rpm || true

# 默认启动docker
sudo systemctl enable --now docker
# docker cgroup配置
cat << EOF | sudo tee /etc/docker/daemon.json
{"exec-opts": ["native.cgroupdriver=systemd"]}
EOF
sudo systemctl restart docker

# 3. 导入docker镜像
ls *.image | sed 's/^/sudo docker image load -i /' | bash

# 4. 其他准备 =======================================================
# 4.1 防火墙
sudo systemctl disable --now firewalld
# 4.2 selinux
sudo setenforce 0
sudo sed -i 's/^SELINUX=enforcing$/SELINUX=permissive/' /etc/selinux/config
# 4.3 swap
sudo swapoff -a
sudo sed -i 's/^[^#].* swap /#&/' /etc/fstab

# 5. 初始化集群(master节点处理)
# sudo kubeadm init --v=5 --pod-network-cidr=10.244.0.0/16 --kubernetes-version=v1.22.0
# 5.1 安装flannel组件 FIXME: 注意kubectl配置
# kubectl apply -f kube-flannel.yml
# 5.2 修正kubelet port配置
# sudo sed -i 's/^[^#].*--port=0/#&/' /etc/kubernetes/manifests/kube-scheduler.yaml
# sudo sed -i 's/^[^#].*--port=0/#&/' /etc/kubernetes/manifests/kube-controller-manager.yaml
# sudo systemctl restart kubelet.service
# 5.3 (可选)让master节点也可以运行pod
# kubectl taint nodes --all node-role.kubernetes.io/master-

echo "install finished, please continue!"
```

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
