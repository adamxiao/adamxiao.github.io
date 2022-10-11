# libvirt pci总线

https://docs.openeuler.org/zh/docs/22.03_LTS/docs/StratoVirt/%E5%AF%B9%E6%8E%A5libvirt.html

磁盘
元素介绍
* 属性 type ：指定后端存储介质类型，在 StratoVirt 虚拟化中，该值为 file 。
  * 属性 device：呈现给虚拟机的存储介质类型，在 StratoVirt 虚拟化中，该值为 disk 。
* driver：指定后端驱动的详细信息。
  * 属性 type ：磁盘的格式类型，在 StratoVirt 虚拟化中，该值为 raw 。StratoVirt 当前只支持 raw 格式的磁盘。
  * 属性 iothread：为磁盘配置 iothread ，取值为 iothread 编号。在配置磁盘的 iothread 之前，需使用 iothread 元素配置 iothread 的个数。
* source： 指定后端存储介质。
  * 属性 file：指定磁盘路径。
* target：指定后端驱动的详细信息。
  * 属性 dev：指定磁盘名称。
  * 属性 bus：指定磁盘设备的类型，在 StratoVirt 虚拟化中，该值为 virtio 。
* iotune： 指定磁盘 IO 特性。
  * 属性 total_iops_sec：设置磁盘 iops 的值。
* address：用于设置设备所要挂载的总线属性。
  * 属性 type：总线类型，在 StratoVirt 虚拟化中，该值为 pci 。
  * 属性 domain：虚拟机的域。
  * 属性 bus：设备将要挂载的 bus 号。
  * 属性 slot：设备将要挂载的 slot 号，取值范围为：[0, 31] 。
  * 属性 function：设备将要挂载的 function 号，取值范围为：[0, 7] 。

网络设备
元素介绍
* interface：网络接口
  * 属性 type：指定网络设备类型。
* mac：虚拟网卡地址
  * 属性 address：虚拟网卡地址。
* source： 指定后端网桥
  * 属性 bridge：指定网桥。
* target：指定后端网卡
  * 属性 dev：指定后端的 tap 设备。
* model： 虚拟网卡类型
  * 属性 type： 虚拟网卡类型，在 StratoVirt 虚拟化中，该值为 virtio。
* driver：用来指定是否开启 vhost 。
  * 属性 name：如果设置 name 为 qemu 则使用 virtio-net 设备，如果不配置 driver 或者 name 值为 vhost ，则使用 vhost-net 设备。
