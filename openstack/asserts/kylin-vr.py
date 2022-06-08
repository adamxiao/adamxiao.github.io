#!/usr/bin/env python
# -*- coding:utf-8 -*-

import yaml
from yaml.loader import SafeLoader
import subprocess
import netifaces
import argparse
import os
import time
import fcntl

'''yaml
if_list:
   - ipaddr: 10.90.3.37
     prefix: 24
     mac: 52:54:84:11:00:00
     gateway: 10.90.3.1
   - ipaddr: 192.168.100.254
     prefix: 24
     mac: 52:54:84:00:08:38
eip_list:
  - eip: 10.90.2.252
    vm-ip: 192.168.100.192
  - eip: 10.90.2.253
    vm-ip: 192.168.100.193
port_forward_list:
  # master1.kcp5-arm.iefcu.cn
  - eip: 10.90.2.254
    protocal: udp
    port: 80
    end_port: 82
    vm-port: 80
    vm-ip: 192.168.100.190
'''

# https://blog.csdn.net/sunny_day_day/article/details/119893768
def load_interface():
  """获取接口mac地址对应名称"""
  macMap = {}
  for interface in netifaces.interfaces():
    macAddr = netifaces.ifaddresses(interface)[netifaces.AF_LINK][0]['addr']
    macMap[macAddr] = interface
  # print(macMap)
  return macMap


# 测试:
# 没有文件的情况; 文件为空内容的情况; 语法异常的情况; 配置缺失的情况;
# 读取配置文件
def load_config():
  # Open the file and load the file
  with open('/etc/kylin-vr/kylin-vr.yaml') as f:
    data = yaml.load(f, Loader=SafeLoader)
    # print(data)
    return data
  return nil


# XXX: 优化, 增量更新配置文件?
def one_interface_conf(ifname, ifconf, eip_list):
  """docstring for one_interface"""
  # filename = '/etc/sysconfig/network-scripts/ifcfg-' + ifname
  filename = '/var/run/kylin-vr/ifcfg-' + ifname
  # print(filename)

  fp = open(filename, 'w')

  fp.write('NAME=%s\nDEVICE="%s"\n' % (ifname, ifname))
  fp.write('''BOOTPROTO="none"
ONBOOT="yes"
TYPE="Ethernet"
IPV6INIT="no"
''')
  fp.write('''
IPADDR=%s
PREFIX=%s
''' % (ifconf['ipaddr'], ifconf['prefix']))
  if 'gateway' in ifconf:
    fp.write('GATEWAY=%s\n' % ifconf['gateway'])

    for i, eip in enumerate(eip_list):
      fp.write('''IPADDR%d=%s\nPREFIX%d=32\n''' % (i+1, eip, i+1))
  fp.close()


def get_eip_list(data):
  eip_set = set()

  for eip in data['eip_list']:
    eip_set.add(eip['eip'])

  for port_forward in data['port_forward_list']:
    eip_set.add(port_forward['eip'])

  return eip_set


# XXX: 处理参数异常情况!
def gen_network_conf(data):
  macMap = load_interface()
  eip_list = []
  for i, if_conf in enumerate(data['if_list']):
    mac = if_conf['mac']
    if mac not in macMap:
      # debug log
      continue
    interface = macMap[mac]
    data['if_list'][i]['ifname'] = interface

    if 'gateway' in if_conf: # 网关接口为公网物理出口
      data['ifname'] = interface
      eip_list = get_eip_list(data)

    # print(mac)
    # print(interface)
    one_interface_conf(interface, if_conf, eip_list)

  # 最后, 替换成新的ifcfg-xxx配置
  subprocess.call("rm -f /etc/sysconfig/network-scripts/ifcfg-eth*", shell=True)
  subprocess.call("mv /var/run/kylin-vr/ifcfg-eth* /etc/sysconfig/network-scripts", shell=True)


# 生成eip规则
def gen_eip_iptable_conf(f, data):
  # 1. 通过网关地址获取到公网接口名称
  # ip route | head -1 | grep default | awk '{print $5}'
  # 2. 或者通过mac地址获取公网接口名称
  if 'ifname' not in data:
    return

  ifname = data['ifname']

  for eip_item in data['eip_list']:
    extern_ip=eip_item['eip']
    vm_ip=eip_item['vm-ip']
    f.write("-A POSTROUTING -s %s/32 -o %s -j SNAT --to-source %s\n" % (vm_ip, ifname, extern_ip))
    f.write("-A PREROUTING -i %s -d %s/32 -j DNAT --to-destination %s\n" % (ifname, extern_ip, vm_ip))


