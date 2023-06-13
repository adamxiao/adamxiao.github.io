# openshift创建虚拟机入门

## 创建虚拟机

### web控制台创建

在 项目 -> 计算 -> 实例中，点击创建实例
* 名称: test1
* 源: 选择基础镜像
* 实例类型: 选择虚拟机规格, 1核1G 等
* 网络: 比较重要, 待深入研究
* 其他可选参数暂不处理

### openstack命令行创建

https://posts.careerengine.us/p/5dd4b21fb1bc2b756d694c16
```
openstack server create --flavor m1.tiny --image cirros --nic net-id=f7e02e069858447397c5e980c55c4f94 --security-group bc02ec6c-370b-4f16-92cb-4c65d0b272ff --key-name key wellqin01

# 其中flavor类型模板，image镜像，选的是cirros镜像， net-id是网络id，-security-group后面是指定的安全组id，--key-name是创建的秘钥对名称key，wellqin01是实例名称

openstack image create --disk-format qcow2 --container-format bare --public \
            --property os_type=linux --file ./cirros-0.3.4-x86_64-disk.img cirros
```

检查实例的状态和登录实例:
openstack server list

## 其他资料

查看nova节点服务等
```bash
root@ubuntu-devstack:~# nova service-list
+--------------------------------------+----------------+-----------------+----------+---------+-------+----------------------------+-----------------+-------------+
| Id                                   | Binary         | Host            | Zone     | Status  | State | Updated_at                 | Disabled Reason | Forced down |
+--------------------------------------+----------------+-----------------+----------+---------+-------+----------------------------+-----------------+-------------+
| b831255b-c2c0-460b-93af-1b2a2ed006e2 | nova-scheduler | ubuntu-devstack | internal | enabled | up    | 2022-05-12T07:38:14.000000 | -               | False       |
| f4ae1ba9-87c9-45c8-bc57-39546108f3e2 | nova-conductor | ubuntu-devstack | internal | enabled | up    | 2022-05-12T07:38:09.000000 | -               | False       |
| 16d06789-d274-4bbe-8902-77d3a896c43a | nova-conductor | ubuntu-devstack | internal | enabled | up    | 2022-05-12T07:38:12.000000 | -               | False       |
| 8b249a46-eab3-4726-9b59-3ef8208051e6 | nova-compute   | ubuntu-devstack | nova     | enabled | up    | 2022-05-12T07:38:08.000000 | -               | False       |
| bf283acb-2f3e-4c67-b83c-81e52118e4dc | nova-compute   | devstack3       | nova     | enabled | up    | 2022-05-12T07:38:15.000000 | -               | False       |
+--------------------------------------+----------------+-----------------+----------+---------+-------+----------------------------+-----------------+-------------+
```

## FAQ

### Host 'devstack3' is not mapped to any cell

错误： 实例 "test3" 执行所请求操作失败，实例处于错误状态。: 请稍后再试 [错误: Host 'devstack3' is not mapped to any cell]. 

解决方案：
controller端输入以下命令：
```bash
nova-manage cell_v2 discover_hosts --verbose

Found 2 cell mappings.
Skipping cell0 since it does not contain hosts.
Getting computes from cell 'cell1': fdbe5ef1-2fbd-4cc3-95fb-3f301ea99afb
Checking host mapping for compute host 'devstack3': af0bd5b2-991b-41e8-99af-ba40f5cec41f
Creating host mapping for compute host 'devstack3': af0bd5b2-991b-41e8-99af-ba40f5cec41f
Found 1 unmapped computes in cell: fdbe5ef1-2fbd-4cc3-95fb-3f301ea99afb

root@ubuntu-devstack:~# nova-manage cell_v2 discover_hosts --verbose
Found 2 cell mappings.
Skipping cell0 since it does not contain hosts.
Getting computes from cell 'cell1': fdbe5ef1-2fbd-4cc3-95fb-3f301ea99afb
Checking host mapping for compute host 'ubuntu-devstack3': 855e226c-0230-4598-85d3-9ccfaf946aef
Creating host mapping for compute host 'ubuntu-devstack3': 855e226c-0230-4598-85d3-9ccfaf946aef
Found 1 unmapped computes in cell: fdbe5ef1-2fbd-4cc3-95fb-3f301ea99afb
```

## 参考资料
