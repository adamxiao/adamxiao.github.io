#!/usr/bin/env python
# -*- coding:utf-8 -*-

import subprocess
import argparse
import time
import fcntl
import json
import base64
import os

OVS="/usr/lib/ksvd/bin/ovs-vsctl --db=unix:/run/openvswitch/db.sock"
SERVICE_DIR = '/lib/systemd/system/'


# 写文件内容到虚拟机文件中
def write_file_content(domain, file_id, conf_file):
  if not os.path.exists(conf_file):
    print('conf_file %s not exist, do nothing!' % conf_file)
    return False

  cmd_prefix = 'virsh qemu-agent-command {domain} --cmd '.format(domain=domain)

  # XXX: 文件太大的话是否分段写入
  with open(conf_file, "rb") as fp:
    b64_buff = base64.b64encode(fp.read())
    write_cmd = cmd_prefix + '\'{"execute":"guest-file-write", "arguments":{"handle":%s,"buf-b64":"%s"}}\'' % (file_id, b64_buff)
    # print(write_cmd)
    return_code = subprocess.call(write_cmd, shell=True)
    if 0 != return_code:
      print('write file failed, ret is %d' % return_code)
      return False

  return True


# 重新配置虚拟路由虚拟机配置
def reload_vr_conf(domain, conf_file):
  cmd_prefix = 'virsh qemu-agent-command {domain} --cmd '.format(domain=domain)
  open_cmd = cmd_prefix + '\'{"execute":"guest-file-open", "arguments":{"path":"/etc/kylin-vr/kylin-vr.yaml","mode":"w"}}\''
  #open_cmd = cmd_prefix + '\'{"execute":"guest-file-open", "arguments":{"path":"/tmp/kylin-vr.yaml","mode":"w"}}\''
  # print(open_cmd)

  # XXX: 检查返回内容是否正常?
  proc = subprocess.Popen(open_cmd, shell=True, stdout = subprocess.PIPE)
  result = json.load(proc.stdout)
  #print(result)
  file_id = result['return']
  #print("fileid is %s" % file_id)

  write_ret = write_file_content(domain, file_id, conf_file)
  if not write_ret:
    print("write file content failed")

  # XXX: 文件句柄一直不关会怎么样呢?
  close_cmd = cmd_prefix + '\'{"execute":"guest-file-close", "arguments":{"handle":%s}}\'' % file_id
  # print(close_cmd)
  return_code = subprocess.call(close_cmd, shell=True)
  if 0 != return_code:
    print('close file failed, ret %d' % return_code)

  if write_ret:
    kylin_vr_reload(domain)


# 虚拟路由程序重新读取加载配置文件
def kylin_vr_reload(domain):
  cmd_prefix = 'virsh qemu-agent-command {domain} --cmd '.format(domain=domain)

  reload_cmd = cmd_prefix + '\'{"execute":"guest-exec","arguments":{"path":"python2","arg":["/usr/bin/kylin-vr.py", "-c", "reload"]}}\''
  return_code = subprocess.call(reload_cmd, shell=True)
  if 0 != return_code:
    print('kylin_vr_reload failed, ret is %d' % return_code)
  else:
    print('kylin vr reload success')


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
  parser.add_argument('-c', '--command', help='sub command', \
        choices=['reload', 'test'], \
        default='reload')
  parser.add_argument('-y', '--yaml', help='specify kylin-vr config yaml. Example: -c reload -y xxx.yaml')
  parser.add_argument('-d', '--domain', help='specify vm uuid. Example: -c reload -d kylin-vr')
  args = parser.parse_args()

  # 加锁保证单例执行
  a = get_lock()

  # ./kylin-vr-ctl.py -y /etc/kylin-vr/kylin-vr.yaml -d b3dcc8bd-616a-35f6-f065-b4a3cd44e940

  cmd = args.command if args.command else 'reload'
  if 'test' == cmd:
    #kylin_vr_reload(args.domain)
    convert_file_2_base64(args.yaml)
  else: # reload
    reload_vr_conf(args.domain, args.yaml)

if __name__ == '__main__':
  main()
