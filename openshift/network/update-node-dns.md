# 修改节点dns地址即时生效

## 修改dns地址

临时修改, 修改/etc/resolv.conf
```conf
nameserver 10.90.3.167
```

永久修改，修改nmcli配置文件（注意文件名不同机器可能不一样，修改systemConnectionsMerged目录没用）

/etc/NetworkManager/system-connections/enp3s0.nmconnection
```
dns=10.90.3.167;
```

### 即时生效dns

重启openshift-dns中的dns容器

=> 如何重启，可以修改daemonset环境变量？

## 新增ip地址

```
address2=10.90.3.167/24,10.90.3.1
```