# openstack packstack安装

TODO:

基于centos7.9云镜像

https://blog.51cto.com/u_4708948/2474756
```
yum install -y centos-release-openstack-train
yum install -y openstack-packstack
packstack --allinone
```

- 关闭selinux, 关闭防火墙
- 设置主机名
