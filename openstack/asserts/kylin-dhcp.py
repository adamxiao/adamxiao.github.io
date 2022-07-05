#!/usr/bin/env python
# -*- coding:utf-8 -*-

import yaml
from yaml.loader import SafeLoader
import subprocess
import argparse
import os
import time
import fcntl
import shutil

OVS="/usr/lib/ksvd/bin/ovs-vsctl --db=unix:/run/openvswitch/db.sock"
SERVICE_DIR = '/lib/systemd/system/'

'''yaml
dhcp:
  ipaddr: 192.168.101.250
  gateway: 192.168.101.254
  mac: 52:54:84:11:00:00
  bridge: bridge
  vlanid: 0
  l3_id: subnet1
  dns: 10.90.3.38,192.168.168.168
  netmask: 255.255.255.0
ip_list:
  - ip: 192.168.101.190
    mac: 52:54:84:00:07:c6
  - ip: 192.168.101.191
    mac: 52:54:84:00:07:ca
'''

# hosts.option示例配置
'''
# hosts.option
tag:facb2b4a7501,3
tag:facb2b4a7501,6
tag:facb2b4a7501,option:netmask,255.255.255.0
tag:facb2b4a7501,option:mtu,1500

tag:faa91684f700,option:router,192.168.222.1
tag:faa91684f700,option:dns-server,223.5.5.5
tag:faa91684f700,option:classless-static-route,0.0.0.0/0,192.168.222.1,169.254.169.254/32,192.168.222.254
tag:faa91684f700,option:microsoft-249,0.0.0.0/0,192.168.222.1,169.254.169.254/32,192.168.222.254
tag:faa91684f700,option:netmask,255.255.255.0
tag:faa91684f700,option:mtu,1500
'''

# 测试:
# 没有文件的情况; 文件为空内容的情况; 语法异常的情况; 配置缺失的情况;
# 读取配置文件
def load_config(conf_file):
  # 传入配置文件, 例如: /etc/kylin-dhcp/kylin-dhcp.yaml
  with open(conf_file) as f:
    data = yaml.load(f, Loader=SafeLoader)
    # print(data)
    return data
  return nil

def get_l3_name(data):
  dhcp = data['dhcp']
  return 'vpc-' + dhcp['l3_id']

# XXX: 处理参数异常情况!
# def gen_dnsmasq_conf(data):
def gen_dhcp_conf(data):
  dhcp = data['dhcp']
  l3_name = get_l3_name(data)
  ip = dhcp['ipaddr']

  dirname = '/var/lib/ksvd/dnsmasq/' + l3_name
  if not os.path.exists(dirname):
    os.makedirs(dirname)

  filename = dirname + '/dnsmasq.conf'
  fp = open(filename, 'w')

  fp.write('''\
domain-needed
bogus-priv
no-hosts
addn-hosts=%s/hosts.dns
dhcp-option=vendor:MSFT,2,1i
dhcp-lease-max=65535
dhcp-hostsfile=%s/hosts.dhcp
dhcp-optsfile=%s/hosts.option
log-facility=%s/dnsmasq.log
#interface=inner5
except-interface=lo
#bind-interfaces
leasefile-ro
dhcp-range=%s,static
''' % (dirname, dirname, dirname, dirname, ip))

  fp.close()

  filename = dirname + '/hosts.dhcp'
  fp = open(filename, 'w')

  for ip_conf in data['ip_list']:
    # fa:c8:6f:df:a3:01,set:fac86fdfa301,156.134.23.139,infinite
    ip = ip_conf['ip']
    mac = ip_conf['mac']
    mac_id = mac.replace(':', '')
    fp.write('%s,set:%s,%s,infinite\n' % (mac, mac_id, ip))

  filename = dirname + '/hosts.dns'
  fp = open(filename, 'w')

  for ip_conf in data['ip_list']:
    pass
  fp.close()

  filename = dirname + '/hosts.option'
  fp = open(filename, 'w')

  gateway = dhcp['gateway']
  dns = dhcp['dns']
  netmask = dhcp['netmask']

  for ip_conf in data['ip_list']:
    ip = ip_conf['ip']
    mac = ip_conf['mac']
    mac_id = mac.replace(':', '')
    fp.write('tag:%s,option:netmask,%s\n' % (mac_id, netmask))
    fp.write('tag:%s,option:mtu,1500\n' % mac_id)
    fp.write('tag:%s,option:dns-server,%s\n' % (mac_id, dns))
    fp.write('tag:%s,option:router,%s\n' % (mac_id, gateway))
  fp.close()


