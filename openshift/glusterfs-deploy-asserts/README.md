# 部署配置glusterfs存储卷

1. 在gluster节点上操作

```
modprobe dm_thin_pool
```

2. 部署GlusterFS DaemonSet

```
oc create -f glusterfs-daemonset.json
oc get pods
# oc label node <...node...> storagenode=glusterfs 
```

3. 部署配置heketi bootstrap容器

```
# 权限配置等准备
oc create -f heketi-service-account.json
oc create clusterrolebinding heketi-gluster-admin --clusterrole=edit --serviceaccount=default:heketi-service-account
oc create secret generic heketi-config-secret --from-file=./heketi.json

oc create -f heketi-bootstrap.json
```

4. 配置heketi管理glusterfs集群

```
# 找到heketi容器名称
oc cp topology-sample.json deploy-heketi-5fc68f6bc-tjspw:/topology-sample.json

oc rsh deploy-heketi-5fc68f6bc-tjspw
heketi-cli topology load --json=topology-sample.json

heketi-cli setup-openshift-heketi-storage
# 单机需要加参数--durability=none
# heketi-cli setup-openshift-heketi-storage --durability=none

oc cp deploy-heketi-5fc68f6bc-tjspw:/heketi-storage.json ./heketi-storage.json
```

5. 复制heketi配置到新存储中去，然后删除临时bootstrap heketi，启动正式heketi 

```
kubectl create -f heketi-storage.json

# 检查jobs是否完成, 然后就可以删除临时heketi了
kubectl delete all,service,jobs,deployment,secret --selector="deploy-heketi"

# 部署正式heketi
oc create -f heketi-deployment.json
```

6. 创建存储类

```
oc create -f slow-sc.yaml
kubectl patch storageclass slow -p '{"metadata": {"annotations":{"storageclass.kubernetes.io/is-default-class":"true"}}}'
```


# 参考资料

参考: https://github.com/heketi/heketi
参考: ./docs/design/kubernetes-integration.md
中文参考: https://jimmysong.io/kubernetes-handbook/practice/using-heketi-gluster-for-persistent-storage.html

