# openstack 备份

问题:
- 现在最关键的就是Freezer-scheduler 没有调度任务执行?
  而且没有日志? => 开启scheduler的调试日志
  => 手动运行freezer-agent执行备份动作!!!

- cinder-backup怎么实现增量备份的?
  我对实例打快照，2次，第二次备份，也没有提示为增量备份?
  => 后台命令可以增量备份, web页面没有选项...
  metadata有数据:  "parent_id": "dba97c81-9ebb-45ec-a60d-1366c8c2be35",
  增量备份确实小的多! 只记录差异的chunk(32K)
  增量链如下: A -> B -> C (根据parent-id)

- cinder-backup删除全量或者中间的增量会怎么样?
  => 页面提示无法删除! 有增量备份的全量备份不能删除, 有依赖的也不能删除

- cinder-bakcup可以合并增量到全量备份为一个新的备份吗?
  需要吗，能吗? 看命令行帮助是没有 => 查资料也没有
  能不能基于备份创建新的备份? => 暂无

nova有一个备份接口, 但是不支持卷后端的实例
/servers/{server_id}/action
Create Server Back Up (createBackup Action)

问题是备份到哪里，备份为glance镜像? => 看源码确实是的! 最后还给打了一个快照...
```
        if compute_utils.is_volume_backed_instance(context, instance):
            LOG.info("It's not supported to backup volume backed "
                     "instance.", instance=instance)
            raise exception.InvalidRequest(
                _('Backup is not supported for volume-backed instances.'))
        else:
            image_meta = compute_utils.create_image(
                context, instance, name, 'backup', self.image_api,
                extra_properties=props_copy)
```

示例参数如下:
```
{
    "createBackup": {
        "name": "Backup 1",
        "backup_type": "daily",
        "rotation": 1
    }
}
```

