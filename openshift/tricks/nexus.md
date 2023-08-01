# nexus安装使用

关键字:
* nexus
* mvn mirror
* npm mirror
* ...

能不能作为apt, pip的仓库mirror?

## 作为npm私有镜像仓库 

参考[使用nexus搭建npm本地私人仓库](https://juejin.cn/post/6911642325559017480)

#### 使用容器部署运行

```bash
mkdir -p nexus-data && chmod 777 nexus-data
# 等待自动生成密码可能需要一点时间!
```

创建docker-compose.yml配置:
```yaml
version: "3.7"
services:
  nexus:
    #image: sonatype/nexus3
    image: hub.iefcu.cn/public/nexus3
    ports:
      - "5565:8081" # 后台访问主端口，同时也是group仓库的访问端口
      - "5567:8082" # 代理仓库端口，即第三方仓库，如taobao
      - "5566:8083" # 私有仓库端口，内部开发上传的仓库，不对外暴露
    restart: always
    container_name: "nexus3" # 容器名称
    volumes:
      - "./nexus-data:/nexus-data" # 将/nexus-data挂载本地的/media/mes/file2/nexus3
    logging:
      driver: json-file
      options:
        max-file: '3'
        max-size: 10m
```

然后点击Sign in进行登录，首次登录时，账号为admin，密码自动生成在./nexus-data/admin.password文件中
cat ./nexus-data/admin.password

可选: 给容器配置代理, 访问国外网络更快！=> 验证中, 没生效?
```yaml
    env_file:
      - adam-proxy.env
```

在 管理配置 -> 系统 -> HTTP, 有http和https代理配置! => 验证中, 亲测有效!

#### 验证使用npm镜像仓库

```
npm config set registry http://docker.iefcu.cn:5565/repository/npm-group/
使用淘宝镜像源
npm config set registry https://registry.npm.taobao.org
```

## 作为ubuntu软件源apt镜像仓库

nexus3有apt插件, 可以配置

关键字`nexus apt mirror`

TODO:
* 1.目前只代理了一个focal镜像源, 很多软件不在这里!

#### 简介

https://help.sonatype.com/repomanager3/nexus-repository-administration/formats/apt-repositories#AptRepositories-Introduction

配置步骤:
* 创建仓库 apt(proxy)
  * name: apt-proxy
  * Distribution: focal
    目前我配置ubuntu 20.04的apt
  * Remote Stroage: https://mirrors.aliyun.com/ubuntu/ 
* 创建仓库 apt(hosted)
* xxx

=> 阿里源有点问题, 还是用这个源吧: http://archive.ubuntu.com/ubuntu/
* 创建仓库 apt(proxy)
  * name: ubuntu-proxy
  * Distribution: focal
    目前我配置ubuntu 20.04的apt
  * Remote Stroage: http://archive.ubuntu.com/ubuntu/ 

用中国的: http://cn.archive.ubuntu.com/ubuntu

#### 使用方法

配置source.list
```
deb http://docker.iefcu.cn:5565/repository/ubuntu-cn-proxy/ focal main restricted
deb http://docker.iefcu.cn:5565/repository/ubuntu-cn-proxy/ focal-updates main restricted

deb http://docker.iefcu.cn:5565/repository/ubuntu-cn-proxy/ focal universe
deb http://docker.iefcu.cn:5565/repository/ubuntu-cn-proxy/ focal-updates universe

deb http://docker.iefcu.cn:5565/repository/ubuntu-cn-proxy/ focal multiverse
deb http://docker.iefcu.cn:5565/repository/ubuntu-cn-proxy/ focal-updates multiverse
```

If you already loaded a metadata using apt update commands first clean it by removing all files from /var/lib/apt/lists/.

To configure the Apt client to work with Nexus Repository Manager edit the file /etc/apt/sources.list. Add the following line if you want to add the repository to the list, or replace the content of the file if you're going to use only your repository:

```
deb <repository URL> <distribution> main
```

For a hosted repository you should use the <distribution> from the repository properties. For a proxy repository, the <distribution> should be the same as in the original remote repository settings.

You can get the <repository URL> from the table in Browsing Repositories and Repository Groups via the UI.

#### 参考资料

[nexus apt repositories](https://help.sonatype.com/repomanager3/nexus-repository-administration/formats/apt-repositories)

## 作为pip软件源镜像仓库

nexus3创建PyPI代理仓库, 最少要配置如下字段:
* 类型: pypi(proxy)
* Define Name - e.g. pypi-proxy
* Define URL for Remote storage. The official Python Package Index Remote Storage URL value to enter is https://pypi.org/.  Using https://pypi.python.org/ should also work as long as redirects are maintained.
  还有其他的一些pypi镜像源:
  * 豆瓣源 http://pypi.douban.com/
    (注意: 不要加simple, 使用的使用加simple, why?)
  * 阿里云 http://mirrors.aliyun.com/pypi/
    目前我使用的!
  * https://pypi.python.org/
    不要用 https://pypi.python.org/pypi 
  * 等等...

> 注意：要在仓库地址后面加/simple, why?

pip更换源, 修改配置文件: ~/.pip/pip.conf (或者/etc/pip.conf)
```conf
[global]
index-url = http://docker.iefcu.cn:5565/repository/aliyun-pypi/simple
trusted-host = docker.iefcu.cn
```

执行脚本自动配置
```bash
mkdir -p $HOME/.pip
cat > $HOME/.pip/pip.conf << EOF
[global]
index-url = http://docker.iefcu.cn:5565/repository/aliyun-pypi/simple
trusted-host = docker.iefcu.cn
EOF
```

或者使用pip命令安装私有mirror仓库
```bash
pip config --user set global.index http://docker.iefcu.cn:5565/repository/aliyun-pypi/
pip config --user set global.index-url http://docker.iefcu.cn:5565/repository/aliyun-pypi/simple
pip config --user set global.trusted-host docker.iefcu.cn
```
注:
* --index-url is used by pip install
* --index is used by pip search

参考 https://pip.pypa.io/en/stable/topics/configuration/


使用容器简单测试pypi源:
```bash
docker run --rm -it \
  hub.iefcu.cn/public/python:3-alpine \
  pip install --trusted-host docker.iefcu.cn \
  -i http://docker.iefcu.cn:5565/repository/aliyun-pypi/simple Flask
```

使用容器简单测试pypi源:
```bash
cat > /tmp/pip.conf << EOF
[global]
index-url = http://docker.iefcu.cn:5565/repository/aliyun-pypi/simple
trusted-host = docker.iefcu.cn
EOF

cat > /tmp/requirements.txt << EOF
Flask!=0.11,>=1.0.2  # BSD
EOF

docker run --rm -it \
  -v /tmp/pip.conf:/root/.pip/pip.conf \
  -v /tmp/requirements.txt:/tmp/requirements.txt \
  hub.iefcu.cn/public/python:3-alpine \
  pip install -r /tmp/requirements.txt

#pip install --upgrade pip
```

#### 参考资料

* [nexus官方pypi文档](https://help.sonatype.com/repomanager3/nexus-repository-administration/formats/pypi-repositories)
* [使用 Nexus 搭建 PyPi 私服及上传](https://codeantenna.com/a/pEuvCwUpR7)

## 以前的零散点

管理界面
http://docker.iefcu.cn:5565 (映射端口8081)

旧版本nexus
```
docker run -d --restart=always -p 8081:8081 --name nexus -v $PWD/data:/sonatype-work hub.iefcu.cn/public/nexus
```

## 参考资料

* [使用nexus搭建npm本地私人仓库](https://juejin.cn/post/6911642325559017480)
* [(好)nexus创建内网apt yum epel pypi](https://blog.csdn.net/hy19930118/article/details/107612525)
