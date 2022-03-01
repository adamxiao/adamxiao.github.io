# MetalLB安装以及使用方法

## 安装方法



## 使用方法

1. 首先配置地址池

```bash
cat << EOF | oc apply -f -
apiVersion: metallb.io/v1alpha1
kind: AddressPool
metadata:
  #namespace: metallb-system
  namespace: adam-test
  name: doc-example
spec:
  protocol: layer2
  addresses:
  - 10.90.3.27-10.90.3.29
EOF
```

2. 然后在service中使用这个地址池

```bash
cat << EOF | oc apply -f -
apiVersion: v1
kind: Service
metadata:
  name: traefik-ingress
  namespace: grzs-traefik
  labels:
    app: traefik
  annotations:
    metallb.universe.tf/address-pool: doc-example
spec:
  ports:
  - name: https
    protocol: TCP
    port: 443
    targetPort: 443
  - name: http
    protocol: TCP
    port: 80
    targetPort: 80
  type: LoadBalancer
  selector:
    app: traefik
EOF
```

3. 最后查看svc自动分配的ip地址，以及访问

```bash
oc -n grzs-traefik get svc traefik-ingress
```

![](2022-03-01-15-41-29.png)


## 参考资料

[openshift官方文档 - 配置 METALLB 地址池](https://access.redhat.com/documentation/zh-cn/openshift_container_platform/4.9/html/networking/metallb-configure-address-pools)