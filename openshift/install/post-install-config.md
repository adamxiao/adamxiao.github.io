# 安装后配置文档

## 配置认证用户

参考![](./add-basic-user.md)

## registry auth配置

pullSecret修改
1.首先获取当前全局的pull-secret
```
oc get secret/pull-secret -n openshift-config --template='{{index .data ".dockerconfigjson" | base64decode}}' >pull-secret.json
```

2.然后添加registry的secret
(当然也可以手动修改这个json配置文件)
```
oc registry login --registry="<registry>" \
  --auth-basic="<username>:<password>" \
  --to=pull-secret.json
```

3.最后更新到集群中
```
oc set data secret/pull-secret -n openshift-config --from-file=.dockerconfigjson=pull-secret.json
```
这个操作需要一点时间, 会改动到所有的节点配置

#### 修正Insights Operator降级问题

参考《Restoring a degraded Insights Operator》
https://docs.openshift.com/container-platform/4.9/post_installation_configuration/connected-to-disconnected.html#connected-to-disconnected-restore-insights_connected-to-disconnected
=> 就是修改pull-secret， 去除掉 cloud.openshift.com 配置

导出pull-secret
```
oc extract secret/pull-secret -n openshift-config --confirm --to=.
# 导出的文件为 .dockerconfigjson
```

修改pull-secret并更新
```
# 修改文件 .dockerconfigjson, 去除cloud.openshift.com的配置
# 然后更新
oc set data secret/pull-secret -n openshift-config --from-file=.dockerconfigjson=./.dockerconfigjson
```

最后检查insight operator状态
```
[core@master1 insight-operator]$ oc get co insights
NAME       VERSION      AVAILABLE   PROGRESSING   DEGRADED   SINCE   MESSAGE
insights   4.x.x        True        False         False      xxxd
```

## 时间同步配置

## 配置数据存储

## 配置警报通知

## 参考文档

[ocp官方安装后配置](https://access.redhat.com/documentation/zh-cn/openshift_container_platform/4.9/html/post-installation_configuration/index)
