# ansible入门

## 概念

https://getansible.com/

#### 什么是Ansible?

Ansilbe是一个部署一群远程主机的工具。远程的主机可以是远程虚拟机或物理机， 也可以是本地主机。

#### Ansible能做什么？

Ansilbe通过SSH协议实现远程节点和管理节点之间的通信。理论上说，只要管理员通过ssh登录到一台远程主机上能做的操作，Ansible都可以做到。

包括：

- 拷贝文件
- 安装软件包
- 启动服务
- …


## 使用场景

[ansible DBA常用场景命令小集](https://blog.csdn.net/Hehuyi_In/article/details/127830430)

- 一、 检查服务器磁盘使用率
- 二、 安装/更新软件包
- 三、 备份原文件，发送新文件
- 四、sql 与 shell 脚本执行

## 安装使用

[非常好的Ansible入门教程（超简单）](https://blog.csdn.net/pushiqiang/article/details/78126063)

### 安装

ubuntu 20.04上安装
```
sudo apt-get install -y ansible
# apt-get安装的ansible版本很低，建议使用pip方式安装
sudo apt install -y python3-pip
sudo pip install ansible
```

### 配置

#### 2.1 管理服务器：Inventory文件

您可以创建一个inventory文件，用于定义将要管理的服务器。这个文件可以命名为任何名字，但我们通常会命名为hosts或者项目的名称。

在hosts文件中，我们可以定义一些要管理的服务器。这里我们将定义我们可能要在“web”标签下管理的两个服务器。标签是任意的。
```
[web]
192.168.22.10
192.168.22.11
```

#### 2.2 基础：运行命令

我们开始对服务器运行任务。ansible会假定你的服务器具有SSH访问权限，通常基于SSH-Key。因为Ansible使用SSH，所以它需要能够SSH连接到服务器。但是，ansible将尝试以正在运行的当前用户身份进行连接。如果我正在运行ansible的用户是ubuntu，它将尝试以ubuntu连接其他服务器。

```
# Run against localhost
$ ansible -i ./hosts --connection=local local -m ping

# Run against remote server
$ ansible -i ./hosts remote -m ping
127.0.0.1 | success >> {
    "changed": false,
    "ping": "pong"
}
```

或者指定密钥?
```
ansible -i ./hosts remote -v -m ping -u root --private-key=~/.ssh/id_rsa
```


#### 2.3 剧本（Playbooks）

Playbook可以运行多个任务，并提供一些更高级的功能。让我们将上述任务移到一本剧本中。在ansible中剧本（playbooks）和角色（roles）都使用Yaml文件定义。

创建文件nginx.yml：
```
---
# hosts could have been "remote" or "all" as well
- hosts: local
  connection: local
  become: yes
  become_user: root
  tasks:
   - name: Install Nginx
     apt:
       name: nginx
       state: installed
       update_cache: true
```

使用一个yaml playbook文件，我们需要使用这个ansible-playbook命令，现在就更容易运行：
```
$ ansible-playbook -i ./hosts nginx.yml

PLAY [local] ******************************************************************

GATHERING FACTS ***************************************************************
ok: [127.0.0.1]

TASK: [Install Nginx] *********************************************************
ok: [127.0.0.1]

PLAY RECAP ********************************************************************
127.0.0.1                  : ok=2    changed=0    unreachable=0    failed=0
```

#### 2.4 角色（roles）

角色很适合组织多个相关任务并封装完成这些任务所需的数据。例如，安装Nginx可能涉及添加软件包存储库，安装软件包和设置配置。
此外，真实的配置通常需要额外的数据，如变量，文件，动态模板等等。这些工具可以与Playbook一起使用，但是我们可以通过将相关任务和数据组织成一个角色（role， 相关的结构）很快就能做得更好。
