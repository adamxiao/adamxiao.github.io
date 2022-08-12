# openshift使用

openshift container platform
容器云平台

## 云计算书籍收集

https://huataihuang.gitbooks.io/cloud-atlas/content/

## 参考文档

[jimmysong云原生gitbook文档](https://jimmysong.io/kubernetes-handbook/practice/traefik-ingress-installation.html)

[CSDN OpenShift 4.x Hands-on Lab](https://blog.csdn.net/weixin_43902588/article/details/105060359)

## 维护一些应用

#### adam-doc

通过源码构建adam-doc应用
```bash
# 可以看到新建应用都做了些什么事情
# oc new-app http://192.168.120.13/xiaoyun/adam-doc.git -o yaml > adam.yaml
# 新建项目，部署应用到这个项目中去
oc new-project s2i-adam-doc
oc new-app http://192.168.120.13/xiaoyun/adam-doc.git
# 创建route, 暴露service
oc expose service adam-doc
```

访问方式 `http://doc.iefcu.cn`

#### work-doc

使用镜像: `hub.iefcu.cn/xiaoyun/work-doc`

访问方式 `http://work.iefcu.cn`

#### wetty

使用镜像: `docker.io/wettyoss/wetty`
mirror镜像: `hub.iefcu.cn/public/wetty`

```
oc new-project wetty
docker run --rm -p 3000:3000 wettyoss/wetty --ssh-host 10.20.1.99 --ssh-port 22345 --ssh-user adam
```

访问方式 `http://tty.iefcu.cn/wetty`

#### nginx

使用镜像: `docker.io/library/nginx`
mirror镜像: `hub.iefcu.cn/public/nginx:stable`

提供独立ip, 然后反向代理一些内部web服务

```bash
oc create configmap nginx-conf --from-file=conf.d/
oc -n nginx create secret tls hub-iefcu-tls --cert=./hub.iefcu.cn_bundle.crt --key=./hub.iefcu.cn.key
oc -n nginx create secret tls iefcu-tls --cert=./fullchain.cer --key=./iefcu.cn.key
```

更新configmap
```
oc -n nginx create configmap nginx-conf --from-file=conf.d/ -o yaml --dry-run=client | oc replace -f -
```

通过metallb创建一个vip
```
cat << EOF | oc apply -f -
apiVersion: v1
kind: Service
metadata:
  name: nginx-vip
  namespace: nginx
  labels:
    app: nginx
  annotations:
    metallb.universe.tf/address-pool: metallb-addr35
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
    app: nginx
EOF
```

访问方式:
* http://hub.iefcu.cn
* http://gitlab.iefcu.cn
* ...
