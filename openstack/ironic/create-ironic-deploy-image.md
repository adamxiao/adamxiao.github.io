# 创建ironic部署镜像

关键字《ironic-python-agent write-image》

[Creating an OpenStack Ironic deploy image with Buildroot](https://blog.christophersmart.com/articles/creating-an-openstack-ironic-deploy-image-with-buildroot/)
=> 可以创建一个很小的部署镜像, 只有几十MB?

关键字《Creating an OpenStack Ironic deploy image》

[Creating instance images](https://docs.openstack.org/ironic/latest/user/creating-images.html)

[Building or downloading a deploy ramdisk image](https://docs.openstack.org/ironic/latest/install/deploy-ramdisk.html)


[Building Ironic Images](https://www.cloudnull.io/2016/11/openstack-ironic-images-and-flavors/)

## 旧的资料

https://github.com/openstack/diskimage-builder.git : diskimage_builder/elements/debootstrap/README.rst
DIB_DEBIAN_USE_DEBOOTSTRAP_CACHE => 干嘛用的?

```
export DIB_IMAGE_CACHE=$HOME/.cache/image-create
export DIB_OFFLINE=1

https://www.cnblogs.com/dream397/p/13259269.html
export DIB_LOCAL_IMAGE=/data/adam
block-device-efi -a arm64
```

#### 基于centos9制作部署镜像

验证成功，可能需要网络支持，否则总是网络中断

参考官方的构建参数
```
DIB_RELEASE=9-stream
DIB_REPOREF_requirements=HEAD
DIB_REPOREF_ironic_python_agent=HEAD
DIB_ARGS=-o ipa-centos9-stable-zed ironic-python-agent-ramdisk centos dynamic-login -x
ELEMENTS_PATH=/usr/local/share/ironic-python-agent-builder/dib
DIB_PYTHON_EXEC=/usr/bin/python3
DIB_DHCP_TIMEOUT=60
DIB_INSTALLTYPE_pip_and_virtualenv=package

disk-image-create -a arm64 -o ipa-centos9-stable-zed-arm64 ironic-python-agent-ramdisk centos dynamic-login -x
```

#### 制作ironic-python-agent镜像

[官方文档 - diskimage-builder images](https://docs.openstack.org/ironic-python-agent-builder/latest/admin/dib.html)

ubuntu 20.04处理
```
export ELEMENTS_PATH=/usr/local/share/ironic-python-agent-builder/dib

cat > sources.list.debian << EOF
deb http://docker.iefcu.cn:5565/repository/bullseye-proxy/ bullseye main
deb http://docker.iefcu.cn:5565/repository/bullseye-proxy/ bullseye-updates main
EOF

export DIB_RELEASE=bullseye
#export DIB_APT_SOURCES="$(pwd)/sources.list.debian"
export DIB_DISTRIBUTION_MIRROR=http://docker.iefcu.cn:5565/repository/bullseye-proxy/
export DIB_DISTRIBUTION_MIRROR=http://mirrors.aliyun.com/debian/

https://docs.openstack.org/diskimage-builder/1.22.1/developer/caches.html
--offline
export DIB_OFFLINE=1

export DIB_DEV_USER_USERNAME=ipa
export DIB_DEV_USER_PWDLESS_SUDO=yes
export DIB_DEV_USER_PASSWORD='123'
disk-image-create -o ironic-python-agent \
  debian ironic-python-agent-ramdisk devuser
```

https://docs.openstack.org/ironic-python-agent/queens/install/index.html
[真官方文档 - Installing Ironic Python Agent](https://docs.openstack.org/ironic-python-agent/yoga/install/index.html)
=> ipa镜像解释，最官方了...
下载tinyipa使用
```
wget https://tarballs.opendev.org/openstack/ironic-python-agent/tinyipa/files/tinyipa-stable-yoga.gz
wget https://tarballs.opendev.org/openstack/ironic-python-agent/tinyipa/files/tinyipa-stable-yoga.vmlinuz
```

