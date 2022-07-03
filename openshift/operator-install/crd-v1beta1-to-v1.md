# crd版本从v1beta升级到v1版本

关键字《crd v1beta1 to v1》

[ucloud的redis operator](https://github.com/ucloud/redis-operator)

```
kubectl create -f deploy/crds/redis_v1beta1_rediscluster_crd.yaml

# wget https://raw.githubusercontent.com/ucloud/redis-operator/master/deploy/crds/redis_v1beta1_rediscluster_crd.yaml
```

## 适配修改过程

参考: https://redhat-connect.gitbook.io/certified-operator-guide/ocp-deployment/operator-metadata/update-crds-from-v1beta1
> Here's a sample CRD shown before and after conversion. The apiVersion is changed to v1, and the schema is now defined per CR version (in v1beta1, you could only define per-version schemas if they were  different).

首先修改v1beta名称为v1, 遇到问题

```
The CustomResourceDefinition "redisclusters.redis.kun" is invalid: spec.versions[0].schema.openAPIV3Schema: Required value: schemas are required
```

缺少schema, 把validation的内容移到versions下面?
schema.openAPIV3Schema 
添加versions[0].schema, 把spec.validation.openAPIV3Schema移动到schema下面,
**但是需要注意，有一个type: object需要处理**

加一个openAPIV3Schema.type: object就可以了
```
The CustomResourceDefinition "redisclusters.redis.kun" is invalid: spec.validation.openAPIV3Schema.type: Required value: must not be empty at the root
```

## 参考资料

* [update-crds-from-v1beta1](https://redhat-connect.gitbook.io/certified-operator-guide/ocp-deployment/operator-metadata/update-crds-from-v1beta1)
* [Versions in CustomResourceDefinitions](https://kubernetes.io/docs/tasks/extend-kubernetes/custom-resources/custom-resource-definition-versioning/)
