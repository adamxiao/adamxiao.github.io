# 时区配置

思路:
* 修改容器TZ时区配置 => 没用
* 查看修改alertmanager源码?
* 修改/etc/localtime?
  新做一个镜像, 或hostpath卷映射
* alert template配置 => 没找到合适方法

https://access.redhat.com/solutions/4682791
应该是alertmanager的时区问题，关键字《openshift promethues timezone setting》

key `openshift修改prometheus容器时区`
https://blog.csdn.net/weixin_43902588/article/details/108298517

https://zhangguanzhang.github.io/2019/09/05/prometheus-change-timezone/
修改源码更改prometheus的时区问题


设置容器时区
在Container运行的时候缺省使用的也是以UTC为基准的时间+时区的体系。如果我们希望用本地时间+时区的体系，可用以下不同的方式告诉运行容器。

在Dockerfile中设置时区环境。
FROM postgres:10
ENV TZ="Asia/Shanghai"
RUN date
1
2
3
运行容器的时候，通过环境变量指定容器使用的时区
docker run <IMAGE:TAG> -e TZ=Asia/Shanghai 
1
运行容器的时候将系统时区目录映射到容器的时区目录上。
$ docker run -v /etc/localtime:/etc/localtime <IMAGE:TAG>
1
在OpenShift的DeploymentConfig中设置时区
$ oc set env dc/<DC_NAME> Asia/Shanghai
原文链接：https://blog.csdn.net/weixin_43902588/article/details/108298517


去openshift-doc上去搜索timezone关键字, alertmanager?
https://github.com/openshift/openshift-docs


https://prometheus.io/docs/alerting/latest/configuration/
alertmanager配置?


Can I set the time zone to CST or other time zones, because utc is too unfriendly to us. I've tried changing the container's time zone. it's no good.
https://github.com/prometheus-operator/kube-prometheus/issues/1185
prometheus-operator/kube-prometheus 提的问题!


第一步, 执行命令 oc scale --replicas=0 deployments/cluster-version-operator -n openshift-cluster-version
第二步，修改StatefulSets alertmanager-main，添加一个TZ环境变量，值为shanghai
```
oc -n openshift-monitoring get StatefulSets alertmanager-main -o yaml | grep shanghai -i -B 1
        - name: TZ
          value: Asia/Shanghai
```


OpenShift AlertManager UTC Timezone
https://access.redhat.com/solutions/4682791
只有ｒｅｄｈａｔ的问题，没权限看答案

Edit the Prometheus Alertmanager configuration
https://access.redhat.com/solutions/3804781


How to set timezone for pods in OpenShift Container Platform?
https://access.redhat.com/solutions/2567961


`配置alertmanager webhook告警接收`
配置默认Default告警接收者为webhook http://x.x.x.x:8080/default, 抓包发现接收到告警信息了
"startsAt":"2022-08-26T03:28:22.563Z"

也可以通过命令行修改这个配置
https://access.redhat.com/documentation/zh-cn/openshift_container_platform/4.6/html/monitoring/applying-custom-alertmanager-configuration_managing-alerts
```
oc -n openshift-monitoring get secret alertmanager-main --template='{{ index .data "alertmanager.yaml" }}' | base64 --decode > alertmanager.yaml
oc -n openshift-monitoring create secret generic alertmanager-main --from-file=alertmanager.yaml --dry-run=client -o=yaml |  oc -n openshift-monitoring replace secret --filename=-
```

