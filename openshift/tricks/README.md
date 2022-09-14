# 技巧

一些小技巧，可能暂未归类

## 未分类

#### 更新pull-secret信息

关键字《openshift update pull secret》

参考： https://docs.microsoft.com/en-us/azure/openshift/howto-add-update-pull-secret

```bash
# 首先获取当前pull-secret
oc get secrets pull-secret -n openshift-config -o template='{{index .data ".dockerconfigjson"}}' | base64 -d > pull-secret.json

# 然后修改pull-secret.json文件
# xxx

# 最后更新pull-secret - 注意这个操作会导致节点依次都重启!!
oc set data secret/pull-secret -n openshift-config --from-file=.dockerconfigjson=./pull-secret.json
```

#### deployment更新

https://github.com/kubernetes/kubernetes/issues/27081
验证ok
```
oc -n nginx patch deployment nginx -p='{"spec":{"template":{"metadata":{"creationTimestamp":"'$( date --utc +%FT%TZ )'"}}}}'
```

https://www.kevinsimper.dk/posts/trigger-a-redeploy-in-kubernetes
```
kubectl patch deployment your_deployment -p "{\"spec\": {\"template\": {\"metadata\": { \"labels\": {  \"redeploy\": \"$(date +%s)\"}}}}}"
```
