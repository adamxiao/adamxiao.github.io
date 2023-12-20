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
