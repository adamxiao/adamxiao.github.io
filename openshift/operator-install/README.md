# operator应用安装

xxx
      operatorframework.io/arch.arm64: supported

elasticsearch这个operator标明不支持arm64, 所以web页面上不能安装？ => 确实是的!
```bash
oc -n openshift-operators get clusterserviceversion -o yaml

    labels:
      olm.api.9337dac30a6def29: provided
      olm.api.e43efcaa45c9f8d0: provided
      olm.copiedFrom: openshift-operators-redhat
      operatorframework.io/arch.amd64: supported
      operatorframework.io/arch.ppc64le: supported
      operatorframework.io/arch.s390x: supported
    name: elasticsearch-operator.5.3.4-13
```

#### openshift-install编译

源码： https://github.com/openshift/installer#release-4.8

```diff
diff --git a/images/baremetal/Dockerfile.ci b/images/baremetal/Dockerfile.ci
index 1a51ddb..cf1f928 100644
--- a/images/baremetal/Dockerfile.ci
+++ b/images/baremetal/Dockerfile.ci
@@ -1,21 +1,22 @@
 # This Dockerfile is a used by CI to publish an installer image
 # It builds an image containing openshift-install.

-FROM registry.ci.openshift.org/ocp/builder:rhel-8-golang-1.16-openshift-4.8 AS builder
-RUN yum install -y libvirt-devel-6.0.0 && \
-    yum clean all && rm -rf /var/cache/yum/*
+FROM hub.iefcu.cn/public/golang:1.16 AS builder
+#RUN yum install -y libvirt-devel-6.0.0 && \
+#    yum clean all && rm -rf /var/cache/yum/*
+RUN apt update && apt install -y libvirt-dev
 WORKDIR /go/src/github.com/openshift/installer
 COPY . .
 RUN TAGS="libvirt baremetal" hack/build.sh


-FROM registry.ci.openshift.org/ocp/4.8:base
+FROM hub.iefcu.cn/library/centos:7
 COPY --from=builder /go/src/github.com/openshift/installer/bin/openshift-install /bin/openshift-install
 COPY --from=builder /go/src/github.com/openshift/installer/data/data/rhcos.json /var/cache/

 RUN yum update -y && \
     yum install --setopt=tsflags=nodocs -y \
-    libvirt-libs-6.0.0 openssl unzip jq openssh-clients && \
+    libvirt-libs openssl unzip jq openssh-clients && \
     yum clean all && rm -rf /var/cache/yum/* && \
     chmod g+w /etc/passwd
```

Dockerfile.adam
```dockerfile
# This Dockerfile is a used by CI to publish an installer image
# It builds an image containing openshift-install.

FROM hub.iefcu.cn/public/golang:1.16 AS builder
RUN apt update && apt install -y libvirt-dev
WORKDIR /go/src/github.com/openshift/installer
COPY . .
RUN TAGS="libvirt baremetal" hack/build.sh


FROM hub.iefcu.cn/public/debian:bullseye
COPY --from=builder /go/src/github.com/openshift/installer/bin/openshift-install /bin/openshift-install
COPY --from=builder /go/src/github.com/openshift/installer/data/data/rhcos.json /var/cache/

RUN apt update && \
    apt install -y \
    libvirt-clients openssl unzip jq openssh-client && \
    chmod g+w /etc/passwd

RUN mkdir /output && chown 1000:1000 /output
USER 1000:1000
ENV PATH /bin
ENV HOME /output
WORKDIR /output
ENTRYPOINT ["/bin/openshift-install"]
```

```
#docker build --build-arg http_proxy=http://10.90.2.11:1087 --build-arg https_proxy=http://10.90.2.11:1087 -f images/baremetal/Dockerfile.ci -t hub.iefcu.cn/xiaoyun/ocp-build:4.8.9-x86_64-openshift-install-new .
docker build --build-arg http_proxy=http://10.90.2.11:1087 --build-arg https_proxy=http://10.90.2.11:1087 -f Dockerfile.adam -t hub.iefcu.cn/xiaoyun/ocp-build:4.8.9-x86_64-openshift-install-new .
```

#### cluster-authentication-operator

源码: https://github.com/openshift/cluster-authentication-operator#release-4.8

