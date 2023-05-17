# ubuntu cloud镜像使用

### 下载镜像

参考openstack中的获取ubuntu镜像
https://docs.openstack.org/image-guide/obtain-images.html

关键字《ubuntu-20.04-server-cloudimg-amd64-disk-kvm.img 不能用》

### 用户密码配置

focal-server-cloudimg-xxx 这些镜像是为云环境创建的, 会配合一个init脚本(或者iso)启动并创建普通用户, 默认root不能登录也没有密码, 而单机运行还是需要root的, 所以在安装前, 要设置一下root口令:
```
virt-customize -a some.qcow2c --root-password password:[your password]
```

### 镜像扩容

ubuntu的cloud镜像没有自动扩容的功能, 需要自己手动扩容?
