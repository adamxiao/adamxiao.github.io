#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import yaml
from yaml.loader import SafeLoader
import subprocess
# import netifaces
import argparse
import os
import time
import fcntl

OVS="/usr/lib/ksvd/bin/ovs-vsctl --db=unix:/run/openvswitch/db.sock"

'''yaml
dhcp:
  ipaddr: 192.168.100.250
  gateway: 192.168.100.254
  mac: 52:54:84:11:00:00
  bridge: mdvs2
  vlanid: 0
  l3_id: subnet1
  dns: 10.90.3.38
  netmask: 255.255.255.0
ip_list:
  - ip: 192.168.100.190
    mac: 52:54:84:00:07:c6
  - ip: 192.168.100.191
    mac: 52:54:84:00:07:ca
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
  filename = '/var/run/kylin-dhcp/dnsmasq.conf'
  fp = open(filename, 'w')

  dhcp = data['dhcp']
  l3_id = dhcp['l3_id']
  ip = dhcp['ipaddr']

  fp.write('''\
domain-needed
bogus-priv
no-hosts
addn-hosts=/var/lib/kylin/dnsmasq/%s/hosts.dns
dhcp-option=vendor:MSFT,2,1i
dhcp-lease-max=65535
dhcp-hostsfile=/var/lib/kylin/dnsmasq/%s/hosts.dhcp
dhcp-optsfile=/var/lib/kylin/dnsmasq/%s/hosts.option
log-facility=/var/lib/kylin/dnsmasq/%s/dnsmasq.log
#interface=inner5
except-interface=lo
#bind-interfaces
leasefile-ro
dhcp-range=%s,static
''' % (l3_id, l3_id, l3_id, l3_id, ip))

  fp.close()

  filename = '/var/run/kylin-dhcp/hosts.dhcp'
  fp = open(filename, 'w')

  for ip_conf in data['ip_list']:
    # fa:c8:6f:df:a3:01,set:fac86fdfa301,156.134.23.139,infinite
    ip = ip_conf['ip']
    mac = ip_conf['mac']
    mac_id = mac.replace(':', '')
    fp.write('%s,set:%s,%s,infinite\n' % (mac, mac_id, ip))

  filename = '/var/run/kylin-dhcp/hosts.dns'
  fp = open(filename, 'w')

  for ip_conf in data['ip_list']:
    pass
  fp.close()

  filename = '/var/run/kylin-dhcp/hosts.option'
  fp = open(filename, 'w')

  gateway = dhcp['gateway']
  dns = dhcp['dns']
  netmask = dhcp['netmask']

  for ip_conf in data['ip_list']:
    ip = ip_conf['ip']
    mac = ip_conf['mac']
    mac_id = mac.replace(':', '')
    fp.write('tag:%s,3\n' % mac_id)
    fp.write('tag:%s,6\n' % mac_id)
    fp.write('tag:%s,option:netmask,%s\n' % (mac_id, netmask))
    fp.write('tag:%s,option:mtu,1500\n' % mac_id)
    fp.write('tag:%s,option:dns-server,%s\n' % (mac_id, dns))
  fp.close()

  create_dhcp_interface(data)
  # TODO: create netns, put netns, set ip addr, up interface
  # ip netns add vpc-subnet1
  # ip link set vpc-subnet1 netns vpc-subnet1

  # ip netns exec vpc-subnet1 ip addr add 192.168.110.250/24 dev vpc-subnet1
  # FIXME: ip netns exec vpc-subnet1 ip link set vpc-subnet1 address 02:ac:10:ff:00:11
  # ip netns exec vpc-subnet1 ip a s vpc-subnet1
  # ip netns exec vpc-subnet1 ip link set vpc-subnet1 up

  # TODO: 看一下之前什么配置接口的?

  # 最后, 替换成新的ifcfg-xxx配置
  # subprocess.call("rm -f /etc/sysconfig/network-scripts/ifcfg-eth*", shell=True)


def create_dhcp_interface(data):
  dhcp = data['dhcp']
  bridge = dhcp['bridge']
  l3_name = 'vpc-' + dhcp['l3_id']
  vlanid = dhcp['vlanid']
  # ${OVS} --may-exist add-port "${dvsname_value}" "${subnetname_value}" -- set interface "${subnetname_value}" type=internal -- set Port "${subnetname_value}" tag="${vlan_value}"
  cmd = '{ovs} --may-exist add-port {bridge} {l3_name} -- set interface {l3_name} type=internal -- set Port {l3_name} tag={vlanid}'.format(ovs=OVS, bridge=bridge, l3_name=l3_name, vlanid=vlanid)
  print(cmd)

def delete_dhcp_interface():
  pass

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
  parser.add_argument('-c', '--command', help='sub command, Note: the allocate command needs to be used with -d parameters', \
        choices=['init', 'reload', 'subnet'], \
        default='init')
  parser.add_argument('-d', '--device', help='the subnet command needs to specify interface name. Example: -c subnet -d eth2')
  args = parser.parse_args()

  # 加锁保证单例执行
  a = get_lock()

  cmd = args.command if args.command else 'init'
  if 'reload' == cmd:
    config_reload(args.device)
  # elif 'subnet' == cmd:
    # config_subnet(args.device)
  else: # init
    config_reload(args.device)

if __name__ == '__main__':
  main()
