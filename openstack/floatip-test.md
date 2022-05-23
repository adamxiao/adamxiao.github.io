# openstack配置浮动ip测试

## xxx

## 其他资料

## 参考资料

[api接口参数详解 - 9.2. Creating virtual networks](https://docs.virtuozzo.com/virtuozzo_hybrid_infrastructure_4_6_compute_api_reference/managing-virtual-networks/creating-virtual-networks.html)
provider:physical_network (Optional) => 对应ovs桥的映射名称?devstack建的到底是什么呢?

创建外部网络, 物理网络这个参数到底应该怎么填?
https://opensource.com/article/17/4/openstack-neutron-networks

这样, 我的devstack中没有!
```
ovs-vsctl list-ports br-ex

eth1
phy-br-ex

ovs-vsctl list-ports br-ex2

eth2
phy-br-ex2
```


[Red Hat OpenStack Platform - Chapter 9. Connect an instance to the physical network](https://access.redhat.com/documentation/en-us/red_hat_openstack_platform/8/html/networking_guide/sec-connect-instance)

3. Configure the physical networks in /etc/neutron/plugins/ml2/openvswitch_agent.ini and map the bridge to the physical network:
Note
For more information on configuring bridge_mappings, see Chapter 13, Configure Bridge Mappings.
```
bridge_mappings = physnet1:br-ex
```
