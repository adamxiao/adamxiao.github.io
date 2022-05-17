# 虚拟路由高可用

* vr
* HA

[openstack FAQ](https://docs.openstack.org/networking-ovn/queens/admin/faq.html)
=> VR路由高可用一般是主备, 使用pacemaker
A typical deployment would use something like Pacemaker to manage the active/passive HA process. Clients would be pointed at a virtual IP address. When the HA manager detects a failure of the master, the virtual IP would be moved and the passive replica would become the new master.


[OpenStack网络指南（16）分布式虚拟路由与VRRP](https://blog.csdn.net/fyggzb/article/details/53924324)

控制节点配置
1.把以下部分加入/etc/neutron/neutron.conf:

[DEFAULT]
core_plugin = ml2
service_plugins = router
allow_overlapping_ips = True
router_distributed = True
l3_ha = True
l3_ha_net_cidr = 169.254.192.0/18
max_l3_agents_per_router = 3
min_l3_agents_per_router = 2
**当配置router_distributed = True标志时，所有用户创建的路由器是分布式的。 没有它，只有特权用户可以使用–distributed True创建分布式路由器。**
类似地，当配置l3_ha = True标志时，所有用户创建的路由器默认为HA。
因此，在配置文件中这两个标志设置为True，所有用户创建的路由器将默认为分布式HA路由器（DVR HA）。
同样可以通过具有管理凭据的用户在neutron router-create命令中设置标志来显式实现：

$ neutron router-create name-of-router --distributed=True --ha=True
