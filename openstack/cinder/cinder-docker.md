# 在容器中运行cinder服务

参考kolla-ansible部署cinder服务

关键字《kolla-ansible部署cinder服务》

kolla-ansible --help

## 参考kolla安装的yoga版本，运行cinder服务

#### KSVD环境准备

依官网建mariadb的cinder数据库, 如下所示(注意: 替换CINDER_DBPASS为合适的密码):
https://docs.openstack.org/cinder/wallaby/install/cinder-controller-install-rdo.html
```
CREATE DATABASE cinder;
GRANT ALL PRIVILEGES ON cinder.* TO 'cinder'@'localhost' IDENTIFIED BY 'CINDER_DBPASS';
GRANT ALL PRIVILEGES ON cinder.* TO 'cinder'@'%' IDENTIFIED BY 'CINDER_DBPASS';
```

#### 部署cinder-api服务

查看kolla-ansible部署的cinder-api容器，获取到启动方式
```
docker inspect cinder_api
```

准备配置目录, 以及文件，先从kolla环境上拷贝, 然后修改
```
mkdir -p /var/log/kolla/cinder/
mkdir -p /etc/kolla/cinder-api/
touch /etc/kolla/cinder-api/{config.json,cinder.conf,cinder-wsgi.conf}
```

创建cinder-api配置文件
```
cat > /etc/kolla/cinder-api/cinder.conf << EOF
[DEFAULT]
debug = False
log_dir = /var/log/kolla/cinder
log_file = cinder-api.log
use_forwarded_for = true
use_stderr = False
my_ip = ${MY_IP}
osapi_volume_workers = 5
volume_name_template = volume-%s
osapi_volume_listen = ${MY_IP}
osapi_volume_listen_port = 8776
api_paste_config = /etc/cinder/api-paste.ini
auth_strategy = keystone
transport_url = rabbit://admin:kylin-ksvd@127.0.0.1:5672//ksvd-mc

[oslo_messaging_notifications]
transport_url = rabbit://admin:kylin-ksvd@127.0.0.1:5672//ksvd-mc
driver = noop

[oslo_middleware]
enable_proxy_headers_parsing = True

[database]
connection = mysql+pymysql://cinder:CINDER_DBPASS@127.0.0.1/cinder
connection_recycle_time = 10
max_pool_size = 1
max_retries = -1

[oslo_concurrency]
lock_path = /var/lib/cinder/tmp

[privsep_entrypoint]
helper_command = sudo cinder-rootwrap /etc/cinder/rootwrap.conf privsep-helper --config-file /etc/cinder/cinder.conf

[coordination]

EOF
```

使用cinder工具建表
```
docker run -it --rm --network host \
  --env KOLLA_CONFIG_STRATEGY=COPY_ALWAYS \
  --env KOLLA_SERVICE_NAME=cinder-api \
  --env KOLLA_BASE_DISTRO=ubuntu \
  --env KOLLA_INSTALL_TYPE=source \
  --env KOLLA_BASE_ARCH=x86_64 \
  --env KOLLA_DISTRO_PYTHON_VERSION=3.8 \
  --entrypoint "" \
  -v /etc/kolla/cinder-api/:/var/lib/kolla/config_files/:ro \
  -v /etc/localtime:/etc/localtime:ro \
  -v /var/log/kolla:/var/log/kolla/:rw \
  hub.iefcu.cn/public/ubuntu-source-cinder-api:yoga \
  cinder-manage --config-file /var/lib/kolla/config_files/cinder.conf db sync
```

先随便组一下, FIXME: 后续需要补充Healthcheck, 日志卷目录, /etc/timezone
```
docker run -d --name cinder_api --network host \
  --env KOLLA_CONFIG_STRATEGY=COPY_ALWAYS \
  --env KOLLA_SERVICE_NAME=cinder-api \
  --env KOLLA_BASE_DISTRO=ubuntu \
  --env KOLLA_INSTALL_TYPE=source \
  --env KOLLA_BASE_ARCH=x86_64 \
  --env KOLLA_DISTRO_PYTHON_VERSION=3.8 \
  -v /etc/kolla/cinder-api/:/var/lib/kolla/config_files/:ro \
  -v /etc/localtime:/etc/localtime:ro \
  -v /var/log/kolla:/var/log/kolla/:rw \
  hub.iefcu.cn/public/ubuntu-source-cinder-api:yoga
```

