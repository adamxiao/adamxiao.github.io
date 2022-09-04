# configmap使用

问题：
* 1. 子目录文件怎么映射 => 不行
* 2. 非utf8文件内容configmap怎么导入的？ => base64
* 3. configmap大小限制1M，超过怎么整？ => 挂载存储卷 或者使用独立的数据库或者文件服务

TODO：
* 1. 使用 ConfigMap 来配置 Redis => 已验证，生成了一个只读的config文件
* 2. 导入非utf8文件尝试 => 优先级低一点？
* 3. mount到同一个目录下多个文件 => 可以！
* 4. xxx


只读问题解决？
https://zhuanlan.zhihu.com/p/88700221
下面这种方式最合理吧！



可以控制路径
https://docs.openshift.com/container-platform/4.4/builds/builds-configmaps.html




configmap可以配置为不可变的。





指定多个configmap，后面就直接会覆盖前面的配置。


不指定configmap里面的文件内容，就是映射全部文件。



基于目录创建configmap, 子目录会被忽略
可以手动把一个子目录加进来，如果重名的配置文件，怎么处理？
oc create configmap dir-test --from-file=./ --from-file=./redis-configmap-test


尝试将不同configmap的文件mount到容器中的同一个目录中，结果有问题。



默认是只读的。


configmap的用途


k8s官方ConfigMap使用教程文档
https://kubernetes.io/zh/docs/tasks/configure-pod-container/configure-pod-configmap/
另外一个教程，跟上面也很类似
https://www.bmc.com/blogs/kubernetes-configmap/


k8s官方ConfigMap概念介绍文档
https://kubernetes.io/zh/docs/concepts/configuration/configmap/
动机 
使用 ConfigMap 来将你的配置数据和应用程序代码分开。
ConfigMap 在设计上不是用来保存大量数据的。在 ConfigMap 中保存的数据不可超过 1 MiB。如果你需要保存超出此尺寸限制的数据，你可能希望考虑挂载存储卷 或者使用独立的数据库或者文件服务。


## 其他

#### 创建configmap

```bash
oc create configmap nginx-conf --from-file=conf.d/
oc -n nginx create secret tls hub-iefcu-tls --cert=./hub.iefcu.cn_bundle.crt --key=./hub.iefcu.cn.key
oc -n nginx create secret tls iefcu-tls --cert=./fullchain.cer --key=./iefcu.cn.key
```

#### 更新configmap

使用oc replace
```
oc -n nginx create configmap nginx-conf --from-file=conf.d/ -o yaml --dry-run=client | oc replace -f -
```

#### 热更新configmap

关键字《openshift configmap-reloader》

https://github.com/openshift/configmap-reload  => fork from jimmidyson/configmap-reload

[Configmap Reload with Spring Boot in Kubernetes](https://gungor.github.io/article/2020/12/27/springboot-k8s-configmap-reload.html)
=> 这个是springboot的监控机制, 连接apiserver，获取configmap的热更新通知。。。

```
kubectl create deployment liveconfig-demo --image=springboot-configmap-livereload-example:0.0.1-SNAPSHOT
kubectl create service clusterip liveconfig-demo --tcp=8080:8080
```

关键字《openshift configmap reload》

[Kubernetes ConfigMap Configuration and Reload Strategy](https://medium.com/swlh/kubernetes-configmap-confuguration-and-reload-strategy-9f8a286f3a44)
=> 也是springboot的机制? the whole Spring ApplicationContext is gracefully restarted

[(好)configmap-reload另外一种实现](https://github.com/jimmidyson/configmap-reload)
configmap-reload is a simple binary to trigger a reload when Kubernetes ConfigMaps are updated. 
It watches mounted volume dirs and notifies the target process that the config map has been changed.
It currently only supports sending an HTTP request, but in future it is expected to support sending OS (e.g. SIGHUP) once Kubernetes supports pod PID namespaces.
https://zhuanlan.zhihu.com/p/136229909
configmap-reload 采用rust语言实现，作为主业务容器的sidercar，主要用于k8s当中监听configmap的变化，待变化后通过http接口的方式通知主业务。在资源消耗上，更小。具体如下：


=> 估计openshift的configmap-reloader也是这种原理。。。
=> 但是会不会是在gitops中使用的。。。
GitOps Kubernetes Rolling Update when ConfigMaps and Secrets Change
https://boxboat.com/2018/07/05/gitops-kubernetes-rolling-update-configmap-secret-change/

[Restart pods when configmap updates in Kubernetes?](https://stackoverflow.com/questions/37317003/restart-pods-when-configmap-updates-in-kubernetes)
https://github.com/kubernetes/kubernetes/issues/22368
=> 官方这个configmap reloader的讨论问题, 目前为解决

https://william-yeh.net/post/2019/06/autoreload-from-configmap/
To clarify this I’ve conducted a series of experiments for 3 possible configmap-reloading strategies:
* Built-in auto-reloading apps
* Pod rollout
  https://github.com/stakater/Reloader
* External signals
  subpath的configmap不行

以annotations备注这个nginx-config配置更新重新推出pod部署
=> 估计openshift也是这种方式处理
```
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx
  annotations:
    configmap.reloader.stakater.com/reload: "nginx-config"
  ...
```

参考资料
K8s基于Reloader的ConfigMap/Secret热更新
https://www.jianshu.com/p/6838be064c8b

#### 基本使用configmap

```
xxx
```

#### 只读问题解决

https://zhuanlan.zhihu.com/p/88700221

lk

## 参考资料

* [openshift 3.11 ConfigMaps Developer Guide](https://docs.openshift.com/container-platform/3.11/dev_guide/configmaps.html)
