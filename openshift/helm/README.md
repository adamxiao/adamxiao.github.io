# helm入门

关键字《编写helm charts》

[helm chart编写入门](https://developer.aliyun.com/article/831879)


## helm相关概念介绍

#### 什么是helm

Helm 是 Kubernetes 的包管理器。包管理器类似于我们在 Ubuntu 中使用的apt、Centos中使用的yum 或者Python中的 pip 一样，能快速查找、下载和安装软件包。使用helm能够将一组k8s资源打包统一管理, 是查找、共享和使用为Kubernetes构建的软件的最佳方式。

#### helm 相关组件及概念

• helm  一个命令行下客户端工具，主要用于k8s应用chart的创建/打包/发布已经创建和管理和远程Chart仓库。
• Tiller  helm的服务端，部署于k8s内，Tiller接受helm的请求，并根据chart生成k8s部署文件（helm称为release），然后提交给 k8s创建应用。Tiller 还提供了 Release 的升级、删除、回滚等一系列功能。
• chart  helm的软件包，其包含运行一个应用所需的所有镜像/依赖/资源定义等,以及k8s中服务定义
• release 使用 helm install 命令在 k8s集群中部署的 Chart 称为 Release
• Repoistory Helm chart 的仓库，Helm 客户端通过 HTTP 协议来访问存储库中 chart 的索引文件和压缩包

#### Chart 文件结构

```
wordpress/
  Chart.yaml          # 包含了chart信息的YAML文件
  LICENSE             # 可选: 包含chart许可证的纯文本文件
  README.md           # 可选: 可读的README文件
  values.yaml         # chart 默认的配置值
  values.schema.json  # 可选: 一个使用JSON结构的values.yaml文件
  charts/             # 包含chart依赖的其他chart
  crds/               # 自定义资源的定义
  templates/          # 模板目录， 当和values 结合时，可生成有效的Kubernetes manifest文件
  templates/NOTES.txt # 可选: 包含简要使用说明的纯文本文件
```

```
# parentchart/values.yaml

subchart1:
  enabled: true
tags:
  front-end: false
  back-end: true
``1

使用带有标签和条件的CLI
--set 参数一如既往可以用来设置标签和条件值。
```
helm install --set tags.front-end=true --set subchart2.enabled=false
```

[一条命令安装或升级版本](https://helm.sh/zh/docs/howto/charts_tips_and_tricks/)
```
helm upgrade --install <release name> --values <values file> <chart directory>
```

[从入门到实践：创作一个自己的 Helm Chart](https://juejin.cn/post/6844903928404918286)

开始创作
运行 helm create my-hello-world，会得到一个 helm 自动生成的空 chart。这个 chart 里的名称是 my-hello-world。 需要注意的是，Chart 里面的 my-hello-world 名称需要和生成的 Chart 文件夹名称一致。如果修改 my-hello-world，则需要做一致的修改。 现在，我们看到 Chart 的文件夹目录如下：


## 旧的资料

(前提: 安装[helm](https://mirror.openshift.com/pub/openshift-v4/x86_64/clients/helm/3.7.1/helm-linux-arm64.tar.gz))

## 参考资料

* [helm官方文档](https://helm.sh/zh/docs/topics/charts/)

