# kolla部署openstack

## Kolla 概述

Kolla是OpenStack下用于自动化部署的一个项目，它基于docker和ansible来实现，其中docker主要负责镜像制作和容器管理，ansible主要负责环境的部署和管理。Kolla实际上分为两部分：Kolla部分提供了生产环境级别的镜像，涵盖了OpenStack用到的各个服务；Kolla-ansible部分提供了自动化的部署。最开始这两部分是在一个项目中的（即Kolla），OpenStack从O开头的版本开始被独立开来，这才有了用于构建所有服务镜像的Kolla项目，以及用于执行自动化部署的Kolla-ansible。

原文链接：https://blog.csdn.net/Skywin88/article/details/123124499

## 基于centos7云镜像, 安装docker，部署openstack

参考: [kolla单节点部署openstack](https://www.cnblogs.com/navysummer/p/14278131.html)

hostnamectl set-hostname kolla

安装各种依赖环境 => 失败, pip不再支持低版本python了
centos7 install python37
```
yum install python-pip
pip install -U pip # => 失败
python -m pip install pip==20.1
yum install python-devel libffi-devel gcc openssl-devel libselinux-python
pip install -U ansible
```


## 其他资料

[kolla一键部署openstack](https://zhuanlan.zhihu.com/p/144742124)
[Kolla部署openstack单节点-train](https://zhuanlan.zhihu.com/p/143029344)
=> 一样的, failed, 但是有参考 价值

- [kolla单节点部署openstack](https://www.cnblogs.com/navysummer/p/14278131.html)
  => failed 关键是kolla-ansible 示例配置文件不对

- [ubuntu20.04LTS单节点kolla部署openstack-train版本](https://blog.csdn.net/Skywin88/article/details/123124499)
  参考官方安装文档: https://docs.openstack.org/project-deploy-guide/kolla-ansible/latest/quickstart.html

https://blog.51cto.com/u_15301988/3085246
NOTE：进行多节点部署，还需要部署 Local Docker Register 服务器，搭建 Docker 私有仓库，详细请浏览：
 https://docs.openstack.org/kolla-ansible/latest/user/multinode.html


https://developer.aliyun.com/article/459561
小试牛刀之Kolla单节点部署

下载Kolla源码
```
git clone https://github.com/openstack/kolla-ansible
# 源码安装kolla-ansible
cd kolla-ansible
pip install .
# 复制相关文件
cp -r etc/kolla /etc/kolla/
cp ansible/inventory/* /root/
```

修改密码
```
# 编辑 /etc/kolla/password
keystone_admin_password: adamxiao
# 生成密码
kolla-genpwd
```

安装openstack
```
kolla-ansible deploy -i /root/all-in-one
```

kolla-ansible虚拟机单节点部署OpenStack
https://blog.csdn.net/qq_16942727/article/details/121081515

## ubuntu 20.04 server安装

参考官方文档: https://docs.openstack.org/project-deploy-guide/kolla-ansible/latest/quickstart.html
安装yoga版本, 参考: https://docs.openstack.org/project-deploy-guide/kolla-ansible/yoga/quickstart.html

虚拟机安装: 双网卡, 8u16G, cpu直通

#### 安装docker

参考官方文档安装
装好之后做成一个模板

#### 安装python3

安装python3等依赖
```
apt install -y git python3-dev libffi-dev gcc libssl-dev

# 自己研究发现, 还需要额外安装的
#pip install docker
apt install -y python3-docker
```

安装pip，安装ansible
```
apt install -y python3-pip
pip install -U pip # 可选吧
pip install 'ansible>=4,<6' # yoga版本
#pip install 'ansible<5.0' # xena版本
pip install --user ansible==4.9.0 # 5.0版本 rabbitmq user问题?
=> 关机后再弄就可以了?
```

#### 安装Kolla-ansible

```
git clone https://github.com/openstack/kolla-ansible -b stable/xena
# 源码安装kolla-ansible
cd kolla-ansible
pip install .
# 复制相关文件
mkdir -p /etc/kolla/
cp -r etc/kolla/* /etc/kolla/
cp ansible/inventory/* /root/
```

修改密码
```
# 编辑 /etc/kolla/password
keystone_admin_password: adamxiao
# 生成密码
kolla-genpwd
```

#### 配置kolla

配置 /etc/kolla/globals.yml
grep  -v  '^$'  /etc/kolla/globals.yml |grep -v '^#'
```
kolla_base_distro: "centos"
kolla_install_type: "source"
kolla_internal_vip_address: "10.0.0.250"
openstack_release: "train"
docker_namespace: "kolla"
network_interface: "ens33" # 浮动ip?
neutron_external_interface: "ens32" # 额外网络平面配置
```

安装openstack
```
kolla-ansible deploy -i /root/all-in-one -vvv
```

zed => 卡在mariadb
yoga => 卡在rabbitmq => 比zed多一些镜像
xena => 卡在rabbitmq => 比zed多一些镜像

#### 构建kolla容器镜像

https://docs.openstack.org/kolla/latest/admin/image-building.html
官方构建方法

```
apt install -y python3-pip
pip install kolla
kolla-build # 默认参数，构建所有镜像
kolla-build nova-libvirt # 单独编译libvirt
```

关键字《kolla镜像本地缓存》

https://www.sdnlab.com/17273.html

```
git clone https://github.com/openstack/kolla.git
cd kolla
# yum install python-devel # centos系列处理
sudo apt install python3-pip
pip install -r requirements.txt -r test-requirements.txt tox
```

以下如果没有特别说明，所有的操作都是在 Kolla 项目的目录里进行
首先要先生成并修改配置文件
```
tox -e genconfig
cp -rv etc/kolla /etc/
```

[使用 Kolla 构建 Pike 版本 OpenStack Docker 镜像](https://my.oschina.net/LastRitter/blog/1788277)

生成 Dockerfile
使用 Pike 版本的默认配置生成 source 类型的 Dockerfile：
```
python tools/build.py -t source --template-only --work-dir=..
```

https://www.cnblogs.com/potato-chip/p/10100667.html
kolla-build镜像时，问题汇总

[管理2000+Docker镜像，Kolla是如何做到的](https://blog.51cto.com/u_9443135/3720391)

[OpenStack Kolla源码分析–Ansible ](https://blog.51cto.com/u_15127593/2749775)

#### 同步kolla docker镜像

[openstack拉取kolla docker镜像到阿里云镜像仓库](https://blog.csdn.net/networken/article/details/106717259)

kolla所有组件的镜像名称在kolla项目中可以找到：
https://github.com/openstack/kolla/tree/master/docker

docker下的目录和二级目录名称跟docker镜像名称相关，所以可以遍历这些目录名称，获取所有目录名称的列表。

kolla镜像格式有一定规则，例如：
```
kolla/centos-source-nova-compute:ussuri
仓库名称/OS版本-包类型-组件名称:openstack版本
```

#### 使用本地docker镜像仓库

[容器化部署OpenStack的正确姿势](https://gist.github.com/baymaxium/6b295d44bc2aa9fce91d237de56e9d57)

编辑 /etc/kolla/globals.yml 配置文件
```
docker_registry: "hub.iefcu.cn"
docker_namespace: "public"
# 最终拉取镜像: hub.iefcu.cn/public/ubuntu-source-haproxy
```

如果部署的是单节点，需要编辑/usr/share/kolla-ansible/ansible/group_vars/all.yml文件，设置enable_haproxy为no。
enable_haproxy: "no"

执行安装OpenStack的命令
kolla-ansible deploy -i /home/all-in-one -vvvv
=> 约花费30min

2）除此外，还有一些小工具，在自己需要时，可以使用。
- kolla-ansible prechecks：在执行部署命令之前，先检查环境是否正确；
- tools/cleanup-containers：可用于从系统中移除部署的容器；
- tools/cleanup-host：可用于移除由于网络变化引发的Docker启动的neutron-agents主机；
- tools/cleanup-images：可用于从本地缓存中移除所有的docker image。

[使用kolla快速部署openstack all-in-one环境](https://cloud.tencent.com/developer/article/1158764)
kolla-build

## FAQ

#### ERROR: kolla_ansible has to be available in the Ansible PYTHONPATH.

https://bugs.launchpad.net/kolla-ansible/+bug/1903923
It's not a bug. Make sure you install both Ansible and Kolla Ansible into the same environment (e.g. both to system, both to user or both to the same venv).

=> 指的就是kolla-ansible安装位置不对?
验证发现之前可能用了其他的python安装的ansible，安装一下即可
```
pip3 install ansible
pip install 'ansible>=4,<6'
=> 不知道有一些什么区别???
```

#### ERROR: Ansible version should be between 2.9 and 2.10. Current version is 2.11.12 which is not supported.

ansible版本不匹配，安装对应的版本

```
kolla-ansible deploy -i /root/all-in-one
ERROR: Ansible version should be between 2.9 and 2.10. Current version is 2.11.12 which is not supported.
```

```
ERROR: Ansible version should be between 2.10 and 2.11. Current version is 2.12.10 which is not supported.
=> pip install --user ansible==4.9.0
Successfully installed ansible-4.9.0 ansible-core-2.11.12
```
=> 查看xena官方文档: https://docs.openstack.org/project-deploy-guide/kolla-ansible/xena/quickstart.html
```
pip install 'ansible<5.0'
```

#### ModuleNotFoundError: No module named 'docker'

https://stackoverflow.com/questions/53941356/failed-to-import-docker-or-docker-py-no-module-named-docker
```
pip install docker
=> 上面不行
apt install -y python3-docker
=> 可以了???
```

#### rabbitmq启动失败: ERROR: epmd error for host openStack: address (cannot connect to host/port)

关键字《kolla deploy disable rabbitmq》
https://bugs.launchpad.net/kolla-ansible/+bug/1855935
[kolla deploy fails due to continuous restart of rabbitmq](https://bugs.launchpad.net/kolla-ansible/+bug/1840369)

修改hosts配置
```
root@kolla2:/home/adam# cat /etc/hosts
127.0.0.1 localhost
10.90.3.22 localhost
10.90.3.22 kolla2
```

#### TASK [service-rabbitmq : nova | Ensure RabbitMQ users exist]

关键字《service-rabbitmq : nova | Ensure RabbitMQ users exist》

https://bugs.launchpad.net/kolla-ansible/+bug/1946506
=> 是bug, 在This issue was fixed in the openstack/kolla-ansible 14.0.0.0rc1 release candidate.
意味着我用的xena版本需要升级

```
failed: [localhost -> localhost] (item=None) => {
    "attempts": 5,
    "censored": "the output has been hidden due to the fact that 'no_log: true' was specified for this result",
    "changed": false
}
fatal: [localhost -> {{ service_rabbitmq_delegate_host }}]: FAILED! => {
    "censored": "the output has been hidden due to the fact that 'no_log: true' was specified for this result",
    "changed": false
}
```

#### TASK [neutron : Copying over ssh key]

尝试ssh-keygen和copy ssh key不行
=> 原来是我使用xena版本的password配置, 没有neutron_ssh_key这个字段

```
The full traceback is:
Traceback (most recent call last):
  File "/usr/local/lib/python3.8/dist-packages/ansible/template/__init__.py", line 1121, in do_template
    res = j2_concat(rf)
  File "<template>", line 12, in root
  File "/usr/local/lib/python3.8/dist-packages/jinja2/runtime.py", line 852, in _fail_with_undefined_error
    raise self._undefined_exception(self._undefined_message)
jinja2.exceptions.UndefinedError: 'neutron_ssh_key' is undefined

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/usr/local/lib/python3.8/dist-packages/ansible/plugins/action/template.py", line 146, in run
    resultant = templar.do_template(template_data, preserve_trailing_newlines=True, escape_backslashes=False)
  File "/usr/local/lib/python3.8/dist-packages/ansible/template/__init__.py", line 1160, in do_template
    raise AnsibleUndefinedVariable(e)
ansible.errors.AnsibleUndefinedVariable: 'neutron_ssh_key' is undefined
fatal: [localhost]: FAILED! => {
    "changed": false,
    "msg": "AnsibleUndefinedVariable: 'neutron_ssh_key' is undefined"
}
```
