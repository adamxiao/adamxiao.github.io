# 安装heketi+glusterfs存储类

首先要解压glusterfs.tgz压缩包，所有的yaml配置文件都在里面

注意事项，修改image，修改成可以拉到的镜像

#### 1. glusterfs宿主机开启内核模块

```bash
sudo modprobe dm_thin_pool
```

#### 2. 部署GlusterFS DaemonSet

注意配置文件里面的image, 确保能够拉到

registry.kcp.local:5000/kcp/gluster-containers:latest
(原来是 hub.iefcu.cn/xiaoyun/gluster-containers:latest)

```bash
oc create -f glusterfs-daemonset.json
oc get pods
# oc label node <...node...> storagenode=glusterfs 
```

#### 3. 部署配置heketi bootstrap容器

注意配置文件里面的image, 确保能够拉到

registry.kcp.local:5000/kcp/heketi:9
(原来是 hub.iefcu.cn/xiaoyun/heketi:9)

```
# 权限配置等准备
oc create -f heketi-service-account.json
oc create clusterrolebinding heketi-gluster-admin --clusterrole=edit --serviceaccount=default:heketi-service-account
oc create secret generic heketi-config-secret --from-file=./heketi.json

oc create -f heketi-bootstrap.json
```

#### 4. 配置heketi管理glusterfs集群

首先配置topology-sample.json配置文件, 配置管理的几个glusterfs实例，主机名, ip和磁盘存储

然后导入配置到heketi容器里面去运行
```
# 找到heketi容器名称
oc cp topology-sample.json deploy-heketi-5fc68f6bc-tjspw:/topology-sample.json

oc rsh deploy-heketi-5fc68f6bc-tjspw
heketi-cli topology load --json=topology-sample.json

heketi-cli setup-openshift-heketi-storage
# 单机(小于3个glusterfs主机)需要加参数--durability=none
# heketi-cli setup-openshift-heketi-storage --durability=none
# 集群就不需要加--durability=none
# heketi-cli setup-openshift-heketi-storage

# 然后将生成的heketi-storage.json拷贝出去
oc cp deploy-heketi-5fc68f6bc-tjspw:/heketi-storage.json ./heketi-storage.json
```

#### 5. 复制heketi配置到新存储中去，然后删除临时bootstrap heketi，启动正式heketi 

修改heketi-storage.json配置文件，修改image为:
registry.kcp.local:5000/kcp/heketi:9
(原来是 hub.iefcu.cn/xiaoyun/heketi:9)

注意这里使用的是kubectl命令
```
kubectl create -f heketi-storage.json

# 检查jobs是否完成, 然后就可以删除临时heketi了
kubectl get jobs
kubectl delete all,service,jobs,deployment,secret --selector="deploy-heketi"

# 部署正式heketi
oc create -f heketi-deployment.json
```

### 6. 创建存储类

修改slow-sc.yaml中的ip地址，使用heketi svc的ip地址
(TODO: 确认一下是否可以使用heketi svc的内部域名?)

```
oc create -f slow-sc.yaml
# 以及配置存储类为默认存储类
kubectl patch storageclass slow -p '{"metadata": {"annotations":{"storageclass.kubernetes.io/is-default-class":"true"}}}'
```

# 参考资料

参考: https://github.com/heketi/heketi
参考: ./docs/design/kubernetes-integration.md
中文参考: https://jimmysong.io/kubernetes-handbook/practice/using-heketi-gluster-for-persistent-storage.html
