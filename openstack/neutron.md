# neutron相关资料

分析neutron接口，设计网络虚拟化接口

问题:
* ML2组件是什么意思?
https://www.bookstack.cn/read/openstack_understand_Neutron/appendix_install-README.md
=> 猜测后续的版本使用ovn这个二层了? 还可以看看配置文件 /etc/neutron/plugins/ml2/ml2_conf.ini(neutron插件)
[OpenStack —— 网络服务Neutron(五)](https://blog.51cto.com/wzlinux/1962561)
plugin解决的是What的问题，即网络要配置成什么样子？而至于如何配置How的工作则交由agent完成。
plugin，agent和network provider是配套使用的，比如上例中network provider是linux bridge，那么就得使用linux bridge的plungin和agent；如果network provider换成了OVS或者物理交换机，plugin 和agent也得替换。
plugin的一个主要的职责是在数据库中维护Neutron网络的状态信息，这就造成一个问题：所有network provider的plugin都要编写一套非常类似的数据库访问代码。为了解决这个问题，Neutron在H版本实现了一个ML2（Modular Layer 2）plugin，对plugin的功能进行抽象和封装。有了ML2 plugin，各种 network provider无需开发自己的plugin，只需要针对ML2开发相应的driver就可以了，工作量和难度都大大减少。

* l2population
https://www.cnblogs.com/CloudMan6/p/6064244.html
L2 Population 是用来提高 VXLAN 网络 Scalability 的。

现在假设 Host 1 上的 VM A 想与 Host 4 上的 VM G 通信。
VM A 要做的第一步是获知 VM G 的 MAC 地址。
于是 VM A 需要在整个 VXLAN 网络中广播 APR 报文：“VM G 的 MAC 地址是多少？”

如果 VXLAN 网络的节点很多，广播的成本会很大，这样 Scalability 就成问题了。
幸好 L2 Population 出现了。

https://www.jianshu.com/p/86e15a943617
VTEP 是如何提前获知 IP -- MAC -- VTEP 相关信息的呢？
就是l2population实现的功能

[OpenStack（六）Neutron部署](https://www.linux-note.cn/?p=3484)

Neutron负责管理OpenStack内部网络，其部署的模型有两种，分别是Provider networks（提供者网络）和Self-service networks（自服务网络）。

Provider networks一般称之为提供者网络，也称之为单一扁平网络，是OpenStack中最简单的网络模型。该模型利用虚拟网桥的方式，将所有虚拟机实例和宿主机运行于同一网络，相当于这是一个2层网络模型。

## ML2分析

就是二层配置?

/etc/neutron/plugins/ml2/ml2_conf.ini
```conf
[ml2]
tenant_network_types = geneve
extension_drivers = port_security,qos
type_drivers = local,flat,vlan,geneve
mechanism_drivers = ovn,logger
```
Rock版本的 mechanism_drivers 为openvswitch

旧的版本实现是靠这个rpm包?
openstack-neutron-ml2
还有neutron-linuxbridge-agent这个包, 旧了一点吧!

字段解释
* mechanism_drivers
An ordered list of networking mechanism driver entrypoints to be loaded from
the neutron.ml2.mechanism_drivers namespace. (list value)

mechanism_drivers 选项指明当前节点可以使用的 mechanism driver，这里可以指定多种 driver，ML2 会负责加载。

* tenant_network_types

[OpenStack —— 网络进阶Linux Bridge(七)](https://blog.51cto.com/wzlinux/1963447)

1、Local
    linux-bridge支持local, flat, vlan和vxlan 四种network type，目前不支持gre。
    要想开启local功能，只需在ML2配置文件type_drivers包含local即可，如：

2、Flat Network
    flat network是不带tag的网络，要求宿主机的物理网卡直接与linux bridge连接，这意味着： 
每个flat network都会独占一个物理网卡。

3、VLAN Network
    vlan network是带tag的网络，是实际应用最广泛的网络类型。 

    因为物理网卡eth1上面可以走多个vlan的数据，那么物理交换机上与eth1相连的的port要设置成trunk模式，而不是access模式。

四、Network Type(VXLAN)
    VXLAN全称Virtual eXtensible Local Area Network，正如名字所描述的，VXLAN提供与VLAN相同的以太网二层服务，但是拥有更强的扩展性和灵活性。

1、与VLAN相比的优点

    持更多的二层网段。 

    VLAN使用12-bit标记VLAN ID，最多支持4094个VLAN，这对于大型云部署会成为瓶颈。VXLAN的 ID （VNI或者VNID）则用24-bit标记，支持16777216个二层网段。

    能更好地利用已有的网络路径。 
    VLAN使用Spanning Tree Protocol(STP)避免环路，这会导致有一半的网络路径被block掉。VXLAN的数据包是封装到UDP通过三层传输和转发的，可以使用所有的路径。

    避免物理交换机MAC表耗尽。 
    由于采用隧道机制，TOR (Top on Rack) 交换机无需在MAC表中记录虚拟机的信息。

## nuetron 扩展列表

TODO: dns啥的都是通过扩展来实现的?

[ssh_10.90.3.33] root@ubuntu-devstack: ~$neutron ext-list
+--------------------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------+
| alias                                | name                                                                                                                                                           |
+--------------------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------+
| address-group                        | Address group                                                                                                                                                  |
| address-scope                        | Address scope                                                                                                                                                  |
| agent                                | agent                                                                                                                                                          |
| allowed-address-pairs                | Allowed Address Pairs                                                                                                                                          |
| auto-allocated-topology              | Auto Allocated Topology Services                                                                                                                               |
| availability_zone                    | Availability Zone                                                                                                                                              |
| default-subnetpools                  | Default Subnetpools                                                                                                                                            |
| dns-integration                      | DNS Integration                                                                                                                                                |
| dns-domain-ports                     | dns_domain for ports                                                                                                                                           |
| dns-integration-domain-keywords      | DNS domain names with keywords allowed                                                                                                                         |
| external-net                         | Neutron external network                                                                                                                                       |
| extra_dhcp_opt                       | Neutron Extra DHCP options                                                                                                                                     |
| extraroute                           | Neutron Extra Route                                                                                                                                            |
| filter-validation                    | Filter parameters validation                                                                                                                                   |
| fip-port-details                     | Floating IP Port Details Extension                                                                                                                             |
| flavors                              | Neutron Service Flavors                                                                                                                                        |
| floatingip-pools                     | Floating IP Pools Extension                                                                                                                                    |
| router                               | Neutron L3 Router                                                                                                                                              |
| ext-gw-mode                          | Neutron L3 Configurable external gateway mode                                                                                                                  |
| multi-provider                       | Multi Provider Network                                                                                                                                         |
| net-mtu                              | Network MTU                                                                                                                                                    |
| net-mtu-writable                     | Network MTU (writable)                                                                                                                                         |
| network_availability_zone            | Network Availability Zone                                                                                                                                      |
| network-ip-availability              | Network IP Availability                                                                                                                                        |
| pagination                           | Pagination support                                                                                                                                             |
| port-device-profile                  | Port device profile                                                                                                                                            |
| port-mac-address-regenerate          | Neutron Port MAC address regenerate                                                                                                                            |
| port-numa-affinity-policy            | Port NUMA affinity policy                                                                                                                                      |
| binding                              | Port Binding                                                                                                                                                   |
| binding-extended                     | Port Bindings Extended                                                                                                                                         |
| port-security                        | Port Security                                                                                                                                                  |
| project-id                           | project_id field enabled                                                                                                                                       |
| provider                             | Provider Network                                                                                                                                               |
| quota-check-limit                    | Quota engine limit check                                                                                                                                       |
| quotas                               | Quota management support                                                                                                                                       |
| quota_details                        | Quota details management support                                                                                                                               |
| rbac-policies                        | RBAC Policies                                                                                                                                                  |
| rbac-address-scope                   | Add address_scope type to RBAC                                                                                                                                 |
| rbac-security-groups                 | Add security_group type to network RBAC                                                                                                                        |
| revision-if-match                    | If-Match constraints based on revision_number                                                                                                                  |
| standard-attr-revisions              | Resource revision numbers                                                                                                                                      |
| router_availability_zone             | Router Availability Zone                                                                                                                                       |
| security-groups-normalized-cidr      | Normalized CIDR field for security group rules                                                                                                                 |
| security-groups-remote-address-group | Remote address group id field for security group rules                                                                                                         |
| security-groups-shared-filtering     | Security group filtering on the shared field                                                                                                                   |
| security-group                       | security-group                                                                                                                                                 |
| service-type                         | Neutron Service Type Management                                                                                                                                |
| sorting                              | Sorting support                                                                                                                                                |
| standard-attr-description            | standard-attr-description                                                                                                                                      |
| stateful-security-group              | Stateful security group                                                                                                                                        |
| subnet-dns-publish-fixed-ip          | Subnet DNS publish fixed IP                                                                                                                                    |
| subnet-service-types                 | Subnet service types                                                                                                                                           |
| subnet_allocation                    | Subnet Allocation                                                                                                                                              |
| standard-attr-tag                    | Tag support for resources with standard attribute: port, subnet, subnetpool, network, security_group, router, floatingip, policy, trunk, network_segment_range |
| standard-attr-timestamp              | Resource timestamps 


## 旧的neutron版本支持vlan隔离啥的?

http://blog.chinaunix.net/uid-20940095-id-4061153.html

ENABLE_TENANT_VLANS

```
# VLAN configuration - LinuxBridge + VLAN模式
Q_PLUGIN=linuxbridge
ENABLE_TENANT_VLANS=True
TENANT_VLAN_RANGE=1920:1930
PHYSICAL_NETWORK=default
LB_PHYSICAL_INTERFACE=eth0

# VLAN configuration - Open VSwitch + VLAN模式  
#ENABLE_TENANT_VLANS=True
#TENANT_VLAN_RANGE=1920:1930
#PHYSICAL_NETWORK=default
#OVS_PHYSICAL_INTERFACE=eth0
```

## devstack neutron组件服务

neutron组件
* devstack@q-ovn-metadata-agent.service
  /usr/local/bin/neutron-server --config-file /etc/neutron/neutron.conf --config-file /etc/neutron/plugins/ml2/ml2_conf.ini
  => 提供neutron api接口9696端口
* devstack@q-svc.service
  /usr/local/bin/neutron-ovn-metadata-agent --config-file /etc/neutron/neutron_ovn_metadata_agent.ini


计算节点服务真少:
```
[ssh_10.90.3.32] root@devstack3: ~$ll /etc/systemd/system/ | grep devstack | awk '{print $9}'
devstack@c-vol.service
devstack@n-cpu.service
devstack@q-ovn-metadata-agent.service
```

## 参考资料

* [《深入理解neutron网络实现.pdf》](https://www.lhsz.xyz/read/openstack_understand_Neutron/dvr-config.md)
  基于Juno版本的吧?
  https://github.com/yeasy/openstack_understand_Neutron

* [第 8 章 为 OpenStack 网络配置物理交换机](https://access.redhat.com/documentation/zh-cn/red_hat_openstack_platform/9/html/networking_guide/sec-physical-switch)
  vlan模式下需要配置物理交换机
