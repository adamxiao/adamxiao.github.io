# apt,dpkg使用入门

#### 查询程序属于哪个包

https://askubuntu.com/questions/1212555/what-apt-package-installs-ip-addr-command
```
dpkg -S ip | grep '/sbin/ip$'
```

需要安装apt-file, 上面能用就不用这个了
```
apt-file search --regexp 'bin/ip$'
```

#### apt download deb files

apt download package
```
apt install --download-only xxx
```

#### apt list deb files

https://superuser.com/questions/82923/how-to-list-files-of-a-debian-package-without-install

列举已经安装的deb包的文件列表
```
dpkg -L PACKAGENAME
# 或者列举deb包
dpkg -c xxx.deb
```

列举已安装的软件包
```
apt list --installed
```

列举源上的未安装的deb包
```
sudo apt install apt-file
sudo apt-file update        
apt-file list package_name
```

#### 安装软件

```
dpkg -i *.deb
```
