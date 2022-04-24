# rsync使用

## 使用Rsync在远程计算机之间同步数据

当使用rsync进行远程传输时，必须将其安装在源计算机和目标计算机上。新版本的rsync被配置为使用SSH作为默认的远程shell。在以下示例中，我们将目录从本地计算机传输到远程计算机：

=> 已验证
```bash
rsync -a /opt/media/ remote_user@remote_host_or_ip:/opt/media/
```

如果您尚未为远程计算机设置无密码SSH登录，则会要求您输入用户密码。

如果要将数据从远程传输到本地计算机，则需要使用远程位置作为源：

```bash
rsync -a remote_user@remote_host_or_ip:/opt/media/ /opt/media/
```

如果远程主机上的SSH正在侦听默认端口22以外的端口，则可以使用-e选项指定端口：

```bash
rsync -a -e "ssh -p 2322" /opt/media/ remote_user@remote_host_or_ip:/opt/media/
```
当传输大量数据或者大文件时，建议在screen，nohup，tmux中运行rsync命令或使用-P选项：

```bash
rsync -a -P remote_user@remote_host_or_ip:/opt/media/ /opt/media/
```



## 参考资料

* [如何使用Rsync进行本地和远程数据传输和同步](https://www.myfreax.com/how-to-use-rsync-for-local-and-remote-data-transfer-and-synchronization/)
