# openshift pipeline安装使用

## 首先裁剪镜像，同步镜像

```bash
opm index prune -f hub.iefcu.cn/public/redhat-operator-index:v4.9 \
    --binary-image hub.iefcu.cn/public/redhat-operator-index:v4.9 \
    -p openshift-pipelines-operator-rh,openshift-gitops-operator \
    -t hub.iefcu.cn/kcp/pipeline-operator-index:v4.9

podman push hub.iefcu.cn/kcp/pipeline-operator-index:v4.9
```

## 同步镜像到私有registry

```bash
# 同步grafana相关镜像到本地文件
mkdir mirror-pipeline && cd mirror-pipeline
oc adm catalog mirror \
    hub.iefcu.cn/kcp/pipeline-operator-index:v4.9 \
    -a /tmp/pull-secret.json \
    file:///local/index \

--index-filter-by-os="linux/amd64'" \

info: Mirroring completed in 1m45.84s (4.408MB/s)
wrote mirroring manifests to manifests-grafana-operator-index-1647941600

To upload local images to a registry, run:

        oc adm catalog mirror file://local/index/kcp/redhat-operator-index:v4.9 REGISTRY/REPOSITORY

# 同步镜像到私有镜像仓库
oc adm catalog mirror \
  file://local/index/kcp/pipeline-operator-index:v4.9 \
  192.168.120.44/kcp/pipeline-operator-index:v4.9 \
  -a /tmp/pull-secret.json \
  --insecure
```


## 创建自定义catalogSource

```bash
cat << EOF | oc apply -f -
apiVersion: operators.coreos.com/v1alpha1
kind: CatalogSource
metadata:
  name: pipeline
  namespace: openshift-marketplace
spec:
  displayName: pipeline
  image: 'hub.iefcu.cn/kcp/pipeline-operator-index:v4.9'
  #image: 'hub.iefcu.cn/kcp/pipeline-operator-index-local-index-kcp-pipeline-operator-index:v4.9'
  publisher: adam
  sourceType: grpc
EOF
```

临时测试一个catalogSource
```bash
cat << EOF | oc apply -f -
apiVersion: operators.coreos.com/v1alpha1
kind: CatalogSource
metadata:
  name: tmp
  namespace: openshift-marketplace
spec:
  displayName: tmp
  image: 'hub.iefcu.cn/xiaoyun/tmp-operator-index:v4.9'
  publisher: adam
  sourceType: grpc
EOF
```

## 安装pipeline operator

### CLI安装pipeline operator

#### 订阅 Operator

```
cat << EOF| oc apply -f -
apiVersion: operators.coreos.com/v1alpha1
kind: Subscription
metadata:
  name: pipelines-operator-sub
  namespace: openshift-operators
spec:
  channel: stable
  name: openshift-pipelines-operator-rh
  source: pipeline
  sourceNamespace: openshift-marketplace
EOF
```

得到bundle镜像并同步下来计划修改: registry.redhat.io/openshift-pipelines/pipelines-operator-bundle@sha256:33579b992c33350232af2f2c4d370dda769a7f1e1a498ad1c697199f13f5e9a4

## 简单修改一下bundle镜像

同步为 hub.iefcu.cn/kcp/pipelines-operator-bundle

```bash
oc image extract \
  --path /:/root/workspaces/tmp/pipelines-operator-bundle-rootfs \
  hub.iefcu.cn/kcp/pipelines-operator-bundle@sha256:33579b992c33350232af2f2c4d370dda769a7f1e1a498ad1c697199f13f5e9a4

  #-a ~/tmp/pull-secret.json \
  # registry.redhat.io/openshift-pipelines/pipelines-operator-bundle@sha256:33579b992c33350232af2f2c4d370dda769a7f1e1a498ad1c697199f13f5e9a4
```

简单做了一个bundle镜像: hub.iefcu.cn/kcp/pipelines-operator-bundle:v4.9

## 根据bundle镜像制作catalogSource镜像

#### 获取bundle镜像

registry.redhat.io/openshift-pipelines/pipelines-operator-bundle@sha256:33579b992c33350232af2f2c4d370dda769a7f1e1a498ad1c697199f13f5e9a4