```diff
diff --git a/Dockerfile.rhel7 b/Dockerfile.rhel7
index adacb7c..6fd1549 100644
--- a/Dockerfile.rhel7
+++ b/Dockerfile.rhel7
@@ -1,10 +1,10 @@
-FROM registry.ci.openshift.org/ocp/builder:rhel-8-golang-1.15-openshift-4.8 AS builder
+FROM hub.iefcu.cn/public/golang:1.16 AS builder
 WORKDIR /go/src/github.com/openshift/cluster-authentication-operator
 COPY . .
 ENV GO_PACKAGE github.com/openshift/cluster-authentication-operator
 RUN go build -ldflags "-X $GO_PACKAGE/pkg/version.versionFromGit=$(git describe --long --tags --abbrev=7 --match 'v[0-9]*')" -tags="ocp" -o authentication-operator ./cmd/authenticati

-FROM registry.ci.openshift.org/ocp/4.8:base
+FROM hub.iefcu.cn/library/centos:7
 COPY --from=builder /go/src/github.com/openshift/cluster-authentication-operator/authentication-operator /usr/bin/
 COPY manifests /manifests
 COPY vendor/github.com/openshift/api/operator/v1/0000_50_cluster-authentication-operator_01_config.crd.yaml /manifests/01_config.crd.yaml
```

编译
```bash
docker build -f Dockerfile.rhel7 -t hub.iefcu.cn/xiaoyun/ocp-build:4.8.9-x86_64-cluster-authentication-operator .
```

#### machine-config-daemon

https://github.com/openshift/machine-config-operator.git#release-4.8

```
diff --git a/Dockerfile b/Dockerfile
index 2072ea3..d42a441 100644
--- a/Dockerfile
+++ b/Dockerfile
@@ -1,11 +1,11 @@
-FROM registry.ci.openshift.org/ocp/builder:rhel-8-golang-1.15-openshift-4.8 AS builder
+FROM hub.iefcu.cn/public/golang:1.16 AS builder
 WORKDIR /go/src/github.com/openshift/machine-config-operator
 COPY . .
 # FIXME once we can depend on a new enough host that supports globs for COPY,
 # just use that.  For now we work around this by copying a tarball.
 RUN make install DESTDIR=./instroot && tar -C instroot -cf instroot.tar .

-FROM registry.ci.openshift.org/ocp/4.8:base
+FROM hub.iefcu.cn/library/centos:7
 COPY --from=builder /go/src/github.com/openshift/machine-config-operator/instroot.tar /tmp/instroot.tar
 RUN cd / && tar xf /tmp/instroot.tar && rm -f /tmp/instroot.tar
 COPY install /manifests
diff --git a/pkg/daemon/osrelease.go b/pkg/daemon/osrelease.go
index fc42c07..c68ca74 100644
--- a/pkg/daemon/osrelease.go
+++ b/pkg/daemon/osrelease.go
@@ -19,7 +19,7 @@ type OperatingSystem struct {

 // IsRHCOS is true if the OS is RHEL CoreOS
 func (os OperatingSystem) IsRHCOS() bool {
-       return os.ID == "rhcos"
+       return os.ID == "rhcos" || os.ID == "KylinSecOS"
 }

 // IsFCOS is true if the OS is RHEL CoreOS
```

编译
```
docker build -t hub.iefcu.cn/xiaoyun/ocp-build:4.8.9-x86_64-machine-config-operator .
```

#### console-operator

https://github.com/openshift/console-operator#release-4.8

```diff
diff --git a/Dockerfile.rhel7 b/Dockerfile.rhel7
index 355c557..f297407 100644
--- a/Dockerfile.rhel7
+++ b/Dockerfile.rhel7
@@ -1,10 +1,10 @@
-FROM registry.ci.openshift.org/ocp/builder:rhel-8-golang-1.16-openshift-4.8 AS builder
+FROM hub.iefcu.cn/public/golang:1.16 AS builder
 WORKDIR /go/src/github.com/openshift/console-operator
 COPY . .
 ENV GO_PACKAGE github.com/openshift/console-operator
 RUN go build -ldflags "-X $GO_PACKAGE/pkg/version.versionFromGit=$(git describe --long --tags --abbrev=7 --match 'v[0-9]*')" -tags="ocp" -o console ./cmd/console

-FROM registry.ci.openshift.org/ocp/4.8:base
+FROM hub.iefcu.cn/library/centos:7
 RUN useradd console-operator
 USER console-operator
 COPY --from=builder /go/src/github.com/openshift/console-operator/console /usr/bin/console
```

构建镜像
```bash
docker build -f ./Dockerfile.rhel7 -t hub.iefcu.cn/xiaoyun/ocp-build:4.8.9-x86_64-console-operator  .
```

#### oauth-server

origin  https://github.com/openshift/oauth-server (fetch)
branch: 374e2ee38a1910c6d56172e9d4ec1828c4dea1be

主要修改了写死用kylinlogo

