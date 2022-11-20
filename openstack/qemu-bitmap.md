# qcow2 dirty bitmap使用

关键字《persistent bitmap qcow2》

[Dirty Bitmaps and Incremental Backup](https://qemu-project.gitlab.io/qemu/interop/bitmaps.html)

Bitmap Persistence
As outlined in Supported Image Formats, QEMU can persist bitmaps to qcow2 files. Demonstrated in Creation: block-dirty-bitmap-add, passing `persistent: true` to `block-dirty-bitmap-add` will persist that bitmap to disk.

Persistent bitmaps will be automatically loaded into memory upon load, and will be written back to disk upon close. Their usage should be mostly transparent.

However, if QEMU does not get a chance to close the file cleanly, the bitmap will be marked as +inconsistent at next load and considered unsafe to use for any operation. At this point, the only valid operation on such bitmaps is block-dirty-bitmap-remove.

Losing a bitmap in this way does not invalidate any existing backups that have been made from this bitmap, but no further backups will be able to be issued for this chain.

[Qemu-devel PATCH v20 17/30 block: introduce persistent dirty bitmaps](https://patchew.org/QEMU/20170602112158.232757-1-vsementsov@virtuozzo.com/20170602112158.232757-18-vsementsov@virtuozzo.com/)

https://github.com/qemu/qemu/blob/master/block/qcow2-bitmap.c

[Qemu-devel PATCH v10 00/24 qcow2: persistent dirty bitmaps](https://lists.gnu.org/archive/html/qemu-devel/2016-12/msg02981.html)

https://bugzilla.redhat.com/show_bug.cgi?id=1712636
还有关于bitmap的bug...

[PATCH for-4.2? block/qcow2-bitmap: fix crash bug in qcow2_co_remove_persistent_dirty_bitmap](https://lore.kernel.org/all/ec3c0262-2c21-3973-702a-35f3a097e8c2@virtuozzo.com/T/)

[Dirty Bitmaps and Incremental Backup](https://kashyapc.fedorapeople.org/QEMU-Docs/_build/html/docs/interop/bitmaps.html)

#### 验证raw格式磁盘添加bitmap

可以