```
POST /default HTTP/1.1
Host: x.x.x.x:8080
User-Agent: Alertmanager/0.22.2
Content-Length: 4114
Content-Type: application/json

{"receiver":"Default","status":"firing","alerts":[{"status":"firing","labels":{"alertname":"KubeDeploymentReplicasMismatch","container":"kube-rbac-proxy-main","deployment":"elasticsearch-operator","endpoint":"https-main","job":"kube-state-metrics","namespace":"openshift-operators","prometheus":"openshift-monitoring/k8s","service":"kube-state-metrics","severity":"warning"},"annotations":{"description":"Deployment openshift-operators/elasticsearch-operator has not matched the expected number of replicas for longer than 15 minutes. This indicates that cluster infrastructure is unable to start or restart the necessary components. This most often occurs when one or more nodes are down or partioned from the cluster, or a fault occurs on the node that prevents the workload from starting. In rare cases this may indicate a new version of a cluster component cannot start due to a bug or configuration error. Assess the pods for this deployment to verify they are running on healthy nodes and then contact support.","runbook_url":"https://github.com/openshift/runbooks/blob/master/alerts/cluster-monitoring-operator/KubeDeploymentReplicasMismatch.md","summary":"Deployment has not matched the expected number of replicas"},"startsAt":"2022-08-26T03:28:22.563Z","endsAt":"0001-01-01T00:00:00Z","generatorURL":"https://prometheus-k8s-openshift-monitoring.apps.kcp1-arm.iefcu.cn/graph?g0.expr=%28%28%28kube_deployment_spec_replicas%7Bjob%3D%22kube-state-metrics%22%2Cnamespace%3D~%22%28openshift-.%2A%7Ckube-.%2A%7Cdefault%29%22%7D+%3E+kube_deployment_status_replicas_available%7Bjob%3D%22kube-state-metrics%22%2Cnamespace%3D~%22%28openshift-.%2A%7Ckube-.%2A%7Cdefault%29%22%7D%29+and+%28changes%28kube_deployment_status_replicas_updated%7Bjob%3D%22kube-state-metrics%22%2Cnamespace%3D~%22%28openshift-.%2A%7Ckube-.%2A%7Cdefault%29%22%7D%5B5m%5D%29+%3D%3D+0%29%29+%2A+on%28%29+group_left%28%29+cluster%3Acontrol_plane%3Aall_nodes_ready%29+%3E+0\u0026g0.tab=1","fingerprint":"b91b5556cafe531e"},{"status":"firing","labels":{"alertname":"KubeContainerWaiting","container":"elasticsearch-operator","namespace":"openshift-operators","pod":"elasticsearch-operator-74d7966448-wnxgx","prometheus":"openshift-monitoring/k8s","severity":"warning"},"annotations":{"description":"Pod openshift-operators/elasticsearch-operator-74d7966448-wnxgx container elasticsearch-operator has been in waiting state for longer than 1 hour.","summary":"Pod container waiting longer than 1 hour"},"startsAt":"2022-08-26T04:13:46.474Z","endsAt":"0001-01-01T00:00:00Z","generatorURL":"https://prometheus-k8s-openshift-monitoring.apps.kcp1-arm.iefcu.cn/graph?g0.expr=sum+by%28namespace%2C+pod%2C+container%29+%28kube_pod_container_status_waiting_reason%7Bjob%3D%22kube-state-metrics%22%2Cnamespace%3D~%22%28openshift-.%2A%7Ckube-.%2A%7Cdefault%29%22%7D%29+%3E+0\u0026g0.tab=1","fingerprint":"29b51ad9481c9e46"},{"status":"firing","labels":{"alertname":"KubeContainerWaiting","container":"kube-rbac-proxy","namespace":"openshift-operators","pod":"elasticsearch-operator-74d7966448-wnxgx","prometheus":"openshift-monitoring/k8s","severity":"warning"},"annotations":{"description":"Pod openshift-operators/elasticsearch-operator-74d7966448-wnxgx container kube-rbac-proxy has been in waiting state for longer than 1 hour.","summary":"Pod container waiting longer than 1 hour"},"startsAt":"2022-08-26T04:13:46.474Z","endsAt":"0001-01-01T00:00:00Z","generatorURL":"https://prometheus-k8s-openshift-monitoring.apps.kcp1-arm.iefcu.cn/graph?g0.expr=sum+by%28namespace%2C+pod%2C+container%29+%28kube_pod_container_status_waiting_reason%7Bjob%3D%22kube-state-metrics%22%2Cnamespace%3D~%22%28openshift-.%2A%7Ckube-.%2A%7Cdefault%29%22%7D%29+%3E+0\u0026g0.tab=1","fingerprint":"8aa93457ca529f1b"}],"groupLabels":{"namespace":"openshift-operators"},"commonLabels":{"namespace":"openshift-operators","prometheus":"openshift-monitoring/k8s","severity":"warning"},"commonAnnotations":{},"externalURL":"http...
```

由于是rfc3339格式时间, 看能不能改为utc+8:00时间
```
2019-10-12T14:20:50.52+08:00
2017-12-08T08:00:00.00+08:00
```

[Prometheus Alertmanager告警模板](https://blog.csdn.net/u010039418/article/details/111369486)
cat /usr/local/prometheus/alertmanager/wechat.tmpl
```
告警时间: {{ ($alert.StartsAt.Add 28800e9).Format "2006-01-02 15:04:05" }}
```
其中Add 28800e9表示在基准时间上添加8小时，28800e9是8小时的纳秒数。这就是从UTC时间转换到北京东八区时间。


https://github.com/prometheus/alertmanager/issues/2275 ` {{ .StartsAt.Format "2006-01-02T15:04:05Z07:00" }} `

[NOTIFICATION TEMPLATE REFERENCE](https://prometheus.io/docs/alerting/latest/notifications/)
可能能够配置告警通知模板，把这个时间改掉

Defining reusable templates
可以定制alertmanager模板。。。但看openshift好像没有提供接口? 还是可以配置的吧

[How to use a custom template when sending Prometheus alerts](https://access.redhat.com/solutions/4142511)
redhat确实有问题答案，可惜没有权限查看



修改所有容器的时区!

```
docker run -it -p 8080:80 -v $PWD/node_fakecgi.js:/node_fakecgi.js hub.iefcu.cn/public/node:16 /node_fakecgi.js
```

关键字《配置告警规则》
计划监控某个namespace某个部署的pod数量，少于2个正常就告警

```
sum(kube_running_pod_ready{namespace='nginx'})
```

配置一个PrometheusRule告警规则(就是operator管理的crd)
```
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: nginx-pod-num
  namespace: nginx
spec:
  groups:
  - name: nginx-pod-num
    rules:
    - alert: NginxPodNumAlert
      expr: sum(kube_running_pod_ready{namespace='nginx'}) < 2
```
