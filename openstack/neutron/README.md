# neutron

## neutron命令行使用

列举网络
```
openstack network list
openstack network show xxx
```

https://docs.openstack.org/ocata/user-guide/cli-create-and-manage-networks.html

创建网络
```
openstack network create net1
或者指定网络类型
openstack network create net2 --provider-network-type vxlan
```

创建子网
```
openstack subnet create subnet1 --network net1 --subnet-range 192.0.2.0/24
```
=> 有子网dhcp后, 会有一个network namespaces, 例如: qdhcp-96490706-7d0f-49a5-acc3-a886090368ec (id: 3)

列举子网
```
openstack subnet list
```

参考资料:
- [redhat openstack network create](https://access.redhat.com/documentation/zh-cn/red_hat_openstack_platform/10/html/command-line_interface_reference_guide/openstackclient_subcommand_network_create)

## 其他

#### devstack neutron网络配置

devstack neutron config
[Using DevStack with neutron Networking](https://docs.openstack.org/devstack/latest/guides/neutron.html)

```
## Neutron options
Q_USE_SECGROUP=True
FLOATING_RANGE="172.18.161.0/24"
IPV4_ADDRS_SAFE_TO_USE="10.0.0.0/22"
Q_FLOATING_ALLOCATION_POOL=start=172.18.161.250,end=172.18.161.254
PUBLIC_NETWORK_GATEWAY="172.18.161.1"
PUBLIC_INTERFACE=eth0

# Open vSwitch provider networking configuration
Q_USE_PROVIDERNET_FOR_PUBLIC=True
OVS_PHYSICAL_BRIDGE=br-ex
PUBLIC_BRIDGE=br-ex
OVS_BRIDGE_MAPPINGS=public:br-ex
```


## 参考资料

- [openvswitch 二层插件](https://docs.openstack.org/neutron/latest/contributor/internals/openvswitch_agent.html)
