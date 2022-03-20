# dnsmasq使用入门

## 配置dhcp服务

```
# dhcp白名单机制
dhcp-ignore=tag:!known

# 固定分配ip地址
dhcp-host=52:54:84:00:05:8a,10.90.3.20,bootstrap,set:known
# 或者不固定ip地址
dhcp-host=52:54:84:00:05:8a,set:known

#log-dhcp
# 可以配置多段ip地址分配
dhcp-range=subnet3_20,10.90.3.20,10.90.3.36,255.255.255.0,8h
dhcp-option=subnet3_20,3,10.90.3.1
dhcp-option=subnet3_20,6,10.90.3.38,192.168.168.168
dhcp-option=subnet3_20,option:domain-search,iefcu.cn
```