获取方法: 从官方redhat-operator-index中提取出bundle镜像
```bash
oc image extract --confirm \
  --path /database/index.db:/tmp \
  hub.iefcu.cn/public/redhat-operator-index:v4.9

sqlite3 ./index.db 'select * from main.related_image;' | grep pipelines | grep bundle

可以得到不同版本的pipelines的bundle镜像地址
registry.redhat.io/openshift-pipelines/pipelines-operator-bundle@sha256:4a8a4f4dc20909ad47a0e357f22a8d50763afd515c1c2c607a3df90f1dac0d34|redhat-openshift-pipelines.v1.4.0
registry.redhat.io/openshift-pipelines/pipelines-operator-bundle@sha256:3449a2d9c146801c9a3c1444e9764f74d4abcc5392d5c1e58d925a122a0e59e6|redhat-openshift-pipelines.v1.5.2
registry.redhat.io/openshift-pipelines/pipelines-operator-bundle@sha256:b5c6c1a3f937f507d832cde83c1581535f9fa3abbbaf833ffcc9aec0e061a9c2|openshift-pipelines-operator-rh.v1.6.1
=> registry.redhat.io/openshift-pipelines/pipelines-operator-bundle@sha256:33579b992c33350232af2f2c4d370dda769a7f1e1a498ad1c697199f13f5e9a4|openshift-pipelines-operator-rh.v1.6.2

> .tables
> select * from related_image;
> select * from operatorbundle;
```

#### 修改制作bundle镜像

主要是配置支持arm64架构

先同步bundle镜像到私有镜像仓库: hub.iefcu.cn/kcp/pipelines-operator-bundle

```bash
mkdir -p /tmp/pipelines-operator-bundle-rootfs
oc image extract \
  --path /:/tmp/pipelines-operator-bundle-rootfs \
  hub.iefcu.cn/kcp/pipelines-operator-bundle@sha256:33579b992c33350232af2f2c4d370dda769a7f1e1a498ad1c697199f13f5e9a4

# 可选, 加上拉取密钥: -a /tmp/pull-secret.json
```

简单做了一个bundle镜像(在x86下): hub.iefcu.cn/kcp/pipelines-operator-bundle:v4.9

#### 制作catalog镜像

在arm64下做出了一点问题, 计划在x86下面做?
```bash
opm index add \
    --bundles hub.iefcu.cn/kcp/pipelines-operator-bundle:v4.9 \
    --tag hub.iefcu.cn/kcp/pipeline-operator-index:v4.9 \
    --binary-image hub.iefcu.cn/public/redhat-operator-index:v4.9@sha256:fd45ebb5619656628b84266793ddf24ef6a393cd3a85bc1b5315d5500c0bf067
    #--binary-image hub.iefcu.cn/public/redhat-operator-index:v4.9

docker push hub.iefcu.cn/kcp/pipeline-operator-index:v4.9
```
=> 制作catalog镜像遇到错误!!!

```
INFO[0002] loading bundle file                           dir=bundle_tmp900815751/manifests file=tekton-operator_v1_service.yaml load=bundle
ERRO[0002] permissive mode disabled                      bundles="[hub.iefcu.cn/kcp/pipelines-operator-bundle:v4.9]" error="Invalid bundle openshift-pipelines-operator-rh.v1.6.2, replaces nonexistent bundle redhat-openshift-pipelines.v1.5.2"
Error: Invalid bundle openshift-pipelines-operator-rh.v1.6.2, replaces nonexistent bundle redhat-openshift-pipelines.v1.5.2
```

TODO: 分析一下错误的原因?
修改脚本, 使用其他elasticseach-operator-index基础镜像，也不行。。。
```
opm index add \
    --bundles hub.iefcu.cn/kcp/elasticsearch-operator-bundle:v4.9 \
    --bundles hub.iefcu.cn/kcp/logging-operator-bundle:20220406 \
    --bundles hub.iefcu.cn/kcp/pipelines-operator-bundle:v4.9 \
    --tag hub.iefcu.cn/xiaoyun/tmp-operator-index:v4.9 \
    --binary-image hub.iefcu.cn/kcp/elasticsearch-operator-index:v4.9
```

就算加上--permissive运行构建生成catalog镜像，里面也是没有operator镜像的!
```bash
opm index add \
    --bundles hub.iefcu.cn/kcp/pipelines-operator-bundle:v4.9 \
    --tag hub.iefcu.cn/xiaoyun/tmp-operator-index:v4.9 \
    --permissive \
    --binary-image hub.iefcu.cn/kcp/elasticsearch-operator-index:v4.9
```

其实就是更新index.db数据库文件，校验一下数据库文件

查看相关镜像，发现为空
```bash
sqlite3 ./index.db 'select * from related_image;'
```

