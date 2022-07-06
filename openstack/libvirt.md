# libvirt用法

配置ovs桥
```
<interface type='bridge'>
<source bridge='mdvs2'/>
<virtualport type='openvswitch' />
```

测试qemu-ga是否可用
```
# ${DOMAIN}表示虚拟机名字或UUID
virsh qemu-agent-command ${DOMAIN} '{"execute":"guest-ping"}'

#如果返回以下内容则表示qemu-ga可用
{"return":{}}
```

查询qemu-ga支持的命令
```bash
virsh qemu-agent-command ${DOMAIN} '{"execute":"guest-info"}}'
```

qemu-ga写文件
```bash
virsh qemu-agent-command
```

应该会看到支持很多命令，由于接下来做的实验需要用到如下命令，因此请先确认是否均支持

* guest-exec：执行命令（异步操作）
* guest-exec-status：查看执行命令的结果
* guest-file-open：打开文件，获得句柄
* guest-file-write：写文件（传递base64）
* guest-file-close：关闭文件


qemu-ga执行命令


```
virsh qemu-agent-command centos8 --cmd '{"execute":"guest-exec","arguments":{"path":"mkdir","arg":["-p","/root/.ssh"]}}'
{"return":{"pid":9468}}

virsh qemu-agent-command centos8 '{"execute":"guest-exec-status","arguments":{"pid":9905}}'
{"return":{"exitcode":0,"exited":true}}

virsh qemu-agent-command $domain --cmd '{"execute":"guest-exec","arguments":{"path":"touch","arg":["/root/.ssh/adam-test"],"capture-output":true}}'

# 打开文件（以读写方式打开），获得句柄 virsh qemu-agent-command centos8 --cmd '{"execute":"guest-file-open", "arguments":{"path":"/root/.ssh/authorized_keys","mode":"w+"}}'
{"return":1001}
# 写文件，假设上一步返回{"return":1000}，1000就是句柄
virsh qemu-agent-command centos8 --cmd '{"execute":"guest-file-write", "arguments":{"handle":1001,"buf-b64":"xxx"}}'

```

TODO: 句柄泄漏的问题?
写配置文件
```
virsh qemu-agent-command $domain --cmd '{"execute":"guest-file-open", "arguments":{"path":"/usr/local/bin/kylin-vr.yaml","mode":"w"}}'
{"return":1000}
# 写文件，假设上一步返回{"return":1000}，1000就是句柄
virsh qemu-agent-command $domain --cmd '{"execute":"guest-file-write", "arguments":{"handle":1000,"buf-b64":"aGVsbG86IHRydWUK"}}'
{"return":{"count":12,"eof":false}}
# 关闭文件
virsh qemu-agent-command $domain '{"execute":"guest-file-close", "arguments":{"handle":1000}}'
```

测试编写配置文件
```
virsh qemu-agent-command $domain --cmd '{"execute":"guest-file-open", "arguments":{"path":"/etc/kylin-vr/kylin-vr.yaml","mode":"w"}}'
{"return":1000}
# 写文件，假设上一步返回{"return":1000}，1000就是句柄
virsh qemu-agent-command $domain --cmd '{"execute":"guest-file-write", "arguments":{"handle":1000,"buf-b64":"IyAxMC45MC4yLjE4OS0xOTMsIHp5YiAxOTQtMTk2CiMgMTAuOTAuMi4yNTAtMjU0CiMgMTAuOTAuMy4yMC0zNiwgMzctMznlt7LnlKgKaWZfbGlzdDoKICAgLSBpcGFkZHI6IDEwLjkwLjMuMzcKICAgICBwcmVmaXg6IDI0CiAgICAgbWFjOiA1Mjo1NDo4NDowMDowODo0NgogICAgIGdhdGV3YXk6IDEwLjkwLjMuMQogICAtIGlwYWRkcjogMTkyLjE2OC4xMDAuMjU0CiAgICAgcHJlZml4OiAyNAogICAgIG1hYzogNTI6NTQ6ODQ6MTE6MDA6MDQKZWlwX2xpc3Q6CiAgLSBlaXA6IDEwLjkwLjIuMTg5CiAgICB2bS1pcDogMTkyLjE2OC4xMDAuMjAzCiAgLSBlaXA6IDEwLjkwLjIuMjUwCiAgICB2bS1pcDogMTkyLjE2OC4xMDAuMTkwCiAgLSBlaXA6IDEwLjkwLjIuMjUxCiAgICB2bS1pcDogMTkyLjE2OC4xMDAuMTkxCiAgLSBlaXA6IDEwLjkwLjIuMjUyCiAgICB2bS1pcDogMTkyLjE2OC4xMDAuMjAwCiAgLSBlaXA6IDEwLjkwLjIuMjUzCiAgICB2bS1pcDogMTkyLjE2OC4xMDAuMTMKICAtIGVpcDogMTAuOTAuMy4yMQogICAgdm0taXA6IDE5Mi4xNjguMTAwLjMxCiAgLSBlaXA6IDEwLjkwLjMuMjIKICAgIHZtLWlwOiAxOTIuMTY4LjEwMC4zMgogIC0gZWlwOiAxMC45MC4zLjIzCiAgICB2bS1pcDogMTkyLjE2OC4xMDAuMzMKcG9ydF9mb3J3YXJkX2xpc3Q6CiAgLSBlaXA6IDEwLjkwLjIuMjU0CiAgICBwcm90b2NhbDogdGNwCiAgICBwb3J0OiA4MAogICAgZW5kX3BvcnQ6IDgyCiAgICB2bS1wb3J0OiA4MAogICAgdm0taXA6IDE5Mi4xNjguMTAwLjE5MAo="}}'
{"return":{"count":12,"eof":false}}
# 关闭文件
virsh qemu-agent-command $domain '{"execute":"guest-file-close", "arguments":{"handle":1000}}'
```





执行kylin-vr脚本
```
domain=468e4a0e-e647-38b0-6f37-ac7d2cb59585
virsh qemu-agent-command $domain --cmd '{"execute":"guest-exec","arguments":{"path":"python3","arg":["/usr/local/bin/kylin-vr.py", "/usr/local/bin/adam.yaml"]}}'
{"return":{"pid":23453}}

virsh qemu-agent-command $domain '{"execute":"guest-exec-status","arguments":{"pid":23478}}'
```


使用firewalld配置iptables规则?
```
# /etc/firewalld/firewalld.conf
# DefaultZone=trusted

/etc/firewalld/direct.xml
<?xml version="1.0" encoding="utf-8"?>
<direct>
  <rule priority="0" table="filter" ipv="ipv4" chain="INPUT">-i docker0 -j ACCEPT</rule>
</direct>
```

禁用ipv6 《network-scripts disable ipv6》
```
# XXX: 禁用ipv6 <network-scripts disable ipv6>
# https://www.looklinux.com/how-to-disable-ipv6-in-centos-and-redhat/
# /etc/sysctl.conf
```

## FAQ

#### mac地址错误, 添加网卡失败

libvirt: Domain Config error : XML 错误：意外单播 mac 地址，找到多播 '11:11:22:22:33:00'
