# qcow2镜像格式分析

qcow2镜像格式l2 table
https://wenku.baidu.com/view/16254c0c6ddb6f1aff00bed5b9f3f90f76c64d64.html?_wkts_=1721287420499&bdQuery=qcow2%E9%95%9C%E5%83%8F%E6%A0%BC%E5%BC%8Fl2+table&needWelcomeRecommand=1
https://blog.csdn.net/dafukanshijie/article/details/51365369
https://www.docin.com/p-1511575112.html

l1size=round_up(total/cluster_size/l2size, cluster_size)
cluster_size默认为64k 65535
l2size默认为8k 8192
l1size会增大


qcow2 中，磁盘的内容是保存在 cluster 中（每个 cluster 包含一些大小为 512 字节的扇区）。为了找到给定地址所在的 cluster，我们需要查找两张表，L1->L2。L1 表保存一组到 L2 表的偏移量，L2 表保存一组到 cluster 的偏移量；

所以一个地址要根据 cluster_bits（64 位）的设置分成 3 部分，比如说 cluster_bits=12；

低 12 位是一个 4Kb cluster 的偏移（2 的 12 次方=4Kb）；

接下来 9 位是包含 512 个表项目的 L2 表；

剩下 43 位的代表 L1 表偏移量。

为了获取一个给定地址（64 位）的偏移位置：

- 1.从 Head 域中的 l1_table_offset 取得 L1 表的地址
- 2.用前（64-l2_bits-cluster_bits）位地址去索引 L1 表
- 3.在 L1 表中的偏移量获得 L2 表的地址
- 4.用地址中的接下来的 l2_bits 去索引 L2 表，获得一个 64 位的表项
- 5.用 L2 表中的偏移量获得 cluster 的地址
- 6.用地址中剩下的 cluster_bits 位去索引该 cluster，获得该数据块

如果 L1 表和 L2 表中的偏移量都是空，这块区域就尚未被镜像文件分配。

注意 L1 表和 L2 表中的偏移量的前两位被保留，用做表示’copied’ 或’compressed’。

关键字《qcow2 header》
https://www.talisman.org/~erlkonig/misc/qcow-image-format.html
https://chromium.googlesource.com/chromiumos/third_party/qemu/+/tegra-experimental-v3/docs/specs/qcow2.txt
  github.com/qemu/qemu/docs/qcow2.txt.

关键字《qcow refcount table structure》
https://github.com/qemu/qemu/blob/master/docs/qcow2-cache.txt

Near-raw performance, competitive with QED
https://wiki.qemu.org/Features/Qcow3

思路:
- 清空refcount table

```
  typedef struct QCowHeader {
      uint32_t magic; uint32_t version; uint64_t backing_file_offset;
      uint32_t backing_file_size; uint32_t cluster_bits=16, 64k?; uint64_t size; /* in bytes */
      uint32_t crypt_method; uint32_t l1_size; uint64_t l1_table_offset;
      uint64_t refcount_table_offset; uint32_t refcount_table_clusters; uint32_t nb_snapshots;
      uint64_t snapshots_offset;
  } QCowHeader;
```

