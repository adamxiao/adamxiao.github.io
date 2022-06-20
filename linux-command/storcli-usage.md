# storcli命令处理raid

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
