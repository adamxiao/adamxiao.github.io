# openshift 编译arm64 Elasticsearch operator 镜像

TODO: 
* openshift集群范围内代理
* https://access.redhat.com/documentation/zh-cn/openshift_container_platform/4.9/html/post-installation_configuration/nw-proxy-configure-object_post-install-network-configuration

[Creating Kubernetes Secrets Using TLS/SSL as an Example](https://shocksolution.com/2018/12/14/creating-kubernetes-secrets-using-tls-ssl-as-an-example/)
[secret官方文档](https://kubernetes.io/docs/concepts/configuration/secret/)
[OpenShift 4 Hands-on Lab (12) 使用配置参数和环境变量](https://blog.csdn.net/weixin_43902588/article/details/104436782)
[OpenShift 4 - 全图形化 Step-by-Step 部署容器应用](https://blog.csdn.net/weixin_43902588/article/details/115284085)


一种基于openshift的自动化监控微服务api耗时方法？
一种基于角色的集群节点管理配置文件方法
一种基于openshift的自动监控微服务API耗时方法

专利方面考虑
自动service mesh监控服务api耗时
machine-config配置(时间同步等配置) 还有优化的地方
堡垒机器安装做成一个安装程序, 快速安装kcp平台
应用程序部署，回放配置，多平台部署?
gitops相关, CI/CD, 自动识别编译构建镜像啥的
人脸认证登录kcp系统(手机识别登录)

TODO:
* 时间同步配置验证
* 时区配置验证, 以及容器时区
* arm64盒子安装podman, libc6-dev


https://www.one-tab.com/page/YfTvjlabR9OqHV1mRY4wqA?ext=de72ce03-98b7-4210-b30f-86afdf724045

https://devopstales.github.io/home/openshift4-auth/
[Part1b: Install Opeshift 4 with calico](https://devopstales.github.io/kubernetes/openshift4-calico/)

## 容器云后续可开展工作梳理

* 做一个operator hub, 整理好离线安装部署文档
  包含metallb, redis, es等内置提供的operator

* promethues数据存储到pv中

* 集群5节点高可用部署验证
  处理禁止crio清理镜像的问题
  处理时间同步问题

* jenkins自动构建部署xxx应用
  目前他们的应用上云还是比较复杂, 需要简化

* 更多
  日志，块存储, 用户认证租户权限...


## helm入门

关键字《helm原理》

#### 下图为Helm整体应用框架图：

　　helm是作为Helm Repository的客户端工具，helm默认工作时，会从本地家目录中去获取chart，只有本地没有chart时，它才会到远端的Helm Repository上去获取Chart，当然你也可以自己在本地做一个Chart，当需要应用chart到K8s上时，就需要helm去联系K8s Cluster上部署的Tiller Server，当helm将应用Chart的请求给Tiller Server时，Tiller Server接受完helm发来的charts(可以是多个chart) 和 chart对应的Config 后，它会自动联系API Server，去请求应用chart中的配置清单文件，最终这些清单文件会被实例化为Pod或其它定义的资源，而这些通过chart创建的资源，统称为release，一个chart可被实例化多次，其中的某些参数是会根据Config规则自动更改，例如Pod的名字等。

![](https://img2018.cnblogs.com/blog/922925/201908/922925-20190802211739347-306840075.png)

旁路由 单臂路由了解

![](../imgs/2022-03-17-11-59-33.png)

这个页面多几个数据暂时，有节点数，啥的等。
有几个宿主机，硬盘啥的。点进去能看到某一个宿主机的cpu，内存等使用率。
![](../imgs/2022-03-16-14-03-50.png)

备份和恢复
https://access.redhat.com/documentation/zh-cn/openshift_container_platform/4.9/html-single/backup_and_restore/index

etcd备份
![](../imgs/2022-03-14-21-27-51.png)

## 获取Elasticserach镜像以及源码


算法实验
https://algorithm.yuanbin.me/zh-hans/faq/guidelines_for_contributing.html#
https://github.com/billryan/algorithm-exercise
