# gitlab安装使用

关键字《docker 部署gitlab》

## 安装gogs

更轻量级的git仓库

### docker安使用

关键字《gogs docker-compose 安装》

https://codeantenna.com/a/nQwshmozny

配置docker-compose.yaml
```yaml
version: '2.3'
services:
    mysql:
      #image: mysql:5.7
      image: hub.iefcu.cn/public/mysql:5.7
      restart: always
      environment:
        - MYSQL_ROOT_PASSWORD=root
        - MYSQL_DATABASE=gogs
      volumes:
        - ./data/mysql:/var/lib/mysql
        - ./data/conf:/etc/mysql/conf.d
    gogs:
      #image: gogs/gogs:latest
      image: hub.iefcu.cn/public/gogs:latest
      restart: always
      ports:
        - "22345:22"
        - "3000:3000"
      volumes:
        - ./data/gogs:/data
      links:
        - mysql
      depends_on:
        - mysql
```

参数解析:
* 端口映射
  3000和22端口, 可以映射
* mysql密码修改

起来之后登录http://IP, 然后进行你gogs初始化的设置
* 数据库的地址设置为mysql:3306
* mysql账号密码xxx
* hostname等...

## 安装gitlab

注意gitlab容器里进程比较多, 启动比较慢, 需要耐心等待

https://yxnchen.github.io/technique/Docker%E9%83%A8%E7%BD%B2GitLab%E5%B9%B6%E5%AE%9E%E7%8E%B0%E5%9F%BA%E6%9C%AC%E9%85%8D%E7%BD%AE/#%E6%93%8D%E4%BD%9C%E7%B3%BB%E7%BB%9F
```bash
export GITLAB_HOME=/data/gitlab     # 建立gitlab本地目录
mkdir -p $GITLAB_HOME && cd $GITLAB_HOME

docker run -d \
  --hostname gitlab.iefcu.cn \            # 指定容器域名,创建镜像仓库用
  -p 8443:443 \                           # 容器443端口映射到主机8443端口(https)
  -p 8080:80 \                            # 容器80端口映射到主机8080端口(http)
  -p 2222:22 \                            # 容器22端口映射到主机2222端口(ssh)
  --name gitlab \                         # 容器名称
  --restart always \                      # 容器退出后自动重启
  -v $PWD/config:/etc/gitlab \            # 挂载本地目录到容器配置目录
  -v $PWD/logs:/var/log/gitlab \          # 挂载本地目录到容器日志目录
  -v $PWD/data:/var/opt/gitlab \          # 挂载本地目录到容器数据目录
  hub.iefcu.cn/public/gitlab-ce
```

docker-compose运行gitlab
```yaml
version: '3.6'
services:
  gitlab:
    #image: 'gitlab/gitlab-ce:latest'
    image: 'hub.iefcu.cn/public/gitlab-ce:latest'
    container_name: gitlab
    restart: always
    hostname: 'gitlab.iefcu.cn'
    #environment:
    ports:
      - '80:80'
      - '443:443'
      - '22:22'
    volumes:
      - './config:/etc/gitlab'
      - './logs:/var/log/gitlab'
      - './data:/var/opt/gitlab'
    shm_size: '256m'
```

查看root用户密码:
```bash
sudo docker exec -it gitlab grep 'Password:' /etc/gitlab/initial_root_password
```

## 配置gitlab

可参考官方配置说明文档，本地配置文件在$GITLAB_HOME/config/gitlab.rb

## 注册用户并通过

管理员操作:
在 菜单->管理->概述->用户->待通过, 通过用户的注册请求

### 备份默认配置文件

```bash
$ cd /home/docker/gitlab/config
$ cp gitlab.rb gitlab.rb.default
```

## 参考资料

* [官网 - GitLab Docker images install](https://docs.gitlab.com/ee/install/docker.html)
