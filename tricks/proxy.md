# 代理配置

关键字:
* apt代理
* pip代理
* ...

代理配置
搬一个梯子比较重要...

## 命令使用代理

http代理，socks5代理
```bash
export HTTP_PROXY=http://proxy.iefcu.cn:20172/
export http_proxy=http://proxy.iefcu.cn:20172/
export no_proxy=localhost,127.0.0.0/8,::1,192.0.0.0/8,10.0.0.0/8
export HTTPS_PROXY=http://proxy.iefcu.cn:20172/
export https_proxy=http://proxy.iefcu.cn:20172/
export NO_PROXY=localhost,127.0.0.0/8,::1,192.0.0.0/8,10.0.0.0/8

#export ALL_PROXY=socks5://localhost:port
```

(注意: 不是所有的命令都支持完整的代理参数, 例如image-syncer不支持no_proxy)

devstack安装openstack, 代理配置
```bash
#!/bin/bash

#HTTP_PROXY=http://proxy.iefcu.cn:20172/
#http_proxy=http://proxy.iefcu.cn:20172/
#no_proxy=localhost,127.0.0.0/8,::1
#HTTPS_PROXY=http://proxy.iefcu.cn:20172/
#https_proxy=http://proxy.iefcu.cn:20172/
#NO_PROXY=localhost,127.0.0.0/8,::1

# apt proxy (only root)
if [[ $EUID -eq 0 ]]; then
cat > /etc/apt/apt.conf.d/proxy.conf << EOF
Acquire {
  HTTP::proxy "http://proxy.iefcu.cn:20172";
  HTTPS::proxy "http://proxy.iefcu.cn:20172";
}
EOF
fi

# pip proxy
mkdir -p ~/.pip
cat > ~/.pip/pip.conf << EOF
[global]
proxy=http://proxy.iefcu.cn:20172
EOF

# git proxy
cat > ~/.gitconfig << EOF
[https]
    proxy = http://proxy.iefcu.cn:20172
[http]
    proxy = http://proxy.iefcu.cn:20172
EOF
```


## docker使用代理

关键字`docker pull with proxy settings`
参考: https://www.thegeekdiary.com/how-to-configure-docker-to-use-proxy/
https://docs.docker.com/config/daemon/systemd/
```bash
sudo mkdir -p /etc/systemd/system/docker.service.d
cat > /etc/systemd/system/docker.service.d/http-proxy.conf <<EOF
[Service] Environment="HTTP_PROXY=http://user01:password@10.10.10.10:8080/" Environment="HTTPS_PROXY=https://user01:password@10.10.10.10:8080/" Environment="NO_PROXY= hostname.example.com,172.10.10.10"
EOF
systemctl daemon-reload
systemctl restart docker
systemctl show docker --property Environment 
```

我的配置
```
sudo mkdir -p /etc/systemd/system/docker.service.d
cat <<EOF | sudo tee /etc/systemd/system/docker.service.d/http-proxy.conf
[Service]
Environment="HTTP_PROXY=http://proxy.iefcu.cn:20172"
EOF
```

这个方法,可能适合老版本docker
https://www.thegeekdiary.com/how-to-configure-docker-to-use-proxy/



docker客户端配置传递代理 => 忘了干嘛用的了,先记下来
https://docs.docker.com/network/proxy/#configure-the-docker-client

containerd使用代理
```bash
sudo mkdir -p /etc/systemd/system/containerd.service.d
cat <<EOF | sudo tee /etc/systemd/system/containerd.service.d/http-proxy.conf
[Service]
Environment="HTTP_PROXY=http://proxy.iefcu.cn:20172"
EOF
```



#### maven使用代理

https://stackoverflow.com/questions/1251192/how-do-i-use-maven-through-a-proxy
$HOME/.m2/settings配置文件

```xml
<settings>
  <proxies>
    <proxy>
      <id>genproxy</id>
      <active>true</active>
      <protocol>http</protocol>
      <host>proxyHost</host>
      <port>3128</port>
      <username>username</username>
      <password>password</password>
    </proxy>
 </proxies>
</settings>
```
