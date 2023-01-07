# apt,dpkg使用入门

#### apt list deb files

https://superuser.com/questions/82923/how-to-list-files-of-a-debian-package-without-install

列举已经安装的deb包的文件列表
```
dpkg -L PACKAGENAME
# 或者列举deb包
dpkg -c xxx.deb
```

列举源上的未安装的deb包
```
sudo apt install apt-file
sudo apt-file update        
apt-file list package_name
```
