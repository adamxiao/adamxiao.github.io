# ubuntu 20.04使用uniface 816

1. 安装uniface及依赖软件包

```
#apt install -y virt-viewer libusb-dev libpcre2-dev libxcb-xinerama0-dev libqt5widgets5
# dpkg -i ./uniface*.deb
# https://ubuntuqa.com/article/139.html
apt install ./uniface*.deb
```

2. 配置openssl支持低版本tls1.1协议

修改/etc/ssl/openssl.cnf
```
openssl_conf = default_conf
                                                   
[default_conf]                       
ssl_conf = ssl_sect  
     
[ssl_sect]                                          
system_default = system_default_sect
                    
[system_default_sect]
MinProtocol = TLSv1.1                              
CipherString = DEFAULT@SECLEVEL=1
```


3. 从uniface8.1.5中提取libssl.so和libcrypt.so出来用

```
tar -czf /tmp/adam.tgz /usr/lib/ksvd_client/lib/libssl.so.10 /usr/lib/ksvd_client/lib/libcrypto.so.10
```
