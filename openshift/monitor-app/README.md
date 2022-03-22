# 监控相关调研

主要是promethues的配置使用, openshift使用的promethues operator，配置方法跟普通的promethues有一点儿不一样。


关键字《traefik api 耗时监控》

[prometheus监控traefik](https://www.modb.pro/db/116312)

我们可以在grafana上通过图形展示这些metrics，这里推荐两个traefik 2.x的dashboard
（配置查询规则json配置文件即可。）
traefik-mesh安装文件中也有一个traefik的监控dashboard，也是一个json配置文件。

* https://grafana.com/grafana/dashboards/10906
* https://grafana.com/grafana/dashboards/11508

![](https://oss-emcsprod-public.modb.pro/wechatSpider/modb_20210927_a94f5b24-1f6b-11ec-b948-00163e068ecd.png)

![](https://oss-emcsprod-public.modb.pro/wechatSpider/modb_20210927_a9dd0f3c-1f6b-11ec-b948-00163e068ecd.png)


## 添加仪表盘

这篇文档不错。
[Traefik SRE 之使用 Prometheus 进行监控报警](https://www.cnblogs.com/sanduzxcvbnm/p/15749905.html)

Grafana 配置
前面使用 kube-prometheus-stack 这个 Helm Chart 部署的时候就已经部署上了 Grafana，接下来我们可以为 Traefik 的监控指标配置一个 Dashboard，同样首先我们使用端口转发的方式来访问 Grafana：

$ kubectl port-forward service/rometheus-stack-grafana 10080:80
然后访问 Grafana GUI（http://localhost:10080）时，它会要求输入登录名和密码，默认的登录用户名是 admin，密码是 prom-operator，密码可以从名为 prometheus-operator-grafana 的 Kubernetes Secret 对象中获取。

当然我们可以自己为 Traefik 自定义一个 Dashboard，也可以从 Grafana 的官方社区中导入一个合适的即可，点击左侧导航栏上的四方形图标，导航到 Dashboards > Manage，即可添加仪表盘。

=> openshift中的grafana没有添加的地方？

[使用 Prometheus Operator 监控 Traefik Ingress](https://blog.csdn.net/qq_32641153/article/details/93765581)

打开 Grafana，在其中引入编号“4475”的仪表盘
=> **意思就是grafana官网有4475号仪表盘可以导入!!**


prometheus监控traefik_v1_u010533742的博客-程序员ITS404_prometheus监控traefik
https://www.its404.com/article/u010533742/119916068



[(好)OpenShift 4 - 使用定制的Grafana和Dashboard](https://blog.csdn.net/weixin_43902588/article/details/108763230)

我们知道，在OpenShift 4 中已经内置了Prometheus和Grafana，可以在控制台的“仪表盘”中直接使用，它们的相关资源都运行在openshift-monitoring项目中。但是为了能保持监控环境始终可以正常运行，OpenShift只为内置的Grafana提供了只读（下图的Viewer）权限，**即便使用OpenShift集群管理员也不能修改集群内置的Grafana配置，例如导入定制的Dashboard。**