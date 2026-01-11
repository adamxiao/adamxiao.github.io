# adam备份技巧

备份目录有:
* workspaces
* Downloads
* Documents
* ...

```bash
data_dir=/media/adam/nas_data

for dir in Documents Downloads Pictures Music Videos workspaces
do
    if [[ -h $HOME/$dir ]]; then
        echo "link dir $HOME/$dir exist!"
        continue
    fi

    if [[ -d  $HOME/$dir ]]; then
        rmdir $HOME/$dir 2>/dev/null || echo "can't remove dir: $HOME/$dir"
    fi

    if [[ ! -e $HOME/$dir ]]; then
        ln -sf $data_dir/$dir $HOME && echo "link dir $HOME/$dir success!"
    fi
done

#rmdir $HOME/Documents && ln -sf $data_dir/Documents $HOME && echo "Documents link created!"
```

#### tar直接备份系统

关键字《ubuntu 备份》

https://developer.aliyun.com/article/66367

在系统中热备份
```
tar -cvpzf /media/sda7/backup.tgz --exclude=/proc --exclude=/lost+found --exclude=/mnt --exclude=/sys --exclude=/media /
```

使用livecd备份
```
3，创建目录：mkdir /a
4，挂在根目录分区 mount /dev/sdax /a
5，进入a目录 cd /a
6,备份 tar -cvpzf /media/xxx/backup.tgz *
```

Linux 中美妙的事情之一就是在系统正在运行的情况下可以进行还原操作，而不需要启动光盘或者其他任何乱七八糟的东西。当然，如果您的系统已经崩溃，那您必须选择 使用live CD，但是结果还是一样。

#### 恢复系统

[Ubuntu全盘备份与恢复，亲自总结，实测可靠](https://blog.csdn.net/sinat_27554409/article/details/78227496)

[Ubuntu系统备份](https://zhuanlan.zhihu.com/p/51827233)

```
mount 10.90.3.25:/mnt/pool1/nfs /mnt
tar cvpzf /mnt/backup.tgz \
  --exclude=/proc \
  --exclude=/sys \
  --exclude=/run \
  --exclude=/dev \
  --exclude=/tmp \
  --exclude=/swapfile \
  --exclude=/lost+found \
  --exclude=/backup.tgz \
  --exclude=/mnt \
  --exclude=/media \
  --exclude=/data \
  / 2>/mnt/error.log
# 其他有些目录可以单独备份, 例如/home, /data
```

恢复
```
# 使用livecd进入系统, 安装系统, 然后恢复根分区内容
sudo mount 10.90.3.25:/mnt/pool1/nfs /mnt
sudo tar xvpzf backup.tgz -C /target

#修改引导 (或者备份安装好的分区uuid等信息)
$ vi /etc/fstab
```

FIXME: 或者裸恢复，比较麻烦，相当于p2v恢复了

## 备份到云盘

需求:
- 加密
  打散为块
- 挂载为本地盘

https://wgxls.site/posts/rclone-mount-webdav/
=> 后端选择的是WebDAV
```
使用 rclone mount 命令将远程存储挂载到本地。
还有挂载webdav
```

webDAV

alist

rclone

坚果云, 123盘，阿里云

[分享自用webdav免费网盘和自建多套方案](https://linux.do/t/topic/183187)

[照片、影视、笔记、代码…我的个人数据备份同步方式大公开](https://www.youtube.com/watch?v=Oah20xdep0Y)
rclone加密备份
Restic

[Restic笔记](https://www.cnblogs.com/greene/p/18374686)

https://www.escapelife.site/posts/912084a4.html
Restic 是一个免费的，快速，开源，安全和跨平台的备份程序，使用 go 编程语言编写，使用 AES-256 对数据进行加密，并使用 Poly1305-AES 对数据进行身份验证。

Backrest
=> 跟rclone有什么关系?

[把云盘当加密盘用，保护文件隐私的最佳方法！（搭配使用 Rclone 的 Crypt 和 WebDAV）](https://blog.hentioe.dev/posts/rclone-crypt-webdav.html)
=> 选择创建crypt后端`type = crypt`
$HOME/.config/rclone/rclone.conf

rclone是什么?
Rclone 是一个命令行工具，用来管理云上文件。 Rclone 具有强大的云上处理功能，等效于unix 命令rsync、cp、mv、mount、ls、ncdu、tree、rm 和cat，其最初受rsync 的启发并采用Go 编写。

https://www.liueic.com/blog/server-backup
服务器备份 - backrest + rclone + oss

#### rclone备份

发现加密备份时, 文件名太长出错
```
2025/12/25 17:20:21 Failed to sync with 147 errors: last error was: mkdir /data/local/backup1/lfv3d1r7meb0o9tnqk7ievgfi0/hf299nqrbqmedeak0q4o0n096g/m9k4mhv4vepnl518bd377sb0v0/kp6e7gcop5i8b5e235kartcv00/mp2ullbllvm0qv0arppu0ndcrh219snetmpoqgkvdpmemtlp9f72069924ri56fa0ahker2klhjaal58on6k6079vsqd00ufnegn7kb9or38fpimsvp0eds05a85sr40eu1q64v899ufkbtm06oi90na0auo3csvsd69kf094r4mb4cbfp89tstvmdb31jee5a1vjdggcg5um9pmh01gamjb57tln2lfa3agan51tmtlkd4mciqc72b7g4pvgnlf: file name too long
```

$HOME/.config/rclone/rclone.conf
本地加密备份
```
[encrypted-docs]
type = crypt
remote=/data/local/backup1
password = xxx
password2 = xxx2
```

webdav远端
```
[infini]
type = webdav
url = https://rebun.infini-cloud.net/dav/
vendor = other
user = xxx
pass = xxx
```

测试远端
```
rclone ls infini:/
```

#### Backrest备份

[(好)适合全NAS系统的低成本云端加密块备份方案，Backrest（restic）教程分享](https://zhuanlan.zhihu.com/p/1916486493939144033)

为什么要用Backrest
- 第一，大文件无法备份
- 第二，小文件无法备份
- 第三，长路径无法备份

=> 能不能单独解密恢复一个小文件? => 说是可以

#### webDAV网盘

infini-cloud => 日本网盘, 有免费的25G空间