将所有的pipelines的bundle镜像拿来，创建catalog镜像
```bash
opm index add \
    --bundles hub.iefcu.cn/kcp/pipelines-operator-bundle:v4.9 \
	--bundles hub.iefcu.cn/kcp/pipelines-operator-bundle@sha256:4a8a4f4dc20909ad47a0e357f22a8d50763afd515c1c2c607a3df90f1dac0d34 \
	--bundles hub.iefcu.cn/kcp/pipelines-operator-bundle@sha256:3449a2d9c146801c9a3c1444e9764f74d4abcc5392d5c1e58d925a122a0e59e6 \
	--bundles hub.iefcu.cn/kcp/pipelines-operator-bundle@sha256:b5c6c1a3f937f507d832cde83c1581535f9fa3abbbaf833ffcc9aec0e061a9c2 \
    --tag hub.iefcu.cn/xiaoyun/tmp-operator-index:v4.9 \
    --binary-image hub.iefcu.cn/kcp/elasticsearch-operator-index:v4.9

opm index add \
    --bundles hub.iefcu.cn/kcp/pipelines-operator-bundle:v4.9 \
	--generate
```

最后猜测是bundle镜像有依赖redhat-openshift-pipelines.v1.5.2的问题，grep了一下，发现是的
然后去除依赖，重新做了一个bundle镜像，可以了!

最后通过web界面可以安装pipeline operator，但是由于镜像不支持，需要编译镜像!

## 编译pipeline镜像

获取源码：
https://catalog.redhat.com/software/containers/openshift-pipelines/pipelines-operator-bundle/6051bcfb7d4bcfc15f1793bf?container-tabs=gti&gti-tabs=get-the-source

![](../../imgs/2022-04-27-15-12-33.png)

![](../../imgs/2022-04-27-15-13-03.png)

#### 1. pipelines-rhel8-operator

原始信息:
* registry.redhat.io/openshift-pipelines/pipelines-rhel8-operator@sha256:2119dc053cd36f28d654bad37db851d034c1848b3f4166577a713ec5a0b38731
  原始bundle镜像
* hub.iefcu.cn/kcp/pipeline-operator-index-openshift-pipelines-pipelines-rhel8-operator@sha256:2119dc053cd36f28d654bad37db851d034c1848b3f4166577a713ec5a0b38731
  mirror镜像
* xxx
  源码


#### 2. pipelines-operator-webhook-rhel8

registry.redhat.io/openshift-pipelines/pipelines-operator-webhook-rhel8@sha256:f026d4fc9e83519a335e00e563ab9610879b8244a3b3319b19efcb977e02d3d5

## 安装jenkins operator

#### 获取jenkins bundle镜像
```bash
sqlite3 ./index.db 'select * from main.related_image;' | grep jenkins | grep bundle

registry.redhat.io/ocp-tools-4-tech-preview/jenkins-operator-bundle@sha256:359b40e1b6f964d53f2a39181bdb3332537fbc44af7678ba8743376214dd9edc|jenkins-operator.v0.7.2
registry.redhat.io/ocp-tools-4-tech-preview/jenkins-operator-bundle@sha256:59c857c03f39d682c10fd5947cca1bf4229eec68bd42e6067593704614676857|jenkins-operator.v0.7.3
```

同步bundle镜像
* registry.redhat.io/ocp-tools-4-tech-preview/jenkins-operator-bundle@sha256:59c857c03f39d682c10fd5947cca1bf4229eec68bd42e6067593704614676857
  => hub.iefcu.cn/kcp/jenkins-operator-bundle@sha256:59c857c03f39d682c10fd5947cca1bf4229eec68bd42e6067593704614676857

#### 简单修改bundle镜像

```bash
mkdir -p /tmp/jenkins-operator-bundle-rootfs
oc image extract \
  --path /:/tmp/jenkins-operator-bundle-rootfs \
  hub.iefcu.cn/kcp/jenkins-operator-bundle@sha256:59c857c03f39d682c10fd5947cca1bf4229eec68bd42e6067593704614676857
```

删除replace低版本字段，这个bundle镜像就能独立使用
```diff
diff --git a/manifests/jenkins-operator.clusterserviceversion.yaml b/manifests/jenkins-operator.clusterserviceversion.yaml
index b958241..bf9071b 100644
--- a/manifests/jenkins-operator.clusterserviceversion.yaml
+++ b/manifests/jenkins-operator.clusterserviceversion.yaml
@@ -328,7 +328,6 @@ spec:
   provider:
     name: Red Hat
   version: 0.7.3
-  replaces: jenkins-operator.v0.7.2
   relatedImages:
```

做成镜像 hub.iefcu.cn/kcp/jenkins-operator-bundle:v4.9

#### 创建新的catalog镜像

(注意: 必须先加v0.7.2,然后再加v0.7.3版本)
```bash
#--bundles hub.iefcu.cn/kcp/jenkins-operator-bundle@sha256:359b40e1b6f964d53f2a39181bdb3332537fbc44af7678ba8743376214dd9edc \
#--bundles hub.iefcu.cn/kcp/jenkins-operator-bundle@sha256:59c857c03f39d682c10fd5947cca1bf4229eec68bd42e6067593704614676857 \

opm index add \
    --bundles hub.iefcu.cn/kcp/jenkins-operator-bundle:v4.9 \
    --tag hub.iefcu.cn/kcp/kylin-operator-index:v4.9 \
    --binary-image hub.iefcu.cn/public/redhat-operator-index:v4.9@sha256:fd45ebb5619656628b84266793ddf24ef6a393cd3a85bc1b5315d5500c0bf067
```

