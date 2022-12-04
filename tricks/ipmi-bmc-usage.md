# ipmi bmc安装系统

## 华为bmc密码重置

https://support.huawei.com/enterprise/zh/knowledge/EKB1000090882
RH5885V3忘记Bios和bmc密码

- [通过ipmitool工具修改服务器BMC密码](https://support.huawei.com/enterprise/zh/knowledge/EKB1100081447)

我验证的机器型号为: 2288H-V5

思路:
- 通过BIOS配置来修改BMC密码

#### 1. 安装ipmitool工具

```
yum -y install ipmitool
# ubuntu下安装
sudo apt install -y ipmitool
```

#### 2. 显示当前BMC的信息

```
ipmitool lan print 1
```

示例输出
```
Set in Progress         : Set Complete
IP Address Source       : Static Address
IP Address              : x.x.x.x
Subnet Mask             : 255.255.255.0
MAC Address             : xx:xx:xx:xx:xx:xx
SNMP Community String   : TrapAdmin12#$
IP Header               : TTL=0x40 Flags=0x40 Precedence=0x00 TOS=0x10
Default Gateway IP      : x.x.x.x
802.1q VLAN ID          : Disabled
RMCP+ Cipher Suites     : 0,1,2,3,17
Cipher Suite Priv Max   : XuuaXXXXXXXXXXX
                        :     X=Cipher Suite Unused
                        :     c=CALLBACK
                        :     u=USER
                        :     o=OPERATOR
                        :     a=ADMIN
                        :     O=OEM
Bad Password Threshold  : Not Available
```

如果出现未找到impi相关路径, 则需要手动加载内核模块
```
modprobe ipmi_msghandler
modprobe ipmi_devintf
modprobe ipmi_si
```

#### 3. 查看当前BMC中有哪些用户，已经对应的用户ID。

使用ipmi命令查看当前用户及ID，结果如图：
```
ipmitool user list 1
```

#### 4. 修改对应用户的BMC密码。

命令格式为 ipmitool user set password  < userid >

如要修改user ID 为2 的root用户密码为password
```
ipmitool user  set password  2
Password for user 2:
Password for user 2:
IPMI command failed: Unknown (0x95)
Set User Password command failed (user 2)

# 一直提示failed，用同样的方法在另一款机器上设置正常。原因是这台开启了复杂密码验证使能，必须要有特殊字符（该功能可以关闭）
# 使用以下复杂密码就成功了。
ipmitool user set password 2 Test@123
Set User Password command successful (user 2)
```

修改密码

## ipmi新增用户

参考: https://blog.csdn.net/pj_wxyjxy/article/details/119756310

```
1、新增 用户

#ipmitool user set name 3 test

2、设置密码

# ipmitool user set password 3 Test123
IPMI command failed: Invalid data field in request
Set User Password command failed (user 3)

一直提示failed，用同样的方法在另一款机器上设置正常。原因是这台开启了复杂密码验证使能，必须要有特殊字符（该功能可以关闭）

使用以下复杂密码就成功了。
# ipmitool user set password 3 Test@123
Set User Password command successful (user 3)
3、登录bmc web，提示未知错误

还需enable一下用户，就可以正常登录了

#ipmitool user enable 3
```
