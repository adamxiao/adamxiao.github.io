# 构建本地yum源

关键字《yum repo mirror》

https://docs.oracle.com/en/learn/ol-yum-mirror/index.html#sync-repositories-to-the-local-yum-mirror
Sync Repositories to the Local Yum Mirror
```
sudo dnf reposync --delete --download-metadata -p /u01/yum --repoid ol8_addons
```

https://www.redhat.com/sysadmin/how-mirror-repository
Setting up mirrored repos for Red Hat Enterprise Linux 7

安装工具
```
yum install yum-utils createrepo
```

构建本地yum源
```
yum repolist # 查看repo列表
# reposync --gpgcheck -l --repoid=rhel-7-server-rpms --download_path=/var/www/html  # Sync RPMS
# cd /var/www/html/rhel-7-server-rpms
# createrepo -v /var/www/html/rhel-7-server-rpms  # Create the repo
```

## 构建本地kylin336镜像源

先构建一个createrepo镜像: `docker build -t hub.iefcu.cn/public/kylinos:createrepo .`
```
FROM hub.iefcu.cn/library/kylinos:336
RUN yum makecache && yum install -y yum-utils createrepo
```

直接执行命令缓存
```
docker run -it --rm -v $PWD:/data hub.iefcu.cn/library/kylinos:336 bash
yum makecache && yum install yum-utils createrepo
reposync -l --repoid=base --download_path=/data  # Sync RPMS
```

启动http服务, 提供镜像源服务
```
docker run -d --name repo -v xxx:/usr/share/nginx/html hub.iefcu.cn/public/nginx:stable
```

提供https服务的repo
```
docker run -d --name repo \
  -v xxx:/usr/share/nginx/html \
  -v xxx:/etc/nginx/cert \
  hub.iefcu.cn/public/nginx:stable
```

## 构建本地apt源

https://pendrivelinux.com/how-to-set-up-your-own-debian-linux-mirror/
```
apt-get install apt-mirror apache2
```

编辑mirror配置: /etc/apt/mirror.list
示例配置, 这里使用nexus代理镜像 docker.iefcu.cn 作为上游镜像，只镜像 debian bullseye amd64 架构，不镜像源代码包。
```
set base_path    /data/debian11
set defaultarch  # 默认架构与镜像主机的架构一致,这里是amd64
deb http://docker.iefcu.cn:5565/repository/bullseye-proxy/ bullseye main
```

然后就可以同步apt源了
```
apt-mirror
apt-mirror /etc/apt/mirror.list
```

最后同步的内容在这里
```
ln -sf /var/spool/apt-mirror/mirror/ftp.cn.debian.org/ mirror
```

https://blog.fleeto.us/post/build-ubuntu-repository-with-apt-mirror-and-apt-cacher/
- 存储位置（base_path）
- 下载的线程数（nthreads）
- 需要下载的版本和架构
