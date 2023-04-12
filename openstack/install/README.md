# openstack 安装

安装方法:
- manual
  手动安装所有服务...
- kolla-ansible
  安装过yoga版本
- devstack
  安装过yoga和z版本
- packstack
  待尝试, centos7可以试试, centos7支持最高openstack train版本

居然是关键字《kolla-ansible 版本支持》搜索到的。。。

[(OpenEuler 20.03 LTS SP3)OpenStack-Rocky 部署指南](https://docs.openeuler.org/zh/docs/20.03_LTS_SP3/docs/thirdparty_migration/OpenStack-rocky.html)

openEuler 20.03-LTS-SP3 版本官方认证的第三方 oepkg yum 源已经支持 Openstack-Rocky 版本，用户可以配置好 oepkg yum 源后根据此文档进行 OpenStack 部署。

[(OpenEuler 22.03 LTS SP1)OpenStack-Train 部署指南](https://docs.openeuler.org/zh/docs/22.03_LTS_SP1/docs/thirdparty_migration/OpenStack-train.html)

OpenStack SIG还提供了一键部署OpenStack all in one或三节点的ansible脚本，用户可以使用该脚本快速部署一套基于openEuler RPM的OpenStack环境。下面以all in one举例说明使用方法

使用yum安装kolla-ansible
```
yum install openstack-release-train
yum install openstack-kolla openstack-kolla-ansible
```
