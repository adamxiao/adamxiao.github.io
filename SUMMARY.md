# Summary

* [Introduction](README.md)
* [linux命令使用](bash.md)
   * [docker使用](docker.md)
   * [firewall使用](firewalld.md)
   * [git使用](git.md)
   * [nmcli配置网络](linux-command/nmcli.md)
   * [vim使用](vim.md)
   * [journalctl使用](linux-command/journalctl.md)
* [高级技巧](vpn.md)
   * [使用gitbook编写文档](gitbook.md)
   * [ssh反向隧道](scripts/ssh_reverse_tunnel.md)
   * [v2ray安装教程](scripts/V2Ray安装教程.md)
   * [openssl使用](tricks/openssl.md)
   * [openwrt安装使用](tricks/openwrt.md)
   * [vscode使用markdown说明](tricks/vscode-markdown.md)
* [openstack安装使用](openstack/README.md)
   * [devstack安装](openstack/devstack-install.md)
* [docker使用](docker-usage/README.md)
   * [docker基本使用](docker.md)
   * [unzip镜像解压文件](docker-usage/docker-unzip.md)
   * [skopeo拉取同步镜像](docker-usage/skopeo.md)
   * [搭建私有镜像仓库](docker-usage/registry.md)
   * [traefik使用middleware做基本认证](docker-usage/traefik-middleware.md)
* [docker镜像编译构建](docker-image-build/README.md)
   * [jit的centos8基础镜像](docker-image-build/centos8-build-env.md)
   * [istio镜像源码编译](docker-image-build/istio-image-build.md)
   * [docker多架构镜像编译方法](docker-image-build/multi-arch-build.md)
   * [使用podman镜像编译构建镜像](docker-image-build/use-podman-build-image.md)
* [openshift使用](openshift/README.md)
   * [k8s原理与使用简介 - 分享](openshift/k8s-usage-share-ppt.md)
   * [openshift基本安装](openshift/install/README.md)
       * [离线安装部署kcp文档](openshift/ocp-install.md)
       * [定制安装部署kcp技巧](openshift/ocp-custom-install.md)
       * [openshift 安装定制调研](openshift/install/install-customizing.md)
       * [新增htpasswd用户认证](openshift/install/add-basic-user.md)
       * [部署glusterfs存储类](openshift/install-glusterfs-sc.md)
       * [部署内部dns+haproxy等服务](openshift/deploy-internel-dns-haproxy.md)
       * [MetalLB安装以及使用方法](openshift/metallb-usage.md)
       * [禁止crio-wipe清理镜像](openshift/disable-crio-wipe.md)
       * [openshift安装部署traefik](docker-usage/traefik.md)
       * [内部镜像仓库配置使用](openshift/install/internel-registry-usage.md)
   * [openshift部署应用](openshift/deploy-app/README.md)
       * [adam-doc文档部署](openshift/deploy-app/adam-doc-deploy.md)
       * [创建自定义域名的路由](openshift/deploy-app/adam-doc-deploy.md)
       * [redis集群部署](openshift/deploy-app/redis-deploy.md)
       * [devops相关调研](openshift/devops/README.md)
       * [openshift pipeline安装使用](openshift/operator-install/pipeline-install.md)
   * [operatorhub离线搭建使用](openshift/operatorhub-offline.md)
       * [elasticsearch安装](openshift/operator-install/elasticsearch.md)
       * [cluster logging 日志安装](openshift/operator-install/cluster-logging.md)
       * [keycloak认证安装使用](docker-usage/keycloak-usage.md)
   * [quay私有镜像仓库镜像同步](openshift/sync-quay-image.md)
   * [制作新的openshift release镜像](openshift/create-ocp-release.md)
   * [console镜像构建方法](openshift/console-build.md)
   * [console镜像修改 - 监控相关修改](openshift/console-image-update.md)
   * [修改节点dns地址](openshift/network/update-node-dns.md)
   * [使用operator部署ES集群](openshift/deploy-elastic-operator.md)
   * [容器pid max limit限制配置](openshift/tricks/container-pidsLimit.md)
   * [openshift节点修改ip地址](openshift/tricks/update-node-ip.md)
   * [haproxy容器选择节点运行](openshift/tricks/haproxy-node-select.md)
   * [额外新增节点](openshift/install/add-new-node.md)
   * [traefik mesh安装配置使用](openshift/tricks/traefik-mesh.md)
   * [coreos系统pxe安装](openshift/tricks/coreos-pxe-install.md)
   * [openshift监控](openshift/monitor-app/README.md)
       * [promethues使用入门](openshift/monitor-app/promethues-usage.md)
       * [grafana监控面板安装使用](openshift/monitor-app/grafana-install.md)
   * [openshift日志](openshift/logs/README.md)
   * [kubernets client api使用](openshift/tricks/kubernetes-client-api.md)
   * [machine config原理调研](openshift/machine-config.md)
* [服务器虚拟化相关](openstack/README.md)
   * [基于ovs的namespace中的dhcp服务](openstack/ovs-namespace-dhcp.md)
   * [搭建ipsan存储服务的方法](tricks/san-server-setup.md)