# 生成snat规则
def gen_snat_iptable_conf(f, data):
  if 'ifname' not in data:
    return

  ifname = data['ifname']

  # 默认网关接口开启snat
  f.write('-A POSTROUTING -o %s -j MASQUERADE\n' % ifname)


# 生成端口转发iptable规则表
def gen_port_forward_iptable_conf(f, data):
  for port_forward in data['port_forward_list']:
    extern_ip = port_forward['eip']
    vm_ip = port_forward['vm-ip']
    protocal = port_forward['protocal']
    port = port_forward['port']
    vm_port = port_forward['vm-port']

    if 'end_port' not in port_forward: # 单端口映射
      f.write("-A PREROUTING -p %s -d %s --dport %d -j DNAT --to %s:%d\n" % (protocal, extern_ip, port, vm_ip, vm_port))
      f.write("-A POSTROUTING -p %s -s %s --sport %d -j SNAT --to %s:%d\n" % (protocal, vm_ip, vm_port, extern_ip, port))

    else: # 端口范围映射
      end_port = port_forward['end_port']
      f.write("-A PREROUTING -p %s -d %s --dport %d:%d -j DNAT --to %s:%d-%d\n" % (protocal, extern_ip, port, end_port, vm_ip, port, end_port))
      f.write("-A POSTROUTING -p %s -s %s --sport %d:%d -j SNAT --to %s:%d-%d\n" % (protocal, vm_ip, port, end_port, extern_ip, port, end_port))
  

# eip, snat, port forward的iptable规则配置
def gen_iptable_conf(data):
  f = open("/var/run/kylin-vr/iptable.txt", 'w')
  f.write('''
*filter
:INPUT ACCEPT
:FORWARD ACCEPT
:OUTPUT ACCEPT
COMMIT

*mangle
:PREROUTING ACCEPT
:INPUT ACCEPT
:FORWARD ACCEPT
:OUTPUT ACCEPT
:POSTROUTING ACCEPT
COMMIT

*nat
:PREROUTING ACCEPT
:INPUT ACCEPT
:OUTPUT ACCEPT
:POSTROUTING ACCEPT
''')

  gen_eip_iptable_conf(f, data)
  gen_port_forward_iptable_conf(f, data)
  gen_snat_iptable_conf(f, data)

  f.write('\nCOMMIT\n')
  f.close()

# 恢复iptable配置
def reload_iptable():
  return_code = subprocess.call(["iptables-restore","/var/run/kylin-vr/iptable.txt"])
  print('iptable reload return %d' % return_code)


# 重置network配置
def reload_network(data):
  """docstring for reload_network"""
  return_code = subprocess.call("nmcli c reload", shell=True)
  print('nmcli c reload return %d' % return_code)

  for if_conf in data['if_list']:
    if 'ifname' not in if_conf:
      continue
    cmd = 'nmcli c up %s' % if_conf['ifname']
    return_code = subprocess.call(cmd, shell=True)
    print('up connection `%s` return %d' % (cmd, return_code))


def check_flag():
  return os.path.exists('/var/run/kylin-vr')

def gen_flag():
  os.makedirs('/var/run/kylin-vr')

def config_init():
  gen_flag()
  data = load_config()
  if not data:
    print('load config failed!')
    return
  gen_network_conf(data)
  gen_iptable_conf(data)
  reload_iptable()
  pass


# 系统起来之后的配置更新
def config_reload(device):
  if not check_flag():
    print('kylin-vr service is not started, can not reload config!')
    return
  data = load_config()
  if not data:
    print('load config failed!')
    return
  gen_network_conf(data)
  gen_iptable_conf(data)
  reload_network(data)
  reload_iptable()
  pass


def is_running(file):
  fd = open(file, "w")
  try:
    fcntl.lockf(fd, fcntl.LOCK_EX|fcntl.LOCK_NB)
  except :
    return None
  return fd

def get_lock():
  lockfile = "/var/run/kylin-vr-running"
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
    config_init()

if __name__ == '__main__':
  main()
