# local storage安装使用

## 安装使用

```
oc new-project local-storage
```

## 构建arm64版本operator镜像

通过解析redhat-operator-index得到bundle镜像地址

registry.redhat.io/openshift4/ose-local-storage-operator-bundle@sha256:e55c436ab8dffaf7f1ae090ad909328b7e858a8784b6230e96b7205aa29bb537
|local-storage-operator.4.9.0-202201270226

同步下来, 解压查看

mkdir local-storage-bundle-rootfs
oc image extract --confirm \
  --path /:$PWD/local-storage-bundle-rootfs \
  hub.iefcu.cn/kcp/ose-local-storage-operator-bundle@sha256:e55c436ab8dffaf7f1ae090ad909328b7e858a8784b6230e96b7205aa29bb537

修改support arm64
manifests/local-storage-operator.v4.9.0.clusterserviceversion.yaml
"operatorframework.io/arch.arm64": supported

同步镜像, 最后同步下来, 发现都支持arm64了
```
registry.redhat.io/openshift4/ose-kube-rbac-proxy@sha256:904cfd885748b23643555412deed553c3d7cda4c17e8469cfdde94dd02987550
registry.redhat.io/openshift4/ose-local-storage-diskmaker@sha256:a5457be43741a22fd62cecd2bd7e67ab9dc31122cc6e9364c272dd4260600e02
registry.redhat.io/openshift4/ose-local-storage-operator@sha256:fade523358d1700d836a38579fc294cb2471f8f37d16e7bfaeb960bd9d0d4623
```

制作编译新的bundle镜像
```
docker build -t hub.iefcu.cn/kcp/ose-local-storage-operator-bundle:v4.9 .
```

制作新的operator index镜像
```
opm index add \
    --bundles hub.iefcu.cn/kcp/metallb-operator-bundle:v4.9@sha256:74da72dd402e5a85b2ece72695c6772dd56d771fc4e482719a9ffefe9fed89bc \
    --bundles hub.iefcu.cn/kcp/ose-local-storage-operator-bundle:v4.9@sha256:d6016b87ee1c9fed274782b1c2391f478b855682cfc6a7aca748e8fb5efbec09 \
    --tag hub.iefcu.cn/kcp/kylin-operator-index:v4.9 \
    --binary-image hub.iefcu.cn/public/redhat-operator-index:v4.9@sha256:fd45ebb5619656628b84266793ddf24ef6a393cd3a85bc1b5315d5500c0bf067

    --bundles hub.iefcu.cn/kcp/metallb-operator-bundle:v4.9
    --bundles hub.iefcu.cn/kcp/ose-local-storage-operator-bundle:v4.9
```

使用镜像构建
```
docker run -it --privileged --rm hub.iefcu.cn/xiaoyun/podman-opm:amd64
```


## 参考文档

[存储 - 3.11. 使用本地卷的持久性存储](https://access.redhat.com/documentation/zh-cn/openshift_container_platform/4.5/html/storage/persistent-storage-using-local-volume)