#### 部署cinder-scheduler服务

参考cinder-api一样的原理

先准备配置文件...
```
mkdir -p /etc/kolla/cinder-scheduler/
touch /etc/kolla/cinder-scheduler/{config.json,cinder.conf}
```

scheduler的cinder配置文件，基本和api的一样即可

然后运行cinder-scheduler容器
```
docker run -d --name cinder_scheduler --network host \
  --env KOLLA_CONFIG_STRATEGY=COPY_ALWAYS \
  --env KOLLA_SERVICE_NAME=cinder-scheduler \
  -v /etc/kolla/cinder-scheduler/:/var/lib/kolla/config_files/:ro \
  -v /etc/localtime:/etc/localtime:ro \
  -v /var/log/kolla:/var/log/kolla/:rw \
  hub.iefcu.cn/public/ubuntu-source-cinder-scheduler:yoga
```

#### 临时构建新的支持mmj驱动的镜像?

(或者直接map进去...)

创建Dockerfile
```
FROM hub.iefcu.cn/public/ubuntu-source-cinder-volume:yoga
ADD ./mmj-cinder/kylinsec /var/lib/kolla/venv/lib/python3.8/site-packages/cinder/volume/drivers/kylinsec
```

构建新镜像
```
git clone http://192.168.120.13/xiaoyun/mmj-cinder.git -b python3
docker build -t hub.iefcu.cn/xiaoyun/ubuntu-source-cinder-volume:yoga .
```

#### 部署cinder-volume服务

参考cinder-api一样的原理

先准备配置文件...
```
mkdir -p /etc/kolla/cinder-volume/
touch /etc/kolla/cinder-volume/{config.json,cinder.conf}
```

volume的cinder配置文件，基本和api的一样即可, 就是需要额外配置卷后端
(FIXME: 正好可以验证没有后端怎么样! => 启动失败)
```
[mmj]
volume_driver=cinder.volume.drivers.kylinsec.kylinsec.VolumeWrapDriver
volume_base_driver=cinder.volume.drivers.huawei.huawei_driver.HuaweiISCSIDriver
cinder_huawei_conf_file=/etc/cinder/cinder_huawei_conf.xml
kylin_san_ip=10.90.4.49
kylin_san_api_port=5000
kylin_san_login=sysadmin
kylin_san_password=sysadmin
kylin_san_type=iSCSI
volume_backend_name=mmj
```

然后运行cinder-volume容器
```
docker run -d --name cinder_volume --network host \
  --env KOLLA_CONFIG_STRATEGY=COPY_ALWAYS \
  --env KOLLA_SERVICE_NAME=cinder-volume \
  -v /etc/kolla/cinder-volume/:/var/lib/kolla/config_files/:ro \
  -v /etc/localtime:/etc/localtime:ro \
  -v /var/log/kolla:/var/log/kolla/:rw \
  hub.iefcu.cn/xiaoyun/ubuntu-source-cinder-volume:yoga
```

#### 部署cinder-backup服务

TODO:

### 验证是否有arm等其他架构版本...

现在我用的cinder镜像是单架构的, 再找找
关键字《kolla arm64 image》

https://docs.openstack.org/kolla/yoga/support_matrix.html
官网有arm64架构支持, 不过是C - Community maintained

https://cloudbase.it/openstack-on-arm64-part-1/
=> 可以尝试构建镜像

### 源码构建镜像

关键点:
- 基础镜像用哪个?
- 使用那个版本，源码或者release
- 启动命令
- 其他参数
  例如liveness等

思路:
- 基于kolla编译构建镜像
- 基于发行版本简单编译构建
  可以基于源码, 或者基于rpm包
- 基于已有的别人构建的镜像构建
  例如: docker.io/kolla/cinder-api:zed-debian-bullseye-aarch64
