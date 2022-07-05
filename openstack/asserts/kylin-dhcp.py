#!/usr/bin/env python
# -*- coding:utf-8 -*-

import yaml
from yaml.loader import SafeLoader
import subprocess
import argparse
import os
import time
import fcntl

OVS="/usr/lib/ksvd/bin/ovs-vsctl --db=unix:/run/openvswitch/db.sock"

# TODO: 多dns测试; dhcp ip地址和mac地址固定;

'''yaml
dhcp:
  ipaddr: 192.168.101.250
  gateway: 192.168.101.254
  mac: 52:54:84:11:00:00
  bridge: bridge
  vlanid: 0
  l3_id: vpc-subnet1
  dns: 10.90.3.38
  netmask: 255.255.255.0
ip_list:
  - ip: 192.168.101.190
    mac: 52:54:84:00:07:c6
  - ip: 192.168.101.191
    mac: 52:54:84:00:07:ca
'''

# 参考zstack的配置
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
def load_config():
  # Open the file and load the file
  with open('/etc/kylin-dhcp/kylin-dhcp.yaml') as f:
    data = yaml.load(f, Loader=SafeLoader)
    # print(data)
    return data
  return nil


# XXX: 处理参数异常情况!
# def gen_dnsmasq_conf(data):
def gen_dhcp_conf(data):
  dhcp = data['dhcp']
  l3_id = dhcp['l3_id']
  ip = dhcp['ipaddr']

  dirname = '/var/lib/ksvd/dnsmasq/' + l3_id
  # TODO: mkdir -p
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
    fp.write('tag:%s,router,%s\n' % (mac_id, gateway))
  fp.close()

  create_dhcp_interface(data)
  #delete_dhcp_interface(data)
  l3_name = 'vpc-' + dhcp['l3_id']
  create_netns(l3_name)
  #delete_netns(l3_name)
  config_dhcp_interface(data)

  # ip netns exec vpc-subnet1 ip addr add 192.168.110.250/24 dev vpc-subnet1
  # FIXME: ip netns exec vpc-subnet1 ip link set vpc-subnet1 address 02:ac:10:ff:00:11
  # ip netns exec vpc-subnet1 ip a s vpc-subnet1
  # ip netns exec vpc-subnet1 ip link set vpc-subnet1 up

  # TODO: 看一下之前什么配置接口的?

  # 最后, 替换成新的ifcfg-xxx配置
  # subprocess.call("rm -f /etc/sysconfig/network-scripts/ifcfg-eth*", shell=True)

def create_netns(name):
  # cmd = 'ip netns add vpc-subnet1'
  return_code = subprocess.call(["ip","netns", "add", name])
  print('create netns return %d' % return_code)

def delete_netns(name):
  # cmd = 'ip netns add vpc-subnet1'
  return_code = subprocess.call(["ip","netns", "del", name])
  print('delete netns return %d' % return_code)


# 把dhcp接口加入到netns中, 并配置ip,mac,link up等
def config_dhcp_interface(data):
  dhcp = data['dhcp']
  l3_name = 'vpc-' + dhcp['l3_id']
  mac = dhcp['mac']
  ipaddr = dhcp['ipaddr']

  cmd = "ip link set {l3_name} netns {l3_name}".format(l3_name=l3_name)
  return_code = subprocess.call(cmd, shell=True)
  print('add interface to netns return %d' % return_code)

  cmd = "ip netns exec {l3_name} ip link set {l3_name} address {mac}".format(l3_name=l3_name, mac=mac)
  return_code = subprocess.call(cmd, shell=True)
  print('set interface mac addr return %d' % return_code)

  # TODO: netmask convert to prefix
  cmd = "ip netns exec {l3_name} ip addr add {ipaddr}/24 dev {l3_name}".format(l3_name=l3_name, ipaddr=ipaddr)
  return_code = subprocess.call(cmd, shell=True)
  print('set interface ipaddr return %d' % return_code)

  cmd = "ip netns exec {l3_name} ip link set {l3_name} up".format(l3_name=l3_name)
  return_code = subprocess.call(cmd, shell=True)
  print('set interface to netns return %d' % return_code)

def create_dhcp_interface(data):
  dhcp = data['dhcp']
  bridge = dhcp['bridge']
  l3_name = 'vpc-' + dhcp['l3_id']
  vlanid = dhcp['vlanid']
  # ${OVS} --may-exist add-port "${dvsname_value}" "${subnetname_value}" -- set interface "${subnetname_value}" type=internal -- set Port "${subnetname_value}" tag="${vlan_value}"
  cmd = '{ovs} --may-exist add-port {bridge} {l3_name} -- set interface {l3_name} type=internal -- set Port {l3_name} tag={vlanid}'.format(ovs=OVS, bridge=bridge, l3_name=l3_name, vlanid=vlanid)
  #print(cmd)
  return_code = subprocess.call(cmd, shell=True)
  print('create_dhcp_interface return %d' % return_code)

def delete_dhcp_interface(data):
  dhcp = data['dhcp']
  bridge = dhcp['bridge']
  l3_name = 'vpc-' + dhcp['l3_id']
  vlanid = dhcp['vlanid']
  # ${OVS} --may-exist add-port "${dvsname_value}" "${subnetname_value}" -- set interface "${subnetname_value}" type=internal -- set Port "${subnetname_value}" tag="${vlan_value}"
  cmd = '{ovs} del-port {bridge} {l3_name}'.format(ovs=OVS, bridge=bridge, l3_name=l3_name)
  #print(cmd)
  return_code = subprocess.call(cmd, shell=True)
  print('delete_dhcp_interface return %d' % return_code)

def create_dhcp_server():
  pass
    
def delete_dhcp_server():
  pass


def check_flag():
  return os.path.exists('/var/run/kylin-dhcp')

def gen_flag():
  os.makedirs('/var/run/kylin-dhcp')


# 系统起来之后的配置更新
def config_reload(device):
  if not check_flag():
    gen_flag()
  data = load_config()
  if not data:
    print('load config failed!')
    return
  gen_dhcp_conf(data)
  pass


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
        choices=['init', 'reload', 'final'], \
        default='init')
  parser.add_argument('-d', '--device', help='specify interface name. Example: -c init -d eth2')
  args = parser.parse_args()

  # 加锁保证单例执行
  a = get_lock()

  cmd = args.command if args.command else 'init'
  if 'init' == cmd:
    config_reload(args.device)
  elif 'final' == cmd:
    config_reload(args.device)
  elif 'create' == cmd: # 
    config_reload(args.device)
  else: # reload
    config_reload(args.device)

if __name__ == '__main__':
  main()
