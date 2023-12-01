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