其他
性能优化
- [Improving disk I/O performance in QEMU 2.5 with the qcow2 L2 cache](https://blogs.igalia.com/berto/2015/12/17/improving-disk-io-performance-in-qemu-2-5-with-the-qcow2-l2-cache/)

```
qemu-img create -f qcow2 -o preallocation=metadata GUEST.IMG 100M
```

问题:
- 非预分配，如何找到一个空闲的cluster写入内容的?
  空闲的cluster, 写入l2表; 写入cluster data; 写入refcount block;
- refblock的机制分析
  就是管理cluster的分配!
- COW原理分析
- 内部快照原理分析
- l1,l2表的二级寻址方法
  这个反而简单
- 镜像trim缩小原理
- 核心点?: l2表加载内存, refblock加载到内存
- 为什么一些USER.IMG的l1_table_offset不是0x30000 ?
  => 说明l1表被复制了一份? 验证发现内容居然一模一样!
  => 也有可能是resize过? => 看日志发现确实是的!! 好像云桌面的USER.IMG都是resize过的!
  => 即便打了快照, l1_table_offset 也没有变化的!
- 压缩是怎么实现的?

分享思考:
- 应用快照
  就是删除当前l1_table相关数据, 以及refcount加一，跟打快照时一样的相关操作

## 分析

关键字《qcow2文件结构》

[(好)Qemu虚拟机QCOW2格式镜像文件的组成部分及关键算法分析](https://blog.csdn.net/superyongzhe/article/details/126439060)

L1表
- [00-08] 保留为0；
- [09-55] 为L2表的偏移地址，如果为0则表明L2表未被分配；
- [56-62] 保留为0；
- [63]    为0则表明未被使用或者是COW，1则表明L2表被正确分配。

L2表
- [00-61] 簇描述符，根据是否加密而不同；
- [62]    未加密则为0，加密则为1；
- [63]    为0则表明未被使用或者是COW，1则表明簇被正确分配。
=> 一个L2表, 8k * 64k => 512MB => 最多512MB数据

refcount表
用于保存cluster的一级分配表，由Header中的“refcount_table_offset”和“refcount_table_clusters”定位。每个表项描述一个“refcount块”的起始地址，为0则表明未被使用，表项大小为64比特。

一个或多个“refcount块”
用于保存cluster的二级级分配表，每个refcount块占用一个cluster。每个表项的大小为refcount_bit（qcow2必须为16），0表明簇未被使用，1表明被使用，大于等于2则表明会被COW。
例如`00 01`?
=> 一个refcount块，32k * 64k(cluster) => 2GB => 最多2GB数据

主要算法

偏移地址计算（从客户机的磁盘设备虚拟偏移地址转换为宿主机的镜像文件中的真实偏移地址）
=> 二维数组定位
```
// 每个cluster包含的L2表个数
l2_entries = (cluster_size / sizeof(uint64_t));
 
// offset在L2中的索引
l2_index = (offset / cluster_size) % l2_entries;
 
// offset所属的L2在L1中的索引
l1_index = (offset / cluster_size) / l2_entries;
 
// 从L1中获取L2的起始地址”并加载到内存
l2_table = load_cluster(l1_table[l1_index]);
 
// 从offset所在的L2中获取所在簇的起始地址
cluster_offset = l2_table[l2_index];
 
// offset在镜像中的真实地址 = 簇起始地址 + 簇内偏移
return cluster_offset + (offset % cluster_size);
```

偏移地址所在簇的refcount获取
=> 也是二维数组定位
=> 问题refcount只记录数据cluster的refcount吗? 以及为什么是16位? => 看代码解决疑惑!
```
// 每个refcount块容纳的refcount表项个数
refcount_block_entries = (cluster_size * 8 / refcount_bits)
 
// offset所在的refcount块索引
refcount_block_index = (offset / cluster_size) % refcount_block_entries
 
// offset所在refcount块在refcount表中索引
refcount_table_index = (offset / cluster_size) / refcount_block_entries
 
// 加载offset所在的refcount块到内存
refcount_block = load_cluster(refcount_table[refcount_table_index]);
 
// 获得offset所在簇的refcount值
return refcount_block[refcount_block_index];
```

[kvm qcow2，raw 磁盘格式、磁盘存储策略介绍](https://cloud.tencent.com/developer/article/2367195)

磁盘分配策略介绍

Vmware 磁盘分配策略

- 1、厚置备延迟置零（zeroed thick）
  以默认的厚格式创建虚拟磁盘。创建过程中为虚拟磁盘分配所需空间。创建时不会擦除物理设备上保留的任何数据，从虚拟机首次执行写操作时会按需要将其置零。立刻分配指定大小的空间，空间内数据暂时不清空，以后按需清空。

- 2、厚置备置零（eager zeroed thick）
  创建支持群集功能（如 FaultTolerance）的厚磁盘。在创建时为虚拟磁盘分配所需的空间。在创建过程中会将物理设备上保留的数据置零。创建这种格式的磁盘所需的时间可能会比创建其他类型的磁盘长。立刻分配指定大小的空间，并将该空间内所有数据清空。

qcow2磁盘分配策略

- off：缺省策略，即不使用预分配策略，采用动态分配磁盘空间的方式，只在需要时分配实际数据所需的空间，稀疏映像类型。
- metadata：分配元数据(metadata)，预分配后的虚拟磁盘仍然属于稀疏映像类型，实际占用的空间比off策略稍大一些
- full：分配文件的块并标识状态为未初始化，即只分配空间,但不置零(不格式化). 预分配后的虚拟磁盘属于非稀疏映像类型，磁盘文件实际占用的空间和分配的空间相同大小
- falloc：分配所有磁盘空间并置零，预分配后的虚拟磁盘属于非稀疏映像类型,在创建时预分配所有空间并将物理设备上保留的数据置零以提高创建速度，虚拟磁盘创建时间较长。


[qcow2原理详解](https://royhunter.github.io/2016/06/28/qcow2/)
- refcount	Qcow2内部用于管理cluster的分配而维护的引用计数
- refcount table	用于查找refcount的第一级表
- refcount block	用于查找refcount的第二级表

Qcow2维护refcount用以管理image中cluster的分配和释放，refcount作用等同于引用计数，代表了指定的cluster的使用状态：
- 0： 表示空闲
- 1： 表示已使用
- 大于等于2：表示已使用并且写访问必须执行COW操作

给定一个相对于img file的offset可以通过下面计算关系得到refcount：
=> 注意: 不是raw镜像的offset

=> 有一点源码分析
qcow2_alloc_clusters

qcow2_snapshot_create:

- 制造一个snapshot id；
- 分配snapshot header空间，填充信息；
- 分配l1表的空间，并从当前的image的l1表中copy；
- 将snapshot的l1表写入image file；
- 操作所有cluster的refcount，主要是l2表和data block的cluster；
- 增加refcount，并置cluster的状态的copied位；表明这些cluster在写操作是需执行COW;
- 将snapshot header写入image file；

https://sq.sf.163.com/blog/article/218146701477384192
=> 写ppt可以参考一点

https://www.cnblogs.com/kvm-qemu/articles/14017061.html
=> 有书本讲了qcow2镜像的读写

内部快照原理
- 执行快照的时候，给已经分配的每一个cluster的refcount加一, 删除则减一
  refcount 大于一表示有快照引用它
- XXX

## 源码分析

https://github.com/zhangyoujia/qcow2-dump/blob/master/test/qcow2_layout(preallocation).png

qcow2_alloc_cluster_offset
qcow2_alloc_cluster_link_l2

## 内部快照原理

了解COW原理!
- backing file这种外部快照也是COW的应用!
- 内部快照COW的原理

[qcow2原理详解](https://royhunter.github.io/2016/06/28/qcow2/)

qcow2_snapshot_create:

- 制造一个snapshot id；
- 分配snapshot header空间，填充信息；
- 分配l1表的空间，并从当前的image的l1表中copy；
  => 验证是有!
- 将snapshot的l1表写入image file；
- 操作所有cluster的refcount，主要是l2表和data block的cluster；
  => 验证是有! 给已经分配的每一个cluster的refcount加一, 删除则减一
  (refcount 大于一表示有快照引用它)
- 增加refcount，并置cluster的状态的copied位；表明这些cluster在写操作是需执行COW;
- 将snapshot header写入image file；

#### 实验验证

创建镜像
```
qemu-img create -f qcow2 test.img 100G
```

模拟写数据, 可以看出没有metadata预分配，l2表和数据cluster是混合没有规律的
```
qemu-nbd -c /dev/nbd0 test.img
dd if=/dev/random bs=512 count=1 of=/dev/nbd0
dd if=/dev/random bs=64k count=1 seek=1 of=/dev/nbd0
dd if=/dev/random bs=64k count=1 seek=2 of=/dev/nbd0
dd if=/dev/random bs=64k count=1 seek=10000 of=/dev/nbd0
dd if=/dev/random bs=64k count=1 seek=100000 of=/dev/nbd0
qemu-nbd -d /dev/nbd0
```

qemu-img snapshot -c snap1 test.img

## 其他资料

kvm-forum-2017-slides.pdf
=> cache-clean-interval? l2-cache-size=8M

kvm-forum-2020-slides.pdf
=> 讲了高版本qemu5.2支持subcluster实现，读写性能更高一点儿!