[14 Backup and Restore](https://documentation.suse.com/hpe-helion/8/html/hpe-helion-openstack-clm-all/bura-overview.html)
freezer job-create -C client_node_1 --file job-backup.conf

[(好)freezer备份恢复](https://zhuanlan.zhihu.com/p/31597476)

[(好)Openstack 之 备份组件Freezer 原创](https://blog.51cto.com/yuweibing/2122111)

接下来是对Nova进行备份，可以通过web界面进行备份，备份步骤如下：

- 1、创建Action。登录web管理界面，Disaster Restore ->Backup and Restore->动作->Create Action ，填写相关的参数，其中，action选择backup，mode选择nova，storage选择swift（在我的环境中部署的是ceph rgw组件，具有对象存储功能），Container Name or Path 填写对象存储的Container名称比如Novabackup，填写Nova Instance ID ，Network ID可以不填，其中日志可以指定，如果不指定，日志默认在容器freezer_api中/root/.freezer/freezer.log 文件中，也可以在Advance中指定；

- 2、创建Job。登录web管理界面，Disaster Restore ->Backup and Restore->Job->Create Job ，填写开始时间、结束时间，注意Clients需要选择，动作需要选择上面创建的动作，其中动作需要拖动，刚开始总是点击没有反应，后面才发现需要拖动；而且开始时间、结束时间感觉没有用，我填写了一个下午2点多开始，第二天下午2点结束的的时间，后面查看日志，发现是晚上10点20开始执行，执行时间2分多钟，感觉很诡异。

- 3、创建sessions。登录web管理界面，Disaster Restore ->Backup and Restore->Sessions->Create Session ,Session的概念是可以将多个job放在一起，但真不知道有什么作用。创建session的时候和创建Job的时候一样，也有开始时间、间隔、结束时间，这里我没有填写。

- 4、在Job中启动。web管理界面，Disaster Restore ->Backup and Restore->Job->选中job“动作”的下拉框，attach to session ，然后点start。

#### freezer命令行备份

https://blog.51cto.com/yuweibing/2122111

```
docker exec -it  freezer_api bash
```

vi /etc/freezer-openrc.sh
```
export OS_PROJECT_DOMAIN_NAME=default
export OS_USER_DOMAIN_NAME=default
export OS_PROJECT_NAME=admin
export OS_TENANT_NAME=admin
export OS_USERNAME=admin
export OS_PASSWORD=adamxiao
export OS_AUTH_URL=http://10.90.4.100:5000/v3 # 注，容器外部环境的端口值是35357
export OS_INTERFACE=internal
export OS_IDENTITY_API_VERSION=3
```

1、备份命令：
=> 关键是下面这个container
```
freezer-agent --mode nova --nova-inst-id 4ad2e0fd-02ba-414e-acae-5f79e267ea96 --container Novabackup --backup-name bk_nova_1
```

**创建备份action**
```
freezer action-create [-h] --file FILE
```

**创建备份job**
https://documentation.suse.com/hpe-helion/8/html/hpe-helion-openstack-clm-all/bura-overview.html#id45789

创建配置文件 job-backup1.conf
```
{
  "job_actions": [
    {
      "freezer_action": {
        "action": "backup",
        "mode": "nova",
        "backup_name": "backup1",
        "path_to_backup": "/tmp",
        "container": "tmp_backups"
      },
      "max_retries": 3,
      "max_retries_interval": 60
    }
  ],
  "job_schedule": {
    "schedule_interval": "24 hours"
  },
  "description": "backup for tmp dir"
}
```
问题: 备份哪一个nova实例?
相关参数解析:
- mode
  备份模式, 可以是nova, cinder等?

然后创建job => 发现居然创建了一个action, 但是存储是swift
```
freezer job-create -C CLIENT-ID --file FREEZER-FILE
freezer job-create -C CLIENT-ID --file job-backup1.conf
```

=> 查看freezer-api, scheduler没有日志? start, stop也没有。。。

#### freezer-agent独立运行测试

[](https://www.sohu.com/a/122932971_468741)
以备份cinder为例。
将cinder备份到本地文件系统的/home/cinder-backup目录下，命令如下：
```
freezer-agent --cinder-vol-id 8a748800-b51a-482b-969c-f67ada815283 --storage local --container /home/cinder-backup --mode cinder
```

备份流程：

- 1）创建cinder client实例
- 2）通过cinder client获取cinder卷实例cinder_volume
- 3）创建cinder_volume的快照cinder_snapshot
- 4）从快照cinder_snapshot复制出cinder卷cinder_volume2
- 5） 从cinder_volume2创建glance image
- 6）下载glance image
- 7）将此image上传到备份目录/home/cinder-backup下
- 8） 清理现场

其中第6)步获取到的是一个可迭代的stream对象，所以并不是一次性把整个image都下载下来，而是在第7)步边下载边上传，下载/上传的数据块大小是可以自定义的。

[freezer | 基础介绍及使用](https://www.sohu.com/a/199872304_468741)

备份虚机
```
freezer-agent --mode nova --no-incremental true \
  --nova-inst-id 3693a9f1-0ef7-4591-99ef-badbaa62e3eb \
  --backup-name nova_backup --engine nova
```

备份卷
```
freezer-agent --mode cindernative \
  --cindernative-vol-id c385d607-fdd6-40b3-b972-d7f7cc49198a \
  --backup-name cinder_backup
```

问chatgpt: freezer-agent备份nova实例到本地目录

创建备份配置文件: my_backup_config.conf
```
[freezer-agent]
backup_name = my_instance_backup
backup_host = my_nova_host
backup_auth_url = https://my_keystone_host:5000/v3/
backup_username = my_user
backup_password = my_password
backup_project_name = my_project
backup_container = my_backup_container
backup_mode = level-0

[nova]
always_level_0 = True
```

运行freezer-agent命令进行备份
```
freezer-agent --config-file my_backup_config.conf --backup-path /tmp/backup --nova-instance my_instance
=> 报错，参数名不对, 我修正了一下, 但是还是报错...
freezer-agent --config-file ./freezer-agent.conf --path-to-backup /tmp/backup --nova-inst-id 77d7e5f3-d140-43fd-b7b6-933f85c858fc
```

#### openstack实例备份方案

[OpenStack云环境数据备份方案解析](https://www.vinchin.com/blog/vinchin-technique-share-details.html?id=8060)

为什么要引入Freezer
对于很多用户来说，OpenStack 环境中的数据备份一直存在着众多痛点，影响了OpenStack备份，具体包括如下几个方面：

- 1.Nova Cinder 备份方式存在不统一性
  OpenStack 数据备份过程中，我们的主要关注点在Nova 和Cinder中。
  Nova备份方式，一贯做法是将该虚拟机进行快照处理。
  Cinder的Volume备份目前主要有两种方式

  - 1） 对Volume制作快照，形成Volume快照链备份数据
  - 2） 对Volume使用Cinder-backup 的方式进行备份，针对不同的后端使用不同的备份Driver

  如果我们在OpenStack的使用过程中，既要备份云主机又要备份云硬盘就需要在Nova 和Cinder上分别进行备份，无法使其由一种中间的方式来管理所有的备份

- 2.备份数据不方便统一的管理
  备份的数据存储比较独立，Nova Instance一般存放于Glance中，而Cinder Volume 一般存放备份数据，由不同的Driver存于不同的存储中

- 3.无法进行有效的周期性备份
  目前在OpenStack的云环境数据备份中，还无法对备份动作进行有效的周期性的自动化备份

- 4.没有好的备份链管理
  没有好的备份链管理，无法对备份数据进行整理

- 5.对旧备份的删除不智能
  对旧备份的删除能力，云硬盘的备份一般由手工判断等方式，进行清理，即不方便也不智能
 
综上所述，OpenStack环境数据备份中急需一套好的备份方案, 而Freezer在解决上述问题中也有比较好的表现，所以我们引入了Freezer

目前Freezer支持的数据备份有下面这些：
- OpenStack Nova instance(nova): 对OpenStack 云主机进行备份
- OpenStack Cinder volume(Cinder or Cindernative): 对OpenStack 云硬盘进行备份
- ...等

说明: 目前Freezer 对云硬盘的备份主要有两种方式
- 1） Freezer自主的一套对云硬盘的备份机制(Cinder)
- 2） Freezer 编排Cinder Backup 的方式进行备份(Cindernative)

Freezer的特性介绍
- 备份数据多存储支持
  支持nfs, ssh, swift
- 备份数据的上传带宽限速
- 数据一致性校验
- 周期全量/增量备份支持
- 备份数据的压缩加密
- 备份链整理

[对Openstack平台上虚拟机及平台本身备份需要注意什么？推荐使用什么备份软件？](https://www.talkwithtrend.com/Question/435725)

关于Karbo：Karbo其实是一个标准的备份服务编排框架，通过此框架可以真正做到备份服务化。但目前更多的只是框架，针对不同的应用、数据类型的备份目前还需要持续补齐。

openstack可以用第三方的进行备份，由于openstack是半成品，有很多第三方公司对其开发了备份工具，比如# Freezer，其实手动备份也是可以的，但备份不太好管理。

关键字《openstack karbor 安装使用》
karbor源码 => karbor资料非常少呢, 而且下载源码，发现只有rocky等版本, 没有最新版本
```
git clone https://git.openstack.org/openstack/karbor
```
看源码，应该是这个备份nova实例
karbor/services/protection/protection_plugins/server/nova_protection_plugin.py: ProtectOperation: on_main
=> 没有看懂是怎么备份cinder卷的...

karbor/services/protection/protection_plugins/volume/cinder_protection_plugin.py: ProtectOperation: _create_backup
=> 看看怎么备份cinder卷的, 就是调用cinder命令去备份

[OpenStack Train版本新特性大全及快速安装|万字长文](https://posts.careerengine.us/p/5e0d341f36cd9f65d96a0ecc)
https://wiki.openstack.org/wiki/Karbor

[OpenStack Karbor介绍](https://www.jianshu.com/p/f43de1ccb2b7)

[openstack中 虚拟机实例的备份 与 恢复](https://blog.csdn.net/weiyuanke/article/details/7639742)
我们需要备份如下的文件：
- （1）console.log
- （2）disk
- （3）disk.local
- （4）libvirt.xml
- （5）/opt/stack/nova/instances/_base/ephemeral_0_40_None
- （6）/opt/stack/nova/instances/_base/5dcb736a3fbb7f5b92657095aa77a877f4039ec0_10

[NetBackup™ for OpenStack 管理指南](https://www.veritas.com/content/support/zh_CN/doc/137724260-153515852-1)

[4年！我对OpenStack运维架构的总结](https://www.cnblogs.com/lirunzhou/p/9678301.html)
在一个由OpenStack+Ceph架构组成的云平台环境中，有N种数据备份方案。如OpenStack有自带的Karbor、Freezer云服务，Ceph也有相关的备份方案，也有其他商业的备份方案等。实际上，OpenStack云平台本身也提供了一些较好易用的备份功能，比如虚拟机快照/备份、数据卷快照/备份，在使用时也倡导通过将数据卷挂载给虚拟机，从而将数据写入到云盘中，间接的实现数据容灾备份。

关于Ceph的底层存储备份方案，可以使用RBD Mirroring方案。
RBD Mirroring是Ceph新的异步备份功能。支持配置两个Ceph Cluster之间的rbd同步。

#### freezer备份原理

问chatgpt得到如下答案:

Freezer备份是一种基于快照的备份技术，它使用快照来冻结要备份的文件系统，从而保证备份的一致性和完整性。具体原理如下：

- 创建快照：在备份之前，Freezer会先创建一个文件系统快照，这个快照是一个只读的文件系统镜像，它记录了要备份的文件系统在备份开始时的状态。
- 冻结文件系统：创建快照后，Freezer会冻结要备份的文件系统，确保在备份期间没有文件被修改或删除。这样可以保证备份的一致性。
- 备份数据：一旦文件系统被冻结，Freezer就可以开始备份数据了。它会将快照中的数据复制到备份介质中，这个备份介质可以是硬盘、网络存储或者云存储等。
- 解冻文件系统：当备份完成后，Freezer会解冻文件系统，恢复文件系统的正常运行状态。解冻文件系统后，它将可以继续使用，而备份的数据也可以被恢复到任何一个时间点。

总之，Freezer备份通过创建快照和冻结文件系统的方式来保证备份数据的一致性和完整性，这样可以确保备份的可靠性。


关键字《openstack freezer备份源码分析》
=> 没啥资料!

自己看源码(grep nova):
- freezer/engine/nova/nova.py: NovaEngine: backup_data
  => 看源码也是先通过nova接口创建一个实例快照!
```
        image_id = self.nova.servers.create_image(
            server,
            "snapshot_of_{0}".format(backup_resource)
        )
```
  以及创建临时镜像，临时卷, 临时卷快照等, 处理完成后会删除掉!

#### freezer增量备份原理

freezer支持nova实例增量备份吗
=> chatgpt说支持: nova-incremental备份依赖于QEMU guest agent和Libvirt驱动程序，这些驱动程序允许备份系统在运行的实例上进行增量备份。

看freezer源码: 不支持nova/glance实例级别的增量备份?
=> 难道cinder支持增量备份?
=> 问chatgpt: freezer支持实例增量备份吗 => 说支持...
- freezer/job.py: BackupJob
```
    def _validate(self):
        elif self.conf.mode == 'nova':
            if not self.conf.no_incremental:
                raise ValueError("Incremental nova backup is not supported")

            if not self.conf.nova_inst_id and not self.conf.project_id \
                    and not self.conf.nova_inst_name:
                raise ValueError("nova-inst-id or project-id or nova-inst-name"
                                 " argument must be provided")
        elif self.conf.mode == 'glance':
            if not self.conf.no_incremental:
                raise ValueError("Incremental glance backup is not supported")

            if not self.conf.glance_image_id and not self.conf.project_id \
                    and not self.conf.glance_image_name \
                    and not self.conf.glance_image_name_filter:
                raise ValueError("glance-image-id or project-id or"
                                 " glance-image-name or "
                                 " glance-image-name_filter "
                                 "argument must be provided")

        elif self.conf.mode == 'cinder':
            if not self.conf.cinder_vol_id and not self.conf.cinder_vol_name:
                raise ValueError("cinder-vol-id or cinder-vol-name argument "
                                 "must be provided")

        elif self.conf.mode == "cindernative":
            if not self.conf.cindernative_vol_id:
                raise ValueError("cindernative-vol-id"
                                 " argument must be provided")
        else:
            pass
```

#### freezer概念

[freezer | 基础介绍及使用](https://www.sohu.com/a/199872304_468741)

Freezer API：

提供RESTful API，通过这些API维护备份相关的元数据，如client、job、action、backup和session等。
元数据保存于Elasticsearch数据库中；与Freezer Scheduler交互并存储和提供相关的元数据。

- client：运行freezer agent/freezer scheduler的主机。
- action：freezer执行的一次备份、恢复或者删除等动作。
  => 为啥页面能够创建action? 但是不运行?
- backup：备份的相关信息。
- job：在client上执行的一个或者多个 actions，包含了scheduling信息。
- session：共享同样的scheduling时间的一组jobs，用于跨节点同步备份。

Freezer Agent：

负责执行 备份，恢复，删除等任务，可以单独执行也可以接受Freezer Scheduler的调度。支持的job如下：
- BackupJob
  - nova instance
  - cinder
  - 等等
- RestoreJob
  数据恢复，支持指定时间点的恢复，对应的action为restore。
- AdminJob
  管理job，对备份数据的管理，删除旧的备份任务，支持指定时间段的删除，对应的action为admin，--remove-from-date 时间要大于备份的时间。
- ExecJob
  执行命令或脚本，不能被调度。对应的action为exec，需要指定command参数。
- InfoJob
  获取存储介质中的容器名，大小，对象数等信息，对应的action为info。

备份虚机
```
freezer-agent --mode nova --no-incremental true \
  --nova-inst-id 194026b4-5ec3-409e-aa2c-298227ef581c \
  --backup-name nova_backup --engine nova
```

备份卷
```
freezer-agent --mode cindernative \
  --cindernative-vol-id 545f2b02-8ef5-4393-a3bb-6ed142acbcc5 \
  --backup-name cinder_backup
```

Freezer命令

freezer命令行创建非调度任务
```
freezer job-create --file /opt/json/test.json \
  --client 6939853cb6d041febce023634940c396_ubuntudbs
```

job配置
```
{
  "job_actions": [
    {
      "freezer_action": {
        "action": "backup",
        "mode": "nova",
        "nova_inst_id": "77d7e5f3-d140-43fd-b7b6-933f85c858fc",
        "backup_name": "nova-backup1",
        "path_to_backup": "/tmp",
        "engine_name": "nova",
        "container": "tmp_backups"
      },
      "max_retries": 3,
      "max_retries_interval": 60
    }
  ],
  "description": "oneshot backup job for tmp dir"
}
```

https://blog.csdn.net/weixin_34320724/article/details/92138426
这里freezer备份云硬盘实际上是调用了cinder-backup来实现的。

使用curl测试api（freezer api使用keystone v2）
```
# 获取cinder所有的backups，纯属测试
curl -s -H "X-Auth-Token: fced5d5ae9e84009b3dca7972d7c5131"\ 
        -X GET\
        -H "Content-type: application/json"\ 
        http://192.168.141.6:8776/v2/b232965aeb9c4b3a883ce41b16394e3f/backups | python -m json.tool
```

#### cinder-backup增量备份原理？

准备手动验证一下增量备份

关键字《cinder-backup 增量备份合并到全量备份中》

[Openstack 中cinder backup三种backend的对比](https://www.vinchin.com/blog/vinchin-technique-share-details.html?id=8170)

一、基于Chunk的backend
1.2增量备份
增量备份实现思路很简单，对一个volume进行增量备份时，会读取前一次备份（全量或增量）的sha256file，备份时会将每Sha_block_size数据SHA计算的结果与上次备份的值比较，如果相同，就只保存计算结果，如果不同就会将对应的Sha_block进行备份。连续SHA计算结果不同的Sha_block会保存成同一个文件。其中metadata中会注明每个文件的大小以及在原始volume中的偏移量。

由以上描述可以知道，sha256file是实现增量备份的关键。这个文件记录了原始卷每个Sha_block_size数据的SHA值，每次增量备份时，将新的SHA值和上次备份记录的值进行比较，只需要备份SHA值不同的数据。另外，我么也可以知道，增量备份之间是有依赖的，新创建的备份会依赖于上一次的备份，多次增量备份会形成一个依赖链，在这里我们可以称之为备份链。在给volume创建增量备份时，总是会基于这个volume最新备份去创建。每次创建一个全量备份，都意味着增加一个备份链。

[Cinder磁盘备份原理与实践](https://www.51cto.com/article/537194.html)
注意：
volume和backup都使用ceph后端存储时，每次都会尝试使用增量备份，无论用户是否传递incremental参数值。

有图
https://www.cnblogs.com/gzxbkk/p/7794626.html
https://www.cnblogs.com/liufarui/p/13225433.html

#### 配置等元数据备份

除了需要备份虚拟机的卷数据，还需要备份虚拟机的其他配置元数据, 猜测有如下:
=> 理论上跟打快照为镜像的原理一致吧?

- 网卡列表
- cpu
- 内存
- 虚拟机元数据
  例如启动镜像的属性列表?

#### openstack freezer入门使用

问chatgpt得到:

看不懂
```
freezer-agent --config-file /etc/freezer/freezer.conf backup
```

freezer创建一个实例备份

页面上有几个页面点击就报错: 任务, sessions

页面上可以创建一个备份action:
- 模式: nova
- 存储: 本地路径: /tmp/xxx
- nova实例uuid: xxx

提示: 成功：action已成功排队，将很快执行。

=> 感觉没有啥用: action id: 01fe6945af6745a6a2c2b9e1abd6087d

freezer-scheduler.log, 可能是这个原因导致? => 没有freezer-agent服务运行
```
2023-04-04 01:06:20.661 7 INFO freezer.scheduler.daemon [-] freezer daemon starting, pid: 7
2023-04-04 01:06:20.667 7 ERROR freezer.scheduler.freezer_scheduler [-] Unable to get jobs: [*] Error 503: <html><body><h1>503 Service Unavailable</h1>
No server is available to handle this request.
</body></html>
: freezerclient.exceptions.ApiClientException: [*] Error 503: <html><body><h1>503 Service Unavailable</h1>
```

freezer 命令行help
```
Commands:
  action-create  Create an action from a file
  action-delete  Delete an action from the api
  action-list  List all actions for your user
  action-show  Show a single action
  action-update  Update an action from a file
  backup-create  Create an backup from a file
  backup-delete  Delete a backup from the api
  backup-list  List all backups for your user
  backup-show  Show the metadata of a single backup
  client-delete  Delete a client from the api
  client-list  List of clients registered in the api
  client-register  Register a new client
  client-show  Show a single client
  complete  print bash completion command (cliff)
  help  print detailed help for another command (cliff)
  job-abort  Abort a running job
  job-create  Create a new job from a file
  job-delete  Delete a job from the api
  job-get  Download a job as a json file
  job-list  List all the jobs for your user
  job-show  Show a single job
  job-start  Send a start signal for a job
  job-stop  Send a stop signal for a job
  job-update  Update a job from a file
  session-add-job  Add a job to a session
  session-create  Create a session from a file
  session-delete  Delete a session
  session-list  List all the sessions for your user
  session-remove-job  Remove a job from a session
  session-show  Show a single session
  session-start  Start a session
  session-update  Update a session from a file
```

[OpenStack云环境数据备份方案 Freezer](https://blog.csdn.net/hxpjava1/article/details/86801980)
Freezer主要有四个组件， Freezer-Agent、Freezer-Scheduler、Freezer-Web-Ui、 Freezer-Api。
- Freezer-Agent: 主要用于真正执行备份、还原等动作的组件。

源码:
https://github.com/openstack/freezer

官方文档:
https://docs.openstack.org/freezer/latest/

[从数据删除看备份的重要性](https://xuchao918.github.io/2018/05/23/%E2%94%A4%E2%95%99%E2%95%A9%C2%A4%E2%95%9B%E2%96%8C%E2%95%94%E2%95%9B%E2%94%82%C2%A4%E2%94%90%E2%94%A4%E2%96%92%E2%95%95%E2%95%96%E2%96%8C%E2%95%A1%E2%94%80%E2%95%93%E2%95%AA%E2%95%A5%D0%BA%E2%95%A8%E2%95%98/)
=> ceph存储的备份几种方案


https://blog.csdn.net/dylloveyou/article/details/77430786

2.2.1 分块备份策略

那恢复的时候怎么重组呢？这就需要保存元数据信息，元数据信息包括：

- ● Backup信息:其实就是数据库中的信息，或者说就是一个Backup object实例的序列化，包括backup name、description、volume_id等。
- ● Volume信息:数据卷信息，即volume实例的序列化，包括size、name等。
- ● 块信息：即objects信息，这是最重要的数据，记录了每一个块的长度、偏移量、压缩算法、md5值，备份恢复时主要通过这些块信息拼接而成。
- ● 版本：序列化和持久化必不可少的参数，决定升级后能否保证老版本的备份数据能否成功恢复。

## FAQ

#### Critical Error: Endpoint for object-store not found - have you specified a region?

手动执行freezer-agent报错
```
freezer-agent --mode cindernative \
  --cindernative-vol-id c385d607-fdd6-40b3-b972-d7f7cc49198a \
  --backup-name cinder_backup
Critical Error: Endpoint for object-store not found - have you specified a region?
```

问chatgpt说是要配置swift对象存储, 配置之后确实没了。

#### Critical Error: ('Engine error. Failed to backup.', {})

=> 修改wb模式为w模式解决了!

我看freezer依赖python>=3.8， 我的版本是3.8也有问题!!!

关键字《TypeError: a bytes-like object is required, not 'str'》
https://www.hellocodeclub.com/how-to-fix-typeerror-a-bytes-like-object-is-required-not-str
=> 以纯文本文件打开即可

https://bobbyhadz.com/blog/python-typeerror-bytes-like-object-is-required-not-str
=> 可以`f.write(my_json.encode('utf-8'))`, 试试?
=> 可以: `f.writelines([my_json.encode('utf-8')])`, writelines略有不一样
The str.encode method returns an encoded version of the string as a bytes object. The default encoding is utf-8.

估计是swift的问题。。。 => 不是
使用kolla和devstack部署的都一样，未解决

我在devstack中把这个语法改掉, 居然没报这个错了!!! 报其他的错误，基于实例创建镜像500错误... glanceclient.exc.HTTPOverLimit
修改: freezer/engine/nova/nova.py
```
    fb.writelines(json.dumps(metadata))
改为
    fuck = json.dumps(metadata)
    fb.writelines(fuck)
```

原来报错在这里:
```
  File "/opt/stack/freezer/freezer/engine/nova/nova.py", line 358, in set_tenant_meta
    fb.writelines(fuck)
```

```
(freezer-scheduler)[freezer@ubuntu init-run]$ freezer-agent --mode nova --no-incremental true \
>   --nova-inst-id 3693a9f1-0ef7-4591-99ef-badbaa62e3eb \
>   --backup-name nova_backup --engine nova
/var/lib/kolla/venv/lib/python3.8/site-packages/novaclient/client.py:234: UserWarning: The 'interface' argument is deprecated in Ocata and its use may result in errors in future releases. As 'endpoint_type' is provided, the 'interface' argument will be ignored.
  warnings.warn(msg)
Exception in thread Thread-1:
Traceback (most recent call last):
  File "/usr/lib/python3.8/threading.py", line 932, in _bootstrap_inner
    self.run()
  File "/var/lib/kolla/venv/lib/python3.8/site-packages/freezer/utils/streaming.py", line 112, in run
    super(QueuedThread, self).run()
  File "/usr/lib/python3.8/threading.py", line 870, in run
    self._target(*self._args, **self._kwargs)
  File "/var/lib/kolla/venv/lib/python3.8/site-packages/freezer/engine/engine.py", line 100, in backup_stream
    rich_queue.put_messages(self.backup_data(backup_resource,
  File "/var/lib/kolla/venv/lib/python3.8/site-packages/freezer/utils/streaming.py", line 69, in put_messages
    for message in messages:
  File "/var/lib/kolla/venv/lib/python3.8/site-packages/freezer/engine/nova/nova.py", line 312, in backup_data
    self.set_tenant_meta(manifest_path, headers)
  File "/var/lib/kolla/venv/lib/python3.8/site-packages/freezer/engine/nova/nova.py", line 357, in set_tenant_meta
    fb.writelines(json.dumps(metadata))
TypeError: a bytes-like object is required, not 'str'
Exception in thread Thread-2:
Traceback (most recent call last):
  File "/var/lib/kolla/venv/lib/python3.8/site-packages/freezer/utils/streaming.py", line 58, in get
    res = self.data_queue.get(timeout=1)
  File "/usr/lib/python3.8/queue.py", line 178, in get
    raise Empty
_queue.Empty

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/var/lib/kolla/venv/lib/python3.8/site-packages/freezer/utils/streaming.py", line 88, in get_messages
    yield self.get()
  File "/var/lib/kolla/venv/lib/python3.8/site-packages/freezer/utils/streaming.py", line 62, in get
    raise Wait()
freezer.utils.streaming.Wait

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/usr/lib/python3.8/threading.py", line 932, in _bootstrap_inner
    self.run()
  File "/var/lib/kolla/venv/lib/python3.8/site-packages/freezer/utils/streaming.py", line 112, in run
    super(QueuedThread, self).run()
  File "/usr/lib/python3.8/threading.py", line 870, in run
    self._target(*self._args, **self._kwargs)
  File "/var/lib/kolla/venv/lib/python3.8/site-packages/freezer/storage/swift.py", line 209, in write_backup
    for block_index, message in enumerate(rich_queue.get_messages()):
  File "/var/lib/kolla/venv/lib/python3.8/site-packages/freezer/utils/streaming.py", line 90, in get_messages
    self.check_stop()
  File "/var/lib/kolla/venv/lib/python3.8/site-packages/freezer/utils/streaming.py", line 66, in check_stop
    raise Exception("Forced stop")
Exception: Forced stop
Critical Error: ('Engine error. Failed to backup.', {})
```

#### Invalid snapshot: Originating snapshot status must be one of 'available' values

freezer问题这么多，不搞了。。。
=> 反正已经验证到走了相应的nova备份源码，可以了...

```
Exception in thread Thread-1:
Traceback (most recent call last):
  File "/usr/lib/python3.8/threading.py", line 932, in _bootstrap_inner
    self.run()
  File "/opt/stack/freezer/freezer/utils/streaming.py", line 112, in run
    super(QueuedThread, self).run()
  File "/usr/lib/python3.8/threading.py", line 870, in run
    self._target(*self._args, **self._kwargs)
  File "/opt/stack/freezer/freezer/engine/engine.py", line 100, in backup_stream
    rich_queue.put_messages(self.backup_data(backup_resource,
  File "/opt/stack/freezer/freezer/utils/streaming.py", line 69, in put_messages
    for message in messages:
  File "/opt/stack/freezer/freezer/engine/nova/nova.py", line 295, in backup_data
    copied_volume = self.client.do_copy_volume(
  File "/opt/stack/freezer/freezer/openstack/osclients.py", line 250, in do_copy_volume
    volume = self.get_cinder().volumes.create(
  File "/usr/local/lib/python3.8/dist-packages/cinderclient/v3/volumes.py", line 129, in create
    return self._create('/volumes', body, 'volume')
  File "/usr/local/lib/python3.8/dist-packages/cinderclient/base.py", line 306, in _create
    resp, body = self.api.client.post(url, body=body)
  File "/usr/local/lib/python3.8/dist-packages/cinderclient/client.py", line 227, in post
    return self._cs_request(url, 'POST', **kwargs)
  File "/usr/local/lib/python3.8/dist-packages/cinderclient/client.py", line 215, in _cs_request
    return self.request(url, method, **kwargs)
  File "/usr/local/lib/python3.8/dist-packages/cinderclient/client.py", line 201, in request
    raise exceptions.from_response(resp, body)
cinderclient.exceptions.BadRequest: Invalid snapshot: Originating snapshot status must be one of 'available' values (HTTP 400) (Request-ID: req-d2c6ed03-f4a7-4d26-a1e7-940eaca79c33)
Exception in thread Thread-2:
Traceback (most recent call last):
  File "/opt/stack/freezer/freezer/utils/streaming.py", line 58, in get
    res = self.data_queue.get(timeout=1)
  File "/usr/lib/python3.8/queue.py", line 178, in get
    raise Empty
_queue.Empty
```
