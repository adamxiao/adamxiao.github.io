# nmap使用

## 根据ip地址探测操作系统

[Nmap参考指南(Man Page) / 操作系统探测](https://nmap.org/man/zh/man-os-detection.html)

Nmap最著名的功能之一是用TCP/IP协议栈fingerprinting进行远程操作系统探测。 Nmap发送一系列TCP和UDP报文到远程主机，检查响应中的每一个比特。 在进行一打测试如TCP ISN采样，TCP选项支持和排序，IPID采样，和初始窗口大小检查之后， Nmap把结果和数据库nmap-os-fingerprints中超过 1500个已知的操作系统的fingerprints进行比较，如果有匹配，就打印出操作系统的详细信息。 每个fingerprint包括一个自由格式的关于OS的描述文本， 和一个分类信息，它提供供应商名称(如Sun)，下面的操作系统(如Solaris)，OS版本(如10)， 和设备类型(通用设备，路由器，switch，游戏控制台， 等)。

https://blog.csdn.net/u010164190/article/details/125660109

```
0.首先搜索在192.168.1.xxx网段中存活的主机
# nmap -sn -PE -n 192.168.1.0/24
 
注意：
-PE：nmap就只发送一个ICMP echo请求
```

根据ip推测为什么操作系统
```
1.根据ip推测为什么操作系统
# sudo nmap -O --osscan-guess --osscan-limit 192.168.1.5
 
Starting Nmap 7.60 ( https://nmap.org ) at 2020-05-07 15:23 CST
Nmap scan report for test (192.168.1.5)
Host is up (0.000021s latency).
Not shown: 996 closed ports
PORT    STATE SERVICE
22/tcp  open  ssh
111/tcp open  rpcbind
139/tcp open  netbios-ssn
445/tcp open  microsoft-ds
Device type: general purpose
Running: Linux 2.6.X
OS CPE: cpe:/o:linux:linux_kernel:2.6.32
OS details: Linux 2.6.32
Network Distance: 0 hops
 
OS detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 3.98 seconds
 
 
注释：
-o ： 启用os检测
--osscan-limit： 将os检测限制为可能的目标
--osscan-guess ： 推测操作系统检测结果
```

#### 扫描端口

https://wiki.wgpsec.org/knowledge/tools/nmap.html
```
nmap 192.168.0.8
nmap -p 1-65535 192.168.0.8		# -p选项，只扫描指定的端口
```

https://blog.csdn.net/av11566/article/details/125598176
```
nmap -sV -sT -Pn --open -p0-65535 -iL test.txt -oX test.xml
```

nmap -p 80 192.168.0.1-10
