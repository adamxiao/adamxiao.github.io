# ceph 安装

## ceph安装方式

关键字《ceph 部署方法》

- ceph-ansible
  https://docs.27ops.com/%E5%AD%98%E5%82%A8/centos8-ceph/

- ceph-deploy
  https://juejin.cn/post/7086381284733222948
  ceph-deploy部署方式ceph官方通知已不再维护，没有在Nautilus(v14.x)之后的版本测试过
  Ceph-deploy 只用于部署和管理 ceph 集群，客户端需要访问 ceph，需要部署客户端工具。

- kolla-ansible
  https://blog.csdn.net/boxrice007/article/details/112609646
  Train以及之前旧版本, 支持部署ceph

- kolla-ceph
  [(自动化)基于kolla的自动化部署ceph集群](https://www.cnblogs.com/acommoners/p/15946642.html)
  剥离自kolla-ansible?

- cephadm
  https://m.starcto.com/storage_scheme/302.html
  1.2 cephadm安装方式支持命令行CLI和GUI图形化（未来趋势）

### ceph-deploy部署

关键字《ceph-deploy 部署集群》

https://m.starcto.com/storage_scheme/302.html

## 旧的资料

[openstack ussuri版本基于内网三台物理机集群kolla-ansible部署及与ceph 集群 集成](https://www.cnblogs.com/weiwei2021/p/14200722.html)

[OpenStack集成Ceph](https://www.orchome.com/16757)

https://www.cnblogs.com/MarkGuo/p/17095781.html
安装部署ceph
7、ceph为对接openstack做准备

