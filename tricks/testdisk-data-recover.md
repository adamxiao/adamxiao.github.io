# 使用testdisk恢复数据

恢复误删除的文件
testdisk支持ext4文件系统

extundelete 也可以恢复?
```
extundelete /dev/mapper/xxx --restore-file "*DISK1*"
extundelete /dev/mapper/xxx --restore-all
```

https://blog.csdn.net/djhemc/article/details/106727271
ext4 文件分区丢失后（或误删除数据）恢复数据


## FAQ

#### extundelete段错误

关键字《extundelete执行段错误malloc》

https://www.unix.com/fedora/279812-segmentation-fault-while-trying-recover-file-extundelete.html
A segmentation fault core dump is not due to user unfamiliarity. It is a program misbehavior outside the user control. In this case it appears that the extundelete utility has fallen out of maintenance and that it requires a version of e2fsprogs that is too old for up to day system.
Have you given a try to testdisk or Photorec?

https://superuser.com/questions/730614/segmerntation-fault-when-running-extundelete-on-ubuntu-what-to-do
```
apt-get remove extundelete
apt-get install build-essentials e2fslibs-dev
tar -xjf extundelete-VERSION.tar.bz2
cd extundelete
./configure
make
src/extundelete --restore-all image.raw
```
