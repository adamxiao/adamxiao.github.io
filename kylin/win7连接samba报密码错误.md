# win7连接samba报密码错误

https://superuser.com/questions/1150911/system-error-86-has-occurred
https://social.technet.microsoft.com/Forums/lync/en-US/64604b25-ae3e-4d5f-8dab-c0294eb088be/system-error-86-while-mapping-c?forum=w7itpronetworking

最终发现改为未定义即可
https://wx.qq.com/cgi-bin/mmwebwx-bin/webwxcheckurl?requrl=https%3A%2F%2Fwww.shuzhiduo.com%2FA%2FGkz1MXPrzR%2F&skey=%40crypt_695e9f41_9b4f725a5a3fbaa192b01d3d187e7b90&deviceid=e184900374714763&pass_ticket=S4tCabGfbp1DTv3bC%252FC%252B3yfeOdBU7FbUM%252BsP%252BeqNgqjPB9pNwkslml2UgCnTfZ6E&opcode=2&scene=1&username=@4af564de9d2cd48eeb9c8afa9f779198

win10 连接samba 账号密码不正确，win7可以访问
- 1、本地安全策略，本地策略-安全选项，需要修改成默认的值的修改方式：
  查找注册表浏览到 HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\LSA
  直接删除 LMCompatibilityLevel 键。确定删除后。
- 2、运行secpol.msc命令。打开本地安全策略。
- 3、查看 网络安全:LAN管理器身份验证级别，安全设置已经变为默认“没有定义”
  修改后发现输入账户密码就可以直接访问了。

#### 允许guest访问

gpedit.msc
打开本地组策略: 计算机配置 -> 管理模板 -> 网络 -> Lanman工作站 -> 启用不安全的来宾登录

https://learn.microsoft.com/zh-cn/troubleshoot/windows-client/networking/cannot-access-shared-folder-file-explorer#you-cant-access-this-shared-folder-because-your-organizations-security-policies-block-unauthenticated-guest-access

#### 无法访问samba服务

其实是无法访问任何samba共享, 包括自身提供的windows共享

原因是`workstation`服务 没有起来，这个服务就是做samba客户端服务用的
=>报错为1068,依赖服务没能起来
```
使用 SMB 协议创建并维护客户端网络与远程服务器之间的连接。如果此服务已停止，这些连接将无法使用。如果此服务已禁用，任何明确依赖它的服务将无法启动。
```

右键属性，看哪些依赖服务起不来！

关键字《0x800704b3 错误》

[windows无法访问局域网共享，0x800704b3报错解决](https://www.sw-tech.cn/html/xyzs/4637.html)
=> 这篇文章说需要开启如下服务..., 最后检查发现`Computer Browser`服务没有起来, 最后发现是`workstation`服务没有起来，依赖KSVD服务!

关键字《windows修改服务依赖关系》
https://blog.csdn.net/z69183787/article/details/8184736
1.使用regedit进入注册表，在\HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Services\ 找到需要设置的服务名。 
2.找到一个多字符串的DependOnService的项，删除。 
3.重启服务即可（我后来是重启服务器才有用的，不知道为何）。

其他问题 - 0x80004005 错误:
https://www.howtogeek.com/810837/how-to-fix-error-code-0x80004005-on-windows-10-and-11/
=> 发现我遇到的是网络问题

还有就是登录凭据问题
- 可在系统的"控制面板\用户帐户\凭据管理器\windows 凭据"中找到
- 可以在"开始菜单->运行"，输入"control userpasswords2" -弹出对话框,切换到"Windows 凭据"选项卡，在"Windows 凭据"這里看到samba的ip或者电脑名称，删除即可。->再注销/重启电脑就能生效了。
