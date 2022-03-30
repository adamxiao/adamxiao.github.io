# kubernets client api使用

目的就是使用api创建CRD资源，例如IngressRoute

## api接口说明

官方有多种语言的client api, 有java, python, golang等，参考: 
其实最终也是封装调用了k8s的restfull api接口

#### api接口调用方式

k8s提供了多种认证方式来保证集群的安全性：比如客户端证书、静态token、静态密码文件、ServiceAccountTokens等等
你可以同时使用一种或多种认证方式。只要通过任何一个都被认作是认证通过，我们一般都是使用证书方式：客户端证书认证叫作TLS双向认证。

* 客户端证书
* 静态token
* 静态密码文件
* ServiceAccountTokens
* ...

#### api功能说明

[CRD资源增删改查](https://www.kubernetes.org.cn/8984.html)

* createClusterCustomObject	POST /apis/{group}/{version}/{plural}	创建集群范围CRD资源对象
* createNamespacedCustomObject POST /apis/{group}/{version}/namespaces/{namespace}/{plural}	创建分区范围CRD资源对象
* ...

* KubectlExample.java
  log, exec等接口
* YamlExample.java
  Suggested way to load or dump resource in Yaml
  get -o yaml， 输出资源为yaml文件的
  create -f xxx.yaml!!!!
* KubeConfigFileClientExample.java
  就是加载kubeconfig配置文件

* PatchExample.java
  指定是去patch Deployment的

* GenericClientExample.java
  -> xxx

## java调用k8s api

参考：
* [K8S——java调用OpenApi_木冰的专栏-程序员秘密_java 调用k8s](https://www.cxymm.net/article/mubing870825/98480559)
* [java kubernets client仓库文档](https://github.com/kubernetes-client/java/blob/master/examples/examples-release-14/src/main/java/io/kubernetes/client/examples/KubeConfigFileClientExample.java)

#### 在pom文件引用jar包：

在pom文件引用jar包：
```xml
    <dependency>
      <groupId>io.kubernetes</groupId>
      <artifactId>client-java</artifactId>
      <version>4.0.0</version>
      <scope>compile</scope>
    </dependency>
    <dependency>
      <groupId>com.squareup.okio</groupId>
      <artifactId>okio</artifactId>
      <version>2.3.0</version>
    </dependency>
    <dependency>
      <groupId>com.squareup.okhttp</groupId>
      <artifactId>okhttp</artifactId>
      <version>2.5.0</version>
    </dependency>
```

#### java代码调用k8s api

就是kubectl get pods -A的效果

[就是api文档中的官方示例代码](https://github.com/kubernetes-client/java/blob/master/examples/examples-release-14/src/main/java/io/kubernetes/client/examples/Example.java)

```java
package com.data.k8s;

import java.io.IOException;
import io.kubernetes.client.ApiClient;
import io.kubernetes.client.ApiException;
import io.kubernetes.client.Configuration;
import io.kubernetes.client.apis.CoreV1Api;
import io.kubernetes.client.models.V1Node;
import io.kubernetes.client.models.V1NodeList;
import io.kubernetes.client.models.V1Pod;
import io.kubernetes.client.models.V1PodList;
import io.kubernetes.client.util.Config;

public class App 
{
    public static void main( String[] args ) throws IOException, ApiException
    {
        ApiClient client=Config.fromConfig("c:/kubelet.conf");
        Configuration.setDefaultApiClient(client);
        
        CoreV1Api api=new CoreV1Api();
        
        V1PodList list=api.listPodForAllNamespaces(null, null, null, null, null, null, null, null, null);
        for (V1Pod item:list.getItems()) {
            System.out.println( item.getMetadata().getName());
        }
    }
}
```

#### java创建CRD示例

TODO: 尚未未测试验证

[使用helm-controller-简化容器云平台应用商店的开发开发手册](https://www.liangzl.com/get-article-detail-178147.html)

创建
```java
var customObjectsApi = new  CustomObjectsApi(apiClient);
var json = new JsonObjectBuilder()  
       .set("apiVersion", "app.alauda.io/v1alpha1")  
       .set("kind", "HelmRequest")  
       .set("metadata", new JsonObjectBuilder().set("name", name).build())  
       .set("spec", new JsonObjectBuilder()  
               .set("chart", chart)  
               .set("namespace", namespace)  
               .set("releaseName", name)  
               .set("values", Map2JsonUtil.map2Json(params))  
               .set("version", version)  
       ).build();

customObjectsApi.createNamespacedCustomObject("app.alauda.io","v1alpha1", "default", "helmrequests", json, null);
```

卸载
```java
var customObjectsApi = new  CustomObjectsApi(apiClient);
customObjectsApi.deleteNamespacedCustomObject("app.alauda.io", "v1alpha1", "default","helmrequests", "test-nginx",new  V1DeleteOptions().gracePeriodSeconds(0L).propagationPolicy("Foreground"),null, null, null);
```


#### java使用token调用api

TOOD: 未测试验证

```java
ApiClient client =  new ClientBuilder().
        setBasePath(master节点的ip和端口，默认端口6443).setVerifyingSsl(false).
        setAuthentication(new AccessTokenAuthentication(操作前置生成的token)).build();
Configuration.setDefaultApiClient(client);

CoreV1Api api = new CoreV1Api();
```

## python调用k8s api

参考: https://github.com/kubernetes-client/python

#### 安装python kubernets客户端api库

以我在ubuntu 20.04下使用为例:
```bash
sudo apt install -y python3-pip
pip3 install kubernetes
```

#### python创建IngressRoute示例

参考: https://blog.csdn.net/Neil_001/article/details/103675609

创建test.py
```python
#!/usr/bin/env python3
  
from os import path
import yaml
from kubernetes import client, config

def main():
    config.load_kube_config()

    # with open(path.join(path.dirname(__file__), "config_map.yaml")) as f:   #从yaml加载ConfigMap
        # cm = yaml.safe_load(f)
        # k8s_core_v1 = client.CoreV1Api
        # k8s_core_v1.create_namespaced_config_map(body=cm, namespace="default")

    # TODO: 从yaml中加载？
    vcjob = {
        'apiVersion': 'traefik.containo.us/v1alpha1',
        'kind': 'IngressRoute',
        'metadata': {'name': 'traefik-dashboard'},
        'spec': {
          'entryPoints': ["web"],
          'routes': [
            {
              "match": "Host(`kmaster.iefcu.cn`)",
              "kind": "Rule",
              "services": [
                {
                  "name": "traefik-admin",
                  "port": "8080",
                  }
                ],
              }
            ],
          },
        }

    api = client.CustomObjectsApi()
    # vcjob = {...}
    api.create_namespaced_custom_object(            #使用用户自定义api创建vcjob
        group="traefik.containo.us",
        version="v1alpha1",
        namespace="default",
        # plural="jobs",
        plural="ingressroutes", # 这破参数后面的版本才有的吧，不填应该也可以吧？
        body=vcjob,
    )

if __name__ == "__main__":
    main()
```

对应命令行创建ingress的yaml文件如下:
```yaml
apiVersion: traefik.containo.us/v1alpha1
kind: IngressRoute
metadata:
  name: traefik-dashboard
  namespace: grzs-traefik
spec:
  entryPoints:
    - web
  routes:
  - match: Host(`kmaster.iefcu.cn`)
    kind: Rule
    services:
    - name: traefik-admin
      port: 8080
```

## 其他

#### 获取serviceaccount token

```bash
oc -n default serviceaccounts get-token grafana-serviceaccount
```

## FAQ

#### kubernetes.client.exceptions.ApiException
Reason: Unprocessable Entity

HTTP response headers: HTTPHeaderDict({'Audit-Id': 'e6fecbe1-1719-42d4-984e-eada4d925569', 'Cache-Control': 'no-cache, private', 'Content-Type': 'application/json', 'X-Kubernetes-Pf-Flowschema-Uid': 'c5c2578e-ac1c-4ce1-9409-588f757fae02', 'X-Kubernetes-Pf-Prioritylevel-Uid': '8ae59bdf-1cfd-4013-9a85-408918bcc37c', 'Date': 'Tue, 29 Mar 2022 03:26:40 GMT', 'Content-Length': '375'})

HTTP response body: {"kind":"Status","apiVersion":"v1","metadata":{},"status":"Failure","message":"IngressRoute.traefik.containo.us \"traefik-dashboard\" is invalid: spec: Required value","reason":"Invalid","details":{"name":"traefik-dashboard","group":"traefik.containo.us","kind":"IngressRoute","causes":[{"reason":"FieldValueRequired","message":"Required value","field":"spec"}]},"code":422}

原因是spec参数没有，无法处理请求，把参数配置正确即可

## 参考文档

* [(好)使用 Java 操作 Kubernetes API](https://www.kubernetes.org.cn/8984.html)

* [K8S——java调用OpenApi_木冰的专栏-程序员秘密_java 调用k8s](https://www.cxymm.net/article/mubing870825/98480559)

* [Java语言启动训练任务Demo](https://support.huaweicloud.com/usermanual-mindxdl202/atlasmindx_02_0003.html)
  同时还有go语言的版本，python语言的版本(最简单)。
  TODO: 有加载yaml文件的用法, 可以试试

* [Kubernets官方客户端库](https://kubernetes.io/zh/docs/reference/using-api/client-libraries/)

