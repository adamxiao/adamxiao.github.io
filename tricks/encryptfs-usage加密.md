# ubuntu下加密使用

[ubuntu下文件加密方法](https://blog.csdn.net/weixin_50511931/article/details/108367964)

准备工作
```
安装
sudo apt-get install ecryptfs-utils
创建登录密码和挂载密码
ecryptfs-setup-private
```

挂载加密文件
```
① 用ecrypt挂载文件夹

	mount -t ecryptfs /mnt/tPrivate /mnt/tPrivate
	
	 ps:在挂载过程中会遇到询问提示

         a 首先需要输入挂载密码（不同于登录密码）

         b 然后需要选择密钥计算方式（直接回车为默认）

         c 接着需要输入加密长度（直接回车为默认）

         d 接着需要选择是否允许将未加密文件放入此文件夹中（默认为不允许）

② 把要加密的文件放到/mnt/tPrivate 文件夹中

③ 卸载文件夹

	umount /mnt/tPrivate 
```

[Ecryptfs企业级加密文件系统](https://wiki.ubuntu.org.cn/Ecryptfs%E4%BC%81%E4%B8%9A%E7%BA%A7%E5%8A%A0%E5%AF%86%E6%96%87%E4%BB%B6%E7%B3%BB%E7%BB%9F)

```
sudo mount -t ecryptfs real_path ecryptfs_mounted_path
```

real_path 是真实存放数据的地方；ecryptfs_mounted_path 是指你要把文件夹挂载于哪里（具体位置可以随意）
