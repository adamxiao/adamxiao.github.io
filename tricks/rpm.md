# rpm使用入门

* rpm常用命令
* 构建rpm包

## 构建hello rpm包

关键字《hello world rpm》

参考: https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/7/html/rpm_packaging_guide/getting-started-with-rpm-packaging
https://rpm-packaging-guide.github.io/#preparing-software-for-packaging

简单通过spec文件, 创建一个hello脚本rpm包
```
Name:       hello-world
Version:    1
Release:    1
Summary:    Most simple RPM package
License:    FIXME

%description
This is my first RPM package, which does nothing.

%prep
# we have no source, so nothing here

%build
cat > hello-world.sh <<EOF
#!/usr/bin/bash
echo Hello world
EOF

%install
mkdir -p %{buildroot}/usr/bin/
install -m 755 hello-world.sh %{buildroot}/usr/bin/hello-world.sh

%files
/usr/bin/hello-world.sh

%changelog
# let's skip this for now
```

#### 源码打包

```bash
mkdir /tmp/kylin-vr-0.1
# 生成源码文件
cd /tmp/
tar -cvzf kylin-vr-0.1.tar.gz kylin-vr-0.1
kylin-vr-0.1/
kylin-vr-0.1/LICENSE
kylin-vr-0.1/kylin-vr.py

mv /tmp/kylin-vr-0.1.tar.gz ~/rpmbuild/SOURCES/
```

## 未整理

列出所有已安装rpm包
rpm -qa

查询一个已经安装的rpm包的文件列表
rpm -ql libvirt

yum search libvirt
哪个软件包提供了
yum provides /usr/sbin/smbd

提取出rpm包中的脚本(写在SPEC文件中的脚本)
rpm -qp --scripts xxx.rpm

解压rpm包的文件
rpm2cpio xxx.rpm | cpio -div

查看包依赖关系
rpm -qpR file.rpm

Linux RPM 命令参数使用详解 查看 rpm包依赖性
https://blog.csdn.net/Deutschester/article/details/6309521

提取rpm包中的spec文件
rpmrebuild --package --notest-install --spec-only=mysql.spec mysql57-community-release-el7-8.noarch.rpm


强制删除rpm包
```
su -c 'yum clean all && rpm --rebuilddb'
su -c 'package-cleanup --problems'
Then run:

su -c 'yum erase zarafa*'
Edit #1: Try running the next command:

su -c 'yum --setopt=tsflags=noscripts remove zarafa*'
If that doesn't work, try this:

su -c 'rpm -e --noscripts zarafa*'
```

编译rpm包
参考资料：
RPM打包原理、示例、详解及备查
https://www.cnblogs.com/jing99/p/9672295.html
```
yum install rpmrebuild rpmdevtools 
yum-builddep SPECS/trafficserver.spec 
spectool -C ./SOURCES -g SPECS/trafficserver.spec 
rpmbuild --define '_topdir %{getenv:PWD}' -ba SPECS/trafficserver.spec
```


#### 修改RPM包

[rpm重新打包](https://blog.csdn.net/itas109/article/details/104226935) => 验证ok
```
yum install -y epel-release
yum install rpm-build rpmrebuild
```

解压rpm包, 重新构建rpm包(中间可以修改spec文件, 和rpm包里面的文件内容)
```
cp /data/KSVD-core-8.1.9-1.server.2.alpha.48894.x86_64.rpm .
# 创建打包目录
rpmrebuild -p ~/KSVD-core-8.1.9-1.server.2.alpha.48894.x86_64.rpm
cd rpmbuild/
# 提取spec文件
rpmrebuild -s ./SPECS/KSVD-core.spec -p ~/KSVD-core-8.1.9-1.server.2.alpha.48894.x86_64.rpm
# 目录名称规则为: Name-Version-Release.BuildArch
mkdir BUILDROOT/KSVD-core-8.1.9-1.server.2.alpha.48894.x86_64
cd BUILDROOT/KSVD-core-8.1.9-1.server.2.alpha.48894.x86_64/
# 提取rpm文件
rpm2cpio ~/KSVD-core-8.1.9-1.server.2.alpha.48894.x86_64.rpm | cpio -div
cd ~/rpmbuild/
# 同时编译二进制和源码rpm包
rpmbuild -ba SPECS/KSVD-core.spec
```

https://itxx00.github.io/blog/2020/04/07/change-rpm-file-using-rpmrebuild/
使用rpmrebuild修改rpm包内容

某些特殊紧急情况下没法等到重新从源码编译打包，手里只有一个打包好的rpm，但是里面内容需要在安装前就改掉，比如修改某个文件内容等，这个时候rpmrebuild命令可以派上用场。 rpmrebuild工作时会把rpm包内容释放到一个临时目录，如果需要修改rpm包里面的文件的话， 可以通过-m参数指定执行的命令，比如/bin/bash，这样就可以得到一个交互式的shell， 有了交互式shell想象空间就很大了，你可以在这个shell环境下对rpm包释放出来的文件任意修改，当退出这个shell时，rpmrebuild会把改动打包回新的rpm。 例如：

```
rpmrebuild -m /bin/bash -np rpm/xxx.rpm 
# 此时我们得到一个交互shell， 
# 比如知道需要修改的文件名为aaa，可以这样操作： find / -name aaa 
# 尽情发挥吧，完了退出 ctrl+D
```

#### rpmbuild 用法

只打上patch
```
rpmbuild -bp ~/rpmbuild/SPECS/*.spec --nodeps
```
