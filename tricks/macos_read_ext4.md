# mac os x 系统读写ext4格式的u盘
参考：https://www.cyberciti.biz/faq/mac-os-x-read-ext3-ext4-external-usb-hard-disk-partition/
## 方案概要
1. 安装虚拟机VirtualBox
2. 按照虚拟机系统ubuntu
3. 共享mac系统的usb端口给ubuntu使用
4. ubuntu系统读写ext4格式u盘
5. 通过smb或ftp或其他方式传回数据给mac

## 遇到的坑
1. Mac挂载u盘时，ubuntu识别不到，必须在mac上先卸载掉
