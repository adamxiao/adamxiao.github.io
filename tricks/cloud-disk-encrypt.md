# 网盘文件加密

目的:
- 本地隐私文件加密之后，再上传到网盘
- 本地隐私文件加密保存

## 加密方式

关键字《加密放网盘脚本》

[个人隐私数据如何加密上传到网盘空间？](https://www.v2ex.com/t/845121)

https://www.privacyguides.org/en/encryption/

- PGP加密
- 7z加密

#### 注意点:

- 把文件夹加密, 把文件名也给加密了
  7z虽然加密，但是里面的文件名都可以提取出来...

#### 7z加密

```
7z a name.7z filename -v10m
# 加密
7z a xxx.7z -p -v100m xxx

7z e data.7z   #不保持目录结构
7z x data2.7z  #保持目录结构
# 分段的只需要指定第一个就行了
```

#### pgp加密

关键字《linux pgp加密用法》

[Linux下使用GPG(GnuPG)加密及解密文件](https://blog.csdn.net/qq_39778226/article/details/90901581)

[2021年，用更现代的方法使用PGP（上）](https://zhuanlan.zhihu.com/p/344198727)

- 生成公钥,私钥对
  私钥设置密码
- 公钥导出, 可以加密文件
- 私钥导出, 可以解密文件
- 另外一种用法, 私钥签名, 公钥验证
  [linux安装包PGP加密验证](https://blog.csdn.net/qpeity/article/details/113773152)

创建密钥
```
gpg --gen-key
gpg --full-generate-key
```
用户名, 和邮件, 以及密钥密码是必填的!

导出导入公钥
```
gpg -a --export adamxiao > adamxiao.pub.asc
gpg --import adamxiao.pub.asc
最后签收公钥, 参考: https://www.cnblogs.com/embedded-linux/p/5903831.html
gpg --sign-key adamxiao
```

导出导入私钥
```
gpg -a --export-secret-keys adamxiao > adamxiao.asc
gpg --import adamxiao.asc
```

列举私钥,公钥
```
gpg --list-secret-keys
gpg --list-key
```

公钥加密文件
```
gpg --encrypt --recipient "adamxiao" xxx
会在同目录下生成xxx.gpg的加密文件
```

私钥解密文件
```
gpg --decrypt xxx.gpg > xxx
注意会提示输入私钥密码
```

卸载私钥,公钥(必须先卸载私钥，然后才可卸载公钥)
```
gpg --delete-secret-keys adamxiao
gpg --delete-keys adamxiao
```

https://blog.bloade.com/2020/12/06/gpg%E5%AF%86%E9%92%A5%E7%9A%84%E7%94%9F%E6%88%90%E5%92%8C%E7%AE%A1%E7%90%86/
如果子密钥被泄露的话，可以只吊销子密钥。这也是为什么要区分主密钥和子密钥的原因，因为一旦主密钥因为泄露被吊销，那么就只能生成全新的主密钥来使用，此前积累的来自其他人的认证也会全部失效。而使用子密钥并离线存放主密钥的话，主密钥泄露的风险会非常低，也就避免了全部密钥失效的情况。

## 加密脚本设计

- 新建一个文件夹
  加密后的文件，以及readme都放其中
- 对加密文件分片(可选)
  超过一定大小(例如2GB)才分片，部分网盘支持文件大小有限
- 生成sha256文件
- 生成metadata文件?
  记录整个文件的sha256

#### 脚本实现

前提条件，目录最好自己先打包
```
tar -cJf xxx.tar.xz xxx
```

计划简单脚本处理, enc-file.sh
```
filename=$1
mkdir -p ${filename}.d
7z a ${filename}.d/${filename}.7z -p -v2000m ${filename}

# 生成md5校验码
(cd ${filename}.d && md5sum * > md5sum.txt)
md5=`md5sum ${filename}`
echo $md5 >> ${filename}.d/org-md5sum.txt
echo $md5 >> md5sum.txt
```

使gpg密钥进行加密, 安全性更高
