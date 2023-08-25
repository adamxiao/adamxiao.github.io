# journal日志存储调研

关键字《barrier journal是什么》

[日志型文件系统 - 原理和优化](https://zhuanlan.zhihu.com/p/107558961)
=> 里面有journal, super, meta, checkpoint等概念

https://developer.aliyun.com/article/18103
write barriers 是一种内核机制，用来确保文件系统metadata被正确并有序的写入持久化存储介质，不管底层存储是否有易失CACHE，不管电源是否突然关闭，都可以被确保。

[EXT barrier：一个增强文件系统安全性的机制](https://www.jianshu.com/p/722d4f817c51)
单独使用日志功能不能保证没有任何差错。现在的磁盘大都有大容量的缓存，数据不会立即写入到磁盘中，而是先写入到磁盘缓存中。到这一步，磁盘控制器就能更加高效地将其复制到磁盘中。这对性能来说是有好处的，但是对日志功能来说则相反。为了保证日志百分之百可靠，它必须绝对保证元数据在真实数据写入之前被预先写入。

对于像日志文件系统中**日志这样的数据丢失**，其后果可能是非常严重的。**因为数据的写入和日志的写入存在先后顺序**， 日志记录也存在顺序。**而IO落到磁盘缓存后，操作系统将无法再控制数据的落盘顺序。 **如果数据从磁盘缓存刷入非易失性介质的过程中发生掉电，所有IO的落盘顺序将无法保证。

[日志型文件系统的一点理解](https://cloud.tencent.com/developer/article/1640236)

https://66ring.github.io/2021/03/03/universe/linux/FS/journaled_file_system/
我们会把一个完整的更新操作的步骤(更新inode, bitmap, data block)称为一个 事务(transcation) 。会在transcation开始和结束加上TxB和TxE用于判断transcation是否完整。在transcation完成之后才真正更新磁盘数据，这步称为 checkpoint。


[Journal File Format](https://www.freedesktop.org/wiki/Software/systemd/journal-files/)
```
_packed_ struct Header {
        uint8_t signature[8]; /* "LPKSHHRH" */
        le32_t compatible_flags;
        le32_t incompatible_flags;
        uint8_t state;
        uint8_t reserved[7];
        sd_id128_t file_id;
        sd_id128_t machine_id;
        sd_id128_t boot_id;    /* last writer */
        sd_id128_t seqnum_id;
        le64_t header_size;
        le64_t arena_size;
        le64_t data_hash_table_offset;
        le64_t data_hash_table_size;
        le64_t field_hash_table_offset;
        le64_t field_hash_table_size;
        le64_t tail_object_offset;
        le64_t n_objects;
        le64_t n_entries;
        le64_t tail_entry_seqnum;
        le64_t head_entry_seqnum;
        le64_t entry_array_offset;
        le64_t head_entry_realtime;
        le64_t tail_entry_realtime;
        le64_t tail_entry_monotonic;
        /* Added in 187 */
        le64_t n_data;
        le64_t n_fields;
        /* Added in 189 */
        le64_t n_tags;
        le64_t n_entry_arrays;
};
```

[(好)systemd journal file: Python parsing library](https://formats.kaitai.io/systemd_journal/python.html)


关键字《journal日志存储原理》

关键字《meta super checkpoint journal》

[SOSP|FileSystem|OptFS:Opt Journal](https://zhuanlan.zhihu.com/p/86919946)

pre1：cache
磁盘具有cache，对磁盘读写并不会实时写入硬盘

## 其他

[Journal工作原理](https://www.cnblogs.com/zhaowenzhong/p/5163727.html)

[optuna.storages.JournalStorage](https://optuna.readthedocs.io/en/latest/reference/generated/optuna.storages.JournalStorage.html)

