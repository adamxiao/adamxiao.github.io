# storcli命令处理raid

./storcli64 /c0 show

删除raid0
```
[ssh_10.30.11.126] root@node1: Linux$./storcli64 /c0/v4 del
CLI Version = 007.1705.0000.0000 Mar 31, 2021
Operating system = Linux 4.19.90-2003.4.0.0036.ky3.kb29.ksvd2.aarch64
Controller = 0
Status = Success
Description = Delete VD succeeded
```

查看raid硬盘对应的sda硬盘
```
./storcli64 /c0/v1 show all
[ssh_10.30.11.126] root@node1: Linux$./storcli64 /c0/vall show
CLI Version = 007.1705.0000.0000 Mar 31, 2021
Operating system = Linux 4.19.90-2003.4.0.0036.ky3.kb29.ksvd2.aarch64
Controller = 0
Status = Success
Description = None


Virtual Drives :
==============

-------------------------------------------------------------
DG/VD TYPE  State Access Consist Cache Cac sCC     Size Name
-------------------------------------------------------------
0/1   RAID0 Optl  RW     Yes     RWTD  -   ON  3.637 TB
1/4   RAID0 Optl  RW     Yes     RWTD  -   ON  3.637 TB
-------------------------------------------------------------

VD=Virtual Drive| DG=Drive Group|Rec=Recovery
Cac=CacheCade|OfLn=OffLine|Pdgd=Partially Degraded|Dgrd=Degraded
Optl=Optimal|dflt=Default|RO=Read Only|RW=Read Write|HD=Hidden|TRANS=TransportReady
B=Blocked|Consist=Consistent|R=Read Ahead Always|NR=No Read Ahead|WB=WriteBack
AWB=Always WriteBack|WT=WriteThrough|C=Cached IO|D=Direct IO|sCC=Scheduled
Check Consistency
```

## 查看阵列卡总体信息：

storcli show
看到safe-mode
https://www.cpweb.top/1867


https://sites.google.com/a/cohberg.com/default/home/daily-postings/stoplsiraidcardfromhaltingboot
storcli /c0 set bios Mode=IE

  Only the following combinations are supported
    a) storcli /cx set bios state=<on|off>
    b) storcli /cx set bios Mode=<SOE|PE|IE|SME>
    c) storcli /cx set bios abs=<on|off>
    d) storcli /cx set bios DeviceExposure=<value>

DESCRIPTION: Set bios controller property to on or off.
   Mode - Sets the BIOS Boot mode.

     OPTIONS:
       SOE - Stop on errors
       PE  - Pause on errors
       IE  - Ignore errors
       SME - Safe mode on errors
   abs - Enables|Disables  the auto boot select.

## 其他

https://blog.csdn.net/qq_38028248/article/details/115555971
清除磁盘Foreign状态
使用storcli /c0 /fall import命令清除所有foreign状态
=> 验证都不行！

若无法清除，执行以下命令：
./storcli /c0 /fall del
=> controller is booted to safe mode. 命令不支持
同理下面就是delete
https://halysl.github.io/2020/05/12/storcli%E7%9A%84%E8%BF%9B%E9%98%B6%E4%BD%BF%E7%94%A8/#%E5%AF%BC%E5%85%A5-foreign-configuration


解决safe mode的方法!
https://www.broadcom.com/support/knowledgebase/1211161503828/why-is-megaraid-logging-that-it-is-running-in-safe-mode

Answer
Safe mode is a method of warning the user that the system had errors during the bootup process.
If you are running MegaRAID storage Manager, you should have a dialog box with the events described.

You can disable this feature with megacli:

```
 MegaCli adpBIOS -Enbl|-Dsbl| SOE | BE |
EnblAutoSelectBootLd | DsblAutoSelectBootLd |-Dsply|
-aN|-a0,1,2|-aALL
```

=> 这个服务bios中没有设置raid的地方!!!
https://blog.51cto.com/hsxws/1761250
https://zhuanlan.zhihu.com/p/234489376
以下是将foreign硬盘导入阵列卡的步骤，请在确保数据备份好的时候操作，仅提供参考。
  今天发现DELL 720系统无法启动接上显示器查看RAID是否有问题；
  1.开机启动按“Ctrl+R”进入RAID设置。
  2.进入PD Mgmt中查看故障盘的状态（foreign:外来的，online:正常，missing:磁盘未找到，failed:失败）
  3.如磁盘状态为foreign，在VD Mgmt界面下，将指标移到最上一行按F2，选择foreign config下的Import。
   注意！！！绝对不能使用Clear Config
