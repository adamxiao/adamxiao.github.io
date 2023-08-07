# qemu qcow2磁盘cache模式

问题:
- 使用cache=none的模式，ubuntu镜像安装npm包后，立即关机，部分js文件内容为0

思路:
- 可能是qemu没有把cache写入到disk就退出了? => 看cache=none的源码，应该是qemu没有写? => 但是这种明显qemu的bug不应该
  为啥qemu不能写完才让guest关机完成?
- 可能是guest系统没有把cache写入到disk就关机了?
  guest系统重启验证就能排除了思路了? => 每次重启后文件内容还是正常的
- 可能是glusterfs分布式存储内容在cache中然后中断了?
  => qemu关机后, 镜像文件没有变化了!

关键字《qemu cache = none丢数据》

[KVM guest caching modes](https://www.cnblogs.com/lunachy/p/5051398.html)

kvm中host和guest各自维护自己的page caches，使得内存中有两份缓存数据。host的缓存为page cache可以理解为读缓存，guest的缓存为disk write cache，可以理解为写缓存，前者优化读性能，后者优化写性能。如果disk write cache开启，那么一旦数据存在disk write cache中，写操作认为已经完成，即使真正的数据尚未在物理磁盘上。因此如果掉电，则存在数据丢失风险，数据完整性得不到保障。除非用户手动指定fsync（同步内存中所有已修改的文件数据到储存设备），或者disk wriet cache中的内容发生了变化，才会把数据写到物理磁盘上。

- 1.writethrough
  qemu-kvm1.2版本下为默认缓存模式，the host page cache is enabled, but the disk write cache is disabled，数据完整性得到保障（不经过写缓存，而是直接写到物理磁盘），读操作性能较好，写操作性能较差。

- 2.writeback
  qemu-kvm1.2版本以上为默认缓存模式，both the host page cache and the disk write cache are enabled，读写操作性能都很优异，唯一的缺点就是写操作的数据掉电可能丢失，无法保证数据完整性。

- 3.none
  the host page cache is disabled, but the disk write cache is enabled. 读操作性能较差，写操作性能较好，同样数据完整性得不到保障。

- 4.unsafe
  Caching mode of unsafe ignores cache transfer operations completely. 应该是guest发出的刷新缓存指令被忽视，意味着以牺牲数据的完整性来换取性能的提升。

- 5.directsync
  两种缓存均关闭，读写操作性能较差。

| cache mode    | host page cache  | disk write cache |
| writethrough  | on               | off              |
| writeback     | on               | on               |
| none          | off              | on               |
| unsafe        | on               | ignore           |
| directsync    | off              | off              |


http://tacy.github.io/post/linux-kvm/

cache指定缓存模式

```
| Mode | host page cache | guest disk write cache | | none | off | on | | writethough | on | off | | writeback | on | on | | unsafe | on | ignored |
```

cache设置涉及到两个层面的影响，一个是宿主机的缓存，一个是guest的缓存：[fn:3]

host page cache打开意味着数据copy到宿主机缓存即完成写操作，通过fsync刷新缓 存，能够从缓存完成读，但是问题在于guest也会缓存同样的数据，也就意味着同样的 数据在内存中保留两份，一般建议如果是本地设备（包括文件和块设备），建议关闭 宿主机缓存。

guest disk write cache打开意味着写操作进入缓存即完成，可能存在数据丢失风险 ，能提高写性能。

一般情况下本地设备建议选择none,性能最佳，如果是远程设备，建议选择writeback 或者writethrough。unsafe一般很少使用，在安装系统的时候使用能加快安装速度， 但是如果进入正式环境使用，需要切换到对应模式。

另外对于磁盘镜像文件模式，还需要考虑块对齐问题，一般保持和宿主机同样的块大 小，分区块对齐，否则可能引发跨块的io操作，影响io性能。


[(好)kvm中对磁盘的io cache](https://www.hanbaoying.com/2017/06/28/iocache.html)
=> 有代码分析

```
int bdrv_parse_cache_flags(const char *mode, int *flags) {
    *flags &= ~BDRV_O_CACHE_MASK;  
    /*
    * - BDRV_O_NOCACHE: host end 绕过 cache
    * - BDRV_O_CACHE_WB: guest 的磁盘设备启用 writeback cache
    * - BDRV_O_NO_FLUSH: 在 host end 永远不要把 cache 里的数据同步到文件里
    * 这几个宏的具体应用后面分析到数据读写的时候会进行分析*/
    * 
     if (!strcmp(mode, "off") || !strcmp(mode, "none")) { 
        *flags |= BDRV_O_NOCACHE | BDRV_O_CACHE_WB; } 
     /* 由上, 这个组合表示的是 host end 不用 Cache, 数据直接在用户空间(QEMU)
      * 和真实设备之间通过 DMA 直接传输, 但是同时, 告诉 guest 模拟的磁盘设备
      * 是有 cache 的, guest 能发起 flush 的操作(fsync/fdatasync) */ 


      else if (!strcmp(mode, "directsync")) { 
      *flags |= BDRV_O_NOCACHE; }
      /* 很好理解, 完全没有 cache, host end 和 guest end 都没有 cache, 
       *guest不会发起 flush 的操作 */ 
      
       else if (!strcmp(mode, "writeback")) {
        *flags |= BDRV_O_CACHE_WB; }           
        /* 和上面相反, host side 和 guest side 都有 cache, 
         * 性能最好, 但是如果host 掉电, 会导致数据的损失 */  
      
      else if (!strcmp(mode, "unsafe")) { 
      *flags |= BDRV_O_CACHE_WB;  
      *flags |= BDRV_O_NO_FLUSH;  }
      /* 见文可知意, 最不安全的模式, guest side 有cache, 
       *但是 host side 不理睬guest 发起的 flush 操作, 完全忽略, 这种情况性能最高, 
       *snapshot 默认使用 的就是这种模式 */  
      
      else if (!strcmp(mode, "writethrough")) { 
      
      /* host end 有 cache, guest 没有 cache, 其实通过后面的代码分析可以知道,
       *这种模式其实是 writeback + flush 的组合, 也就是每次写操作同时触发
       *一个 host flush 的操作, 会带来一定的性能损失, 尤其是非 raw(e.g. qcow2)
       *的网络存储(e.g. ceph), 但是很遗憾, 这是 QEMU 默认的 Cache 模式 */ 
      } 
      else { return -1; }   
      return 0; 
     }
```

https://www.jianshu.com/p/67d87c5d7d38
cache中的none表示直接从硬盘写到disk镜像文件，性能差但是不会丢数据，write-back 模式正好相反


https://www.ctyun.cn/developer/ask/422742111854661
cache=writethrough 来自guest的IO会缓存在宿主机，而且同时写入到后端存储，写性能较差 cache=writeback 来自guest的IO会缓存在宿主机，需要guest根据一定规则定期flush缓存数据持久化到后端存储，否则有数据丢失风险 cache=none 来自guest的IO不会被缓存在宿主机，但是可能缓存在后端盘，适合大量IO场景 cache=directsync 不缓存 cache=unsafe guest的flush请求可能被忽略

[转载：理解 QEMU/KVM 和 Ceph（1）：QEMU-KVM 和 Ceph RBD 的 缓存机制总结](https://vinchin.com/blog/vinchin-technique-share-details.html?id=10281)
kvm cache机制


关键字《qemu cache=none shutdown lost data》

[Virtual machine write cache lost on shutdown (zvol) #5227](https://github.com/openzfs/zfs/issues/5227)
=> 提到文件内容数据为0, 跟我遇到的是一样的!

其他没有什么资料...
