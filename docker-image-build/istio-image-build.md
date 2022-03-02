# istio镜像源码编译

istio镜像目前没有arm64架构的，需要自己从源码编译出来。

## istio相关镜像

通过describe pods查到缺少这个镜像，其他方法？
docker.io/istio/pilot:1.13.1
关键字《istio离线安装》

https://blog.csdn.net/u011943534/article/details/113180062

```bash
docker pull istio/proxyv2:1.5.5
docker pull grafana/grafana:6.5.2
docker pull jaegertracing/all-in-one:1.16
docker pull quay.io/kiali/kiali:v1.15
docker pull istio/pilot:1.5.5
docker pull prom/prometheus:v2.15.1
```

镜像对应的源码如下:

* https://github.com/istio/istio.git => tag 1.13.1
* https://github.com/istio/proxy.git => tag 1.13.1
  => 没有Dockerfile, 也没有说明怎么编译的?
  不过golang项目的编译都比较简单, 直接一个二进制就可以了
  貌似proxy就是envoy，是c++代码
  计划在ubuntu下编译构建(因为build/docker/BUILD文件里面有ubuntu, 网上文档也是ubuntu)
* ...

优先处理:
* docker.io/istio/proxyv2:1.13.1
* docker.io/istio/pilot:1.13.1

## 编译笔记记录

### 编译Istio-proxy：

```bash
$ ~/.go/src/istio.io/proxy$ pwd
/home/jingzhao/.go/src/istio.io/proxy
$ ~/.go/src/istio.io/proxy$ git checkout 9e5640ad290377b406d15b9a59f2c3f56af17323
$ ~/.go/src/istio.io/proxy$ make
$ ~/.go/src/istio.io/proxy$ ls bazel-out/aarch64-fastbuild/bin/src/envoy/envoy -l
-r-xr-xr-x 1 jingzhao jingzhao 107015072 Aug 7 11:58 bazel-out/aarch64-fastbuild/bin/src/envoy/envoy
```

自己尝试使用golang镜像编译
```bash
docker run -it --name golang \
  -v $PWD:/app \
  hub.iefcu.cn/public/golang:1.16 bash
```

尝试使用ubuntu镜像编译proxy
```bash
docker run -it --name tmp \
  -v $PWD:/app \
  hub.iefcu.cn/public/ubuntu:20.04 bash
```


## 笔记资料

#### 搜索编译arm64镜像

搜索关键字《arm64 安装istio》
发现有人给出如何编译istio的arm64版本方法，可以试试
https://aijishu.com/a/1060000000016469


https://bbs.huaweicloud.com/forum/thread-73441-1-1.html
你好，istio社区目前还不支持ARM64镜像，使用默认的istioctl工具无法自动化部署istio服务。
如需使用，建议参考https://aijishu.com/a/1060000000016469 进行镜像的手动编译、打包和运行；
另外也可以使用https://hub.docker.com/search?q=istio&type=image&architecture=arm64 raspbernetes的镜像进行运行尝试。


#### 使用istioctl安装istio

https://istio.io/latest/docs/setup/getting-started/

wget https://github.com/istio/istio/releases/download/1.13.1/istio-1.13.1-linux-arm64.tar.gz

$ istioctl install --set profile=openshift
=> 安装失败(首当其冲肯定是网络原因)

This will install the Istio 1.13.1 openshift profile with ["Istio core" "Istiod" "CNI" "Ingress gateways"] components into the cluster. Proceed? (y/N) y
✔ Istio core installed                                                                                                                                                                                     
✘ Istiod encountered an error: failed to wait for resource: resources not ready after 5m0s: timed out waiting for the condition                                                                            
  Deployment/istio-system/istiod (container failed to start: ImagePullBackOff: Back-off pulling image "docker.io/istio/pilot:1.13.1")
✘ CNI encountered an error: failed to wait for resource: resources not ready after 5m0s: timed out waiting for the conditionistio-ingressgateway                                                           
                                                                               
✘ Ingress gateways encountered an error: failed to wait for resource: resources not ready after 5m0s: timed out waiting for the condition                                                                  
  Deployment/istio-system/istio-ingressgateway (container failed to start: ContainerCreating: )
- Pruning removed resources                                                                                                                                                                                Error: failed to install manifests: errors occurred during operation

