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
