# chrony 时间同步

* ntp
* chrony
* 时间同步

chrony配置文件路径: /etc/chrony.conf

## chrony服务端安装配置

注意开启防火墙允许ntp协议
```
firewall-cmd --add-service=ntp --permanent --reload
```

配置允许指定客户端同步哦
```
allow 10.90.0.0/16
allow 10.20.0.0/16
```

配置允许所有客户端同步
```
allow all
```

KSVD818示例配置
```conf
server 10.90.2.13 iburst maxpoll 5
driftfile /var/lib/chrony/drift
makestep 1.0 -1
rtcsync
allow all
local stratum 9
logdir /var/log/chrony
```

TODO: chrony参数解析

重启服务
```bash
systemctl restart chronyd
```

## chrony客户端安装配置

```conf
server ntp1.aliyun.com iburst
server ntp2.aliyun.com iburst
server ntp3.aliyun.com iburst
server ntp4.aliyun.com iburst
```

查看chrony是否同步成功
```bash
chronyc sources -v
```

## chrony配置解析

## ocp配置时间同步

4.9.15的默认配置如下
```
pool ntp.iefcu.cn iburst
driftfile /var/lib/chrony/drift
makestep 1.0 3
rtcsync
keyfile /etc/chrony.keys
leapsectz right/UTC
logdir /var/log/chrony
```

ocp设置集群节点和pod的时间和时区
TODO:
安装部署集群时，就将节点和容器的默认时区设置为中国？

参考: [OpenShift 4 - 设置集群节点和Pod容器的时间和时区](https://blog.csdn.net/weixin_43902588/article/details/108298517)
修改节点时间同步
其实就是修改节点的/etc/chony.conf配置文件

首先执行如下命令，生成machine config配置
```
CHRONY_HOST=ntp.iefcu.cn

cat << EOF > chroney.conf 
server ntp.iefcu.cn iburst maxpoll 5
driftfile /var/lib/chrony/drift
makestep 1.0 -1
rtcsync
allow all
local stratum 9
logdir /var/log/chrony
EOF

CHRONEY_BASE64=$(base64 -w 0 chroney.conf)
#echo $CHRONEY_BASE64
#c2VydmVyIDEwLjkwLjIuMTkwIGlidXJzdApkcmlmdGZpbGUgL3Zhci9saWIvY2hyb255L2RyaWZ0Cm1ha2VzdGVwIDEuMCAzCnJ0Y3N5bmMKbG9nZGlyIC92YXIvbG9nL2Nocm9ueQpzZXJ2ZXIgMTAuOTAuMi4xOTAgaWJ1cnN0CmRyaWZ0ZmlsZSAvdmFyL2xpYi9jaHJvbnkvZHJpZnQKbWFrZXN0ZXAgMS4wIDMKcnRjc3luYwpsb2dkaXIgL3Zhci9sb2cvY2hyb255Cg==

cat << EOF > ./99_masters-chrony-configuration.yaml
apiVersion: machineconfiguration.openshift.io/v1
kind: MachineConfig
metadata:
  labels:
    machineconfiguration.openshift.io/role: master
  name: masters-chrony-configuration
spec:
  config:
    ignition:
      config: {}
      security:
        tls: {}
      timeouts: {}
      version: 3.1.0
    networkd: {}
    passwd: {}
    storage:
      files:
      - contents:
          source: data:text/plain;charset=utf-8;base64,${CHRONEY_BASE64}
        mode: 420
        overwrite: true
        path: /etc/chrony.conf
  osImageURL: ""
EOF


cat << EOF > ./99_workers-chrony-configuration.yaml
apiVersion: machineconfiguration.openshift.io/v1
kind: MachineConfig
metadata:
  labels:
    machineconfiguration.openshift.io/role: worker
  name: workers-chrony-configuration
spec:
  config:
    ignition:
      config: {}
      security:
        tls: {}
      timeouts: {}
      version: 3.1.0
    networkd: {}
    passwd: {}
    storage:
      files:
      - contents:
          source: data:text/plain;charset=utf-8;base64,${CHRONEY_BASE64}
        mode: 420
        overwrite: true
        path: /etc/chrony.conf
  osImageURL: ""
EOF
```

修改节点时区
其实时区仅仅影响节点的时间显示，略微修改一下就好，不改也没关系
sudo timedatectl set-timezone Asia/Shanghai
# ls -l /etc/localtime
# timedatectl
               Local time: Sun 2020-12-30 07:32:24 UTC
           Universal time: Sun 2020-12-30 07:32:24 UTC
                 RTC time: Sun 2020-12-30 07:32:23
                Time zone: UTC (UTC, +0000)
System clock synchronized: yes
              NTP service: active
          RTC in local TZ: no
          
# timedatectl list-timezones
# sudo timedatectl set-timezone Asia/Shanghai
# timedatectl
               Local time: Sun 2020-12-30 15:35:15 CST
           Universal time: Sun 2020-12-30 07:35:15 UTC
                 RTC time: Sun 2020-12-30 07:35:15
                Time zone: Asia/Shanghai (CST, +0800)
System clock synchronized: yes
              NTP service: active
          RTC in local TZ: no

设置容器时区