#### 同步catalog镜像的镜像资源

可以先获取需要同步的镜像列表
```
oc image extract --confirm   --path /database/index.db:/tmp   hub.iefcu.cn/kcp/kylin-operator-index:v4.9
sqlite3 /tmp/index.db 'select * from related_image;'

quay.io/redhat-developer/openshift-jenkins-image-builder@sha256:6f491f7ee7ad18b85589ea22820dbb337544903380e78615737639ab5c8e3f66|jenkins-operator.v0.7.3
quay.io/redhat-developer/jenkins-kubernetes-sidecar@sha256:c9a638a0b706c8461173114adb82da45c15029cdc8dd35891491df7e84cc0bb1|jenkins-operator.v0.7.3
registry.redhat.io/ubi8/ubi-minimal@sha256:fdfb0770bff33e0f97d78583efd68b546a19d0a4b0ac23eef25ef261bca3e975|jenkins-operator.v0.7.3
hub.iefcu.cn/kcp/jenkins-operator-bundle:v4.9|jenkins-operator.v0.7.3
registry.redhat.io/ocp-tools-4-tech-preview/jenkins-rhel8-operator@sha256:b67946775d489defdfc0fae7d5950ca2ea055ec13169337fef9d95dd1115be35|jenkins-operator.v0.7.3
registry.redhat.io/openshift4/ose-jenkins@sha256:2bb575a192329b356edf6f30932e2daee26b5a5ebaa228df9f66699d0e530158|jenkins-operator.v0.7.3
```

使用oc工具自动同步相关镜像(验证ok，不错)
```
# 验证ok
mkdir mirror-kylin && cd mirror-kylin
oc adm catalog mirror \
    hub.iefcu.cn/kcp/kylin-operator-index:v4.9 \
    -a /tmp/pull-secret.json \
    192.168.120.44/kcp/kylin \
    --insecure

# 通过这个参数就可以生成imageContentSourcePolicy !
# --dry-run
oc adm catalog mirror \
    hub.iefcu.cn/kcp/kylin-operator-index:v4.9 \
    -a /tmp/pull-secret.json \
    hub.iefcu.cn/kcp/kylin \
    --insecure --dry-run
```

## 最后就可以使用安装这个operator了

#### 创建自定义catalogSource

```bash
cat << EOF | oc apply -f -
apiVersion: operators.coreos.com/v1alpha1
kind: CatalogSource
metadata:
  name: kylin
  namespace: openshift-marketplace
spec:
  displayName: kylin
  image: 'hub.iefcu.cn/kcp/kylin-operator-index:v4.9'
  publisher: adam
  sourceType: grpc
EOF
```

关键字《openshift 4 jenkins operator》
从operatorhub中找到，发现jenkins operator只支持到k8s 1.21, 而openshift 4.9是1.22不支持了!

计划用这个啰!
operatorhub上的 Tektoncd Operator
Tekton Pipelines is a Kubernetes-Native CI/CD solution for building CI/CD pipelines.

argocd-operator

关键字《argocd vs Tektoncd》

[Tekton+Argocd实现自动化流水线](https://www.cnblogs.com/z-gh/p/15459260.html)

什么是tekton
Tekton 是一个功能强大且灵活的Kubernetes 原生开源框架，用于云上持续集成和交付（CI/CD）系统，通过Operator的方式集成到k8集群中，并以容器作为驱动，完成流水线模版定义的任务，社区也提供了很多任务模版来方便使用。


Tekton提供的CRD
Task： 任务模版，你可以在里面定义相应的steps来表示需要执行的步骤，每个step代表一个pod。
TaskRun：任务模版的执行实例，通过传入任务模版定义的参数来创建。
Pipeline：流水线模版，包含一系列任务并且定义各个任务之间的先后顺序。
PipelineRun：流水线模版实例，关联到流水线并传入所有的任务参数来执行

JenkinsFile干嘛用的？ => 之前构建镜像好像提到这个关键字

[Migrating from Jenkins to Tekton](https://docs.openshift.com/container-platform/4.8/cicd/jenkins-tekton/migrating-from-jenkins-to-tekton.html)


[OpenShift 4 Hands-on Lab (7) - 用Jenkins Pipeline实现在不同运行环境中升迁部署应用](https://blog.csdn.net/weixin_43902588/article/details/104285933)

通过模板部署jenkins，然后构建镜像？
