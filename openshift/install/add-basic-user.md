# 配置基本用户登录

## 1. 配置htpasswd用户

新增admin超级管理员用户
```bash
htpasswd -c -B -b users.htpasswd admin ksvd2020
# 输入内容如下:
admin:$2y$05$oANlQ7bXuJQqbytIFkA7OO5Mf5pROsxoIgVU1UYdQrMTkrl2CNVi6
```

赋予admin用户集群管理员权限
```bash
oc adm policy add-cluster-role-to-user cluster-admin admin
```

删除默认kubeadmin用户
```bash
oc -n kube-system delete secrets kubeadmin
```

新增kylin-monitor用户
```bash
htpasswd -c -B -b users.htpasswd kylin-monitor jit@2021
kylin-monitor:$2y$05$IzGbG9RbAEX577z7RKeVEOl3V0AgfeIoCNq8yDiO9GZ8rnYly5Tlu

oc adm policy add-cluster-role-to-user cluster-monitoring-view kylin-monitor
```

## 2. 在webui上新增这个用户

到管理员，管理，集群设置，配置，OAuth，添加，HTPasswd认证
![](../2022-03-02-10-06-43.png)

**新增monitor用户时，注意名称改为kylin-monitor**

![](../2022-03-02-10-07-30.png)

#### 3. 给这个kylin-monitor用户查看监控的权限

```bash
oc adm policy add-cluster-role-to-user cluster-monitoring-view kylin-monitor
```