# XXX: 日志文件需要留下分析吗? no
# 删除dhcp相关配置文件
def clean_dhcp_conf(l3_name):
  dhcp_conf_dir = '/var/lib/ksvd/dnsmasq/' + l3_name
  if not os.path.exists(dhcp_conf_dir):
    print("dhcp conf dir not exist, do nothing!")
  else:
    shutil.rmtree(dhcp_conf_dir)

def create_netns(name):
  # cmd = 'ip netns add vpc-subnet1'
  return_code = subprocess.call(["ip","netns", "add", name])
  print('create netns return %d' % return_code)

def destroy_netns(name):
  # cmd = 'ip netns add vpc-subnet1'
  return_code = subprocess.call(["ip","netns", "del", name])
  print('delete netns return %d' % return_code)


# 把dhcp接口加入到netns中, 并配置ip,mac,link up等
def config_dhcp_interface(data):
  dhcp = data['dhcp']
  l3_name = get_l3_name(data)
  mac = dhcp['mac']
  ipaddr = dhcp['ipaddr']
  netmask = dhcp['netmask']

  cmd = "ip link set {l3_name} netns {l3_name}".format(l3_name=l3_name)
  return_code = subprocess.call(cmd, shell=True)
  print('add interface to netns return %d' % return_code)

  cmd = "ip netns exec {l3_name} ip link set {l3_name} address {mac}".format(l3_name=l3_name, mac=mac)
  return_code = subprocess.call(cmd, shell=True)
  print('set interface mac addr return %d' % return_code)

  cmd = "ip netns exec {l3_name} ip addr add {ipaddr}/{netmask} dev {l3_name}".format(l3_name=l3_name, ipaddr=ipaddr, netmask=netmask)
  return_code = subprocess.call(cmd, shell=True)
  print('set interface ipaddr return %d' % return_code)

  cmd = "ip netns exec {l3_name} ip link set {l3_name} up".format(l3_name=l3_name)
  return_code = subprocess.call(cmd, shell=True)
  print('set interface to netns return %d' % return_code)


# 创建dhcp接口
def create_dhcp_interface(data):
  dhcp = data['dhcp']
  bridge = dhcp['bridge']
  l3_name = get_l3_name(data)
  vlanid = dhcp['vlanid']
  # ${OVS} --may-exist add-port "${dvsname_value}" "${subnetname_value}" -- set interface "${subnetname_value}" type=internal -- set Port "${subnetname_value}" tag="${vlan_value}"
  cmd = '{ovs} --may-exist add-port {bridge} {l3_name} -- set interface {l3_name} type=internal -- set Port {l3_name} tag={vlanid}'.format(ovs=OVS, bridge=bridge, l3_name=l3_name, vlanid=vlanid)
  #print(cmd)
  return_code = subprocess.call(cmd, shell=True)
  print('create dhcp interface return %d' % return_code)

  config_dhcp_interface(data)

# 删除dhcp接口
def destroy_dhcp_interface(l3_name):
  cmd = '{ovs} del-port {l3_name}'.format(ovs=OVS, l3_name=l3_name)
  #print(cmd)
  return_code = subprocess.call(cmd, shell=True)
  print('destroy dhcp interface return %d' % return_code)

# 创建dhcp系统服务, 并启动
def create_dhcp_server(data):
  l3_name = get_l3_name(data)

  tmp_dhcp_service ='/var/run/kylin-dhcp/' + l3_name + '.service'
  dhcp_service = SERVICE_DIR + l3_name + '.service'

  fp = open(tmp_dhcp_service, 'w')

  fp.write('''\
[Unit]
Description=DHCP server
After=network.target

[Service]
ExecStart=/usr/sbin/ip netns exec {l3_name} /usr/sbin/dnsmasq -k --conf-file=/var/lib/ksvd/dnsmasq/{l3_name}/dnsmasq.conf
Restart=always
RestartSec=1s

ExecReload=/bin/kill -HUP $MAINPID

[Install]
WantedBy=multi-user.target
'''.format(l3_name=l3_name))

  fp.close()

  shutil.move(tmp_dhcp_service, dhcp_service)

  return_code = subprocess.call("systemctl daemon-reload", shell=True)
  print('reload systemctl daemon return %d' % return_code)

  start_cmd = 'systemctl start ' + l3_name
  return_code = subprocess.call(start_cmd, shell=True)
  print('start dhcp service return %d' % return_code)

    
# 停止dhcp服务, 销毁dhcp服务
def destroy_dhcp_server(l3_name):
  dhcp_service = SERVICE_DIR + l3_name + '.service'
  if not os.path.exists(dhcp_service):
    print("dhcp service not exist, do nothing!")
    return

  stop_cmd = 'systemctl stop ' + l3_name
  print(stop_cmd)
  return_code = subprocess.call(stop_cmd, shell=True)
  print('stop dhcp service return %d' % return_code)

  os.remove(dhcp_service)
  print(dhcp_service)

  return_code = subprocess.call("systemctl daemon-reload", shell=True)
  print('reload systemctl daemon return %d' % return_code)