```diff
diff --git a/Makefile b/Makefile
index f494c25..5fae9c4 100644
--- a/Makefile
+++ b/Makefile
@@ -1,6 +1,8 @@
 all: build
 .PHONY: all

+export SHELL := $(shell which bash)
+
 # Include the library makefile
 include $(addprefix ./vendor/github.com/openshift/build-machinery-go/make/, \
        golang.mk \
diff --git a/images/Dockerfile.rhel b/images/Dockerfile.rhel
index 7f8726d..ad28f25 100644
--- a/images/Dockerfile.rhel
+++ b/images/Dockerfile.rhel
@@ -1,10 +1,10 @@
-FROM registry.ci.openshift.org/ocp/builder:rhel-8-golang-1.15-openshift-4.8 AS builder
+FROM hub.iefcu.cn/public/golang:1.16 AS builder
 WORKDIR /go/src/github.com/openshift/oauth-server
 COPY . .
 ENV GO_PACKAGE github.com/openshift/oauth-server
 RUN make build --warn-undefined-variables

-FROM registry.ci.openshift.org/ocp/4.8:base
+FROM hub.iefcu.cn/library/centos:7
 COPY --from=builder /go/src/github.com/openshift/oauth-server/oauth-server /usr/bin/
 ENTRYPOINT ["/usr/bin/oauth-server"]
 LABEL io.k8s.display-name="OpenShift OAuth Server" \
diff --git a/pkg/server/errorpage/templates.go b/pkg/server/errorpage/templates.go
index 11eb239..a103c64 100644
--- a/pkg/server/errorpage/templates.go
+++ b/pkg/server/errorpage/templates.go
@@ -125,7 +125,7 @@ body { background-color: var(--pf-global--BackgroundColor--dark-100); }
     <div class="pf-c-login">
       <div class="pf-c-login__container">
         <header class="pf-c-login__header">
-          <img src="data:image/svg+xml;base64,PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0idXRmLTgiPz4KPCEtLSBHZW5lcmF0b3I6IEFkb2JlIElsbHVzdHJhdG9yIDIyLjEuMCwgU1ZHIEV4cG9ydCBQbHVnLUluIC4g
+          <img src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAOYAAABGCAYAAADYduhVAAATAUlEQVR4Xu1dC7BVVRlee+9zDhC+QEl8xQVGJZUbBeKU5qNAEEPU4go4NdqMMqiAVAbT2ITZQ5pMhRmNm45pBQaOgYC8

         </header>
         <main class="pf-c-login__main">
diff --git a/pkg/server/login/templates.go b/pkg/server/login/templates.go
index d052170..f7c4835 100644
--- a/pkg/server/login/templates.go
+++ b/pkg/server/login/templates.go
@@ -241,7 +241,7 @@ select.pf-c-form-control.pf-m-success { --pf-c-form-control--PaddingRight: var(-
     <div class="pf-c-login">
       <div class="pf-c-login__container">
         <header class="pf-c-login__header">
-          <img src="data:image/svg+xml;base64,PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0idXRmLTgiPz4KPCEtLSBHZW5lcmF0b3I6IEFkb2JlIElsbHVzdHJhdG9yIDIyLjEuMCwgU1ZHIEV4cG9ydCBQbHVnLUluIC4g
+               <img src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAOYAAABGCAYAAADYduhVAAATAUlEQVR4Xu1dC7BVVRlee+9zDhC+QEl8xQVGJZUbBeKU5qNAEEPU4go4NdqMMqiAVAbT2ITZQ5pMhRmNm45pBQa

         </header>
         <main class="pf-c-login__main">
diff --git a/pkg/server/selectprovider/selectprovider.go b/pkg/server/selectprovider/selectprovider.go
index cb09b28..ad26a5b 100644
--- a/pkg/server/selectprovider/selectprovider.go
+++ b/pkg/server/selectprovider/selectprovider.go
@@ -39,15 +39,15 @@ type ProviderData struct {
 // allow branding of the page. Uses the default if customSelectProviderTemplateFile is not set.
 func NewSelectProviderRenderer(customSelectProviderTemplateFile string) (*selectProviderTemplateRenderer, error) {
        r := &selectProviderTemplateRenderer{}
-       if len(customSelectProviderTemplateFile) > 0 {
-               customTemplate, err := template.ParseFiles(customSelectProviderTemplateFile)
-               if err != nil {
-                       return nil, err
-               }
-               r.selectProviderTemplate = customTemplate
-       } else {
-               r.selectProviderTemplate = defaultSelectProviderTemplate
-       }
+       //if len(customSelectProviderTemplateFile) > 0 {
+               //customTemplate, err := template.ParseFiles(customSelectProviderTemplateFile)
+               //if err != nil {
+                       //return nil, err
+               //}
+               //r.selectProviderTemplate = customTemplate
+       //} else {
+       //}
+       r.selectProviderTemplate = defaultSelectProviderTemplate

        return r, nil
 }
diff --git a/pkg/server/selectprovider/templates.go b/pkg/server/selectprovider/templates.go
index e3b5b2b..e1f39d5 100644
--- a/pkg/server/selectprovider/templates.go
+++ b/pkg/server/selectprovider/templates.go
@@ -182,7 +182,7 @@ body { background-color: var(--pf-global--BackgroundColor--dark-100); }
     <div class="pf-c-login">
       <div class="pf-c-login__container">
         <header class="pf-c-login__header">
-          <img src="data:image/svg+xml;base64,PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0idXRmLTgiPz4KPCEtLSBHZW5lcmF0b3I6IEFkb2JlIElsbHVzdHJhdG9yIDIyLjEuMCwgU1ZHIEV4cG9ydCBQbHVnLUluIC4g
+          <img src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAOYAAABGCAYAAADYduhVAAATAUlEQVR4Xu1dC7BVVRlee+9zDhC+QEl8xQVGJZUbBeKU5qNAEEPU4go4NdqMMqiAVAbT2ITZQ5pMhRmNm45pBQaOgYC8

         </header>
         <main class="pf-c-login__main">
```


