# nmcli命令配置网络

参考如下示例, 配置网卡ip,gateway,dns等

```bash
sudo nmcli c delete 'Wired connection 1'
sudo nmcli c add con-name enp3s0 type ethernet ifname enp3s0
sudo nmcli c mod enp3s0 ipv4.addresses 10.90.3.84/24 ipv4.gateway 10.90.3.1 ipv4.method manual
sudo nmcli c mod enp3s0 ipv4.dns 10.90.3.38
sudo nmcli c mod enp3s0 ipv6.method disabled
# confirm /etc/NetworkManager/system-connections/enp3s0.nmconnection
sudo nmcli c up enp3s0
```

#### 新增ip地址（网卡多ip配置）

关键字《nmcli 设置接口多ip》

https://www.linuxidc.com/Linux/2017-07/145573.htm

```
nmcli connection modify test2 +ipv4.addresses 10.10.10.10/8
```

对应nmcli配置文件内容为
```
addresses2=xxx
```