# 检查dhcp服务是否存在
def is_exist_dhcp_server(l3_name):
  dhcp_service = SERVICE_DIR + l3_name + '.service'
  return os.path.exists(dhcp_service)


# dhcp服务重新加载配置
def reload_dhcp_server(l3_name):
  reload_cmd = 'systemctl reload ' + l3_name
  return_code = subprocess.call(reload_cmd, shell=True)
  print('reload dhcp service return %d' % return_code)


def check_flag():
  return os.path.exists('/var/run/kylin-dhcp')

def gen_flag():
  os.makedirs('/var/run/kylin-dhcp')


# 重新生成dhcp配置, 重新加载dhcp配置
def reload_dhcp(conf_file):
  if not check_flag():
    gen_flag()
  data = load_config(conf_file)
  if not data:
    print('load config %s failed!' % conf_file)
    return

  l3_name = get_l3_name(data)
  gen_dhcp_conf(data)
  reload_dhcp_server(l3_name)


# 创建dhcp并启动dhcp服务
def create_dhcp(conf_file):
  if not check_flag():
    gen_flag()
  data = load_config(conf_file)
  if not data:
    print('load config %s failed!' % conf_file)
    return

  l3_name = get_l3_name(data)

  # 禁止重复创建dhcp
  if is_exist_dhcp_server(l3_name):
    print('dhcp exist, do nothing!')
    return

  # 1. 创建netns
  # 2. 创建dhcp接口
  # 3. 生成dnsmasq配置
  # 4. 创建dhcp服务配置，以及启动服务
  create_netns(l3_name)
  create_dhcp_interface(data)
  gen_dhcp_conf(data)
  create_dhcp_server(data)


# 销毁dhcp服务
def destroy_dhcp(network):
  if not check_flag():
    gen_flag()
  # 可以指定l3_name, 或者通过配置文件获取到l3_name
  if network:
    l3_name = 'vpc-' + network
  else:
    print('empty network!')
    return

  # 对应创建dhcp的反向操作
  # 1. 停止dhcp服务, 以及销毁dhcp服务配置
  # 2. 销毁dnsmasq配置
  # 3. 销毁dhcp接口
  # 4. 销毁netns
  destroy_dhcp_server(l3_name)
  clean_dhcp_conf(l3_name)
  destroy_dhcp_interface(l3_name)
  destroy_netns(l3_name)


# 获取所有的dhcp服务列表, 以及状态
def list_all_dhcp_status():
  list_cmd = "systemctl list-unit-files | grep ^vpc- | awk '{print $1}'"
  proc = subprocess.Popen(list_cmd, shell=True, stdout = subprocess.PIPE)
  dhcp_list = []
  while True:
    line = proc.stdout.readline()
    if not line:
      break
    dhcp_list.append(line.rstrip())

  if 0 == len(dhcp_list):
    print('{}')
    return

  status_cmd = "systemctl is-active " + " ".join(dhcp_list)
  status_list = []
  proc = subprocess.Popen(status_cmd, shell=True, stdout = subprocess.PIPE)
  while True:
    line = proc.stdout.readline()
    if not line:
      break
    status_list.append(line.rstrip())

  # 关键字《python 两个list合成字典》
  # 输出示例为{'vpc-vpc-subnet1.service': 'active'}
  dict_all = dict(zip(dhcp_list, status_list))
  print(dict_all)


def is_running(file):
  fd = open(file, "w")
  try:
    fcntl.lockf(fd, fcntl.LOCK_EX|fcntl.LOCK_NB)
  except :
    return None
  return fd

def get_lock():
  lockfile = "/var/run/kylin-dhcp-running"
  while True:
    fd = is_running(lockfile)
    if fd:
      return fd
    time.sleep(1)


def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('-c', '--command', help='sub command', \
        choices=['create', 'destroy', 'reload', 'status'], \
        default='reload')
  parser.add_argument('-y', '--yaml', help='specify dhcp config yaml. Example: -c init -y xxx.yaml')
  parser.add_argument('-n', '--network', help='specify vpc network name. Example: -c destroy -n subnet1')
  args = parser.parse_args()

  # 加锁保证单例执行
  a = get_lock()

  cmd = args.command if args.command else 'init'
  if 'create' == cmd:
    create_dhcp(args.yaml)
  elif 'destroy' == cmd:
    destroy_dhcp(args.network)
  elif 'status' == cmd:
    list_all_dhcp_status()
  else: # reload
    reload_dhcp(args.yaml)

if __name__ == '__main__':
  main()