```dockerfile
FROM hub.iefcu.cn/public/golang:1.16-arm AS builder
WORKDIR /go/src/github.com/openshift/oauth-server
COPY . .
ENV GO_PACKAGE github.com/openshift/oauth-server
RUN make build --warn-undefined-variables

FROM hub.iefcu.cn/xiaoyun/openshift4-aarch64:4.9.0-rc.6-arm64-oauth-server
COPY --from=builder /go/src/github.com/openshift/oauth-server/oauth-server /usr/bin/
ENTRYPOINT ["/usr/bin/oauth-server"]
LABEL io.k8s.display-name="OpenShift OAuth Server" \
      io.k8s.description="This is a component of OpenShift and enables cluster authentication" \
      com.redhat.component="oauth-server" \
      name="openshift/ose-oauth-server" \
      io.openshift.tags="openshift, oauth-server"
```

```bash
#docker build -f ./images/Dockerfile.adam -t hub.iefcu.cn/xiaoyun/openshift4-aarch64:4.9.0-rc.6-arm64-oauth-server-new .
docker build -f ./images/Dockerfile.rhel -t hub.iefcu.cn/xiaoyun/ocp-build:4.8.9-x86_64-oauth-server .
```

#### oc

origin  https://github.com/openshift/oc (fetch)
release-4.8

```diff
diff --git a/Makefile b/Makefile
index 8de1907..e44338d 100644
--- a/Makefile
+++ b/Makefile
@@ -1,6 +1,8 @@
 all: build
 .PHONY: all

+export SHELL := $(shell which bash)
+
 ifdef OS_GIT_VERSION
 SOURCE_GIT_TAG := ${OS_GIT_VERSION}
 endif
diff --git a/images/cli/Dockerfile.rhel b/images/cli/Dockerfile.rhel
index 99c0543..14f720d 100644
--- a/images/cli/Dockerfile.rhel
+++ b/images/cli/Dockerfile.rhel
@@ -1,9 +1,10 @@
-FROM registry.ci.openshift.org/ocp/builder:rhel-7-golang-1.16-openshift-4.8 AS builder
+FROM hub.iefcu.cn/public/golang:1.16 AS builder
 WORKDIR /go/src/github.com/openshift/oc
 COPY . .
+RUN apt update && apt install -y libkrb5-dev
 RUN make build --warn-undefined-variables

-FROM registry.ci.openshift.org/ocp/4.8:base
+FROM hub.iefcu.cn/library/centos:7
 COPY --from=builder /go/src/github.com/openshift/oc/oc /usr/bin/
 RUN for i in kubectl openshift-deploy openshift-docker-build openshift-sti-build openshift-git-clone openshift-manage-dockerfile openshift-extract-image-content openshift-recycle; do
 LABEL io.k8s.display-name="OpenShift Client" \
```

构建镜像
```
docker build --build-arg http_proxy=http://10.90.2.11:1087 --build-arg https_proxy=http://10.90.2.11:1087 -f images/cli/Dockerfile.rhel -t hub.iefcu.cn/xiaoyun/ocp-build:4.8.9-x86_64-oc .
```

#### coredns

origin  https://github.com/openshift/coredns.git (fetch)


```
#FROM hub.iefcu.cn/public/debian:stable-slim
FROM hub.iefcu.cn/xiaoyun/ky3.3-6:base

# fuck, 构建有问题
#RUN yum makecache \
#       && yum install -y ca-certificates && update-ca-certificates \
#       && yum clean all

FROM scratch

COPY --from=0 /etc/ssl/certs /etc/ssl/certs
ADD coredns /coredns

EXPOSE 53 53/udp
ENTRYPOINT ["/coredns"]
```

```
# 1. 先使用原生的coredns的Dockerfile构建镜像验证一下.
# 缺点： 没有shell
# ...
podman build -f Dockerfile.adam -t hub.iefcu.cn/xiaoyun/ocp-build:4.8.9-x86_64-coredns .
```
