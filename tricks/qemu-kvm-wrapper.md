# qemu-kvm的包装脚本

```python
#!/usr/bin/env python

import sys
import logging
import subprocess

# filename='/var/log/adam.log',
logging.basicConfig(level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


# del sys.argv[0]
# for i in range(len(sys.argv)):
	# logging.info(sys.argv[i])

cmd='echo org_ocfs2_tunefs_size.pyc ' + ' '.join(sys.argv)
logging.info(cmd)
# sys.argv[0] = 'org_ocfs2_tunefs_size.pyc'
sys.argv[0] = 'echo'
subprocess.check_call(sys.argv)
```

某些场景下使用execv更合适
```
#!/usr/bin/env python

import sys
import logging
import subprocess
import os

# filename='/var/log/adam.log',
logging.basicConfig(level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

for i in range(len(sys.argv)):
    logging.info(sys.argv[i])
    if 'virtio-blk-pci,drive=virtio0-hd2,bus=pci.0' == sys.argv[i]:
        sys.argv[i] = 'virtio-blk-pci,drive=virtio0-hd2,bus=pcie.0'

# sys.argv.append("-no-shutdown") # add param

cmd=' '.join(sys.argv)
logging.info(cmd)
sys.argv[0] = '/usr/libexec/qemu-kvm.1127'
os.execv(sys.argv[0], sys.argv)
```

例如，直接给qemu添加串口参数，记录串口日志
```
sys.argv.append("-chardev")
sys.argv.append("socket,id=charserial0,host=0.0.0.0,port=38443,server,nowait,logfile=/tmp/console.log,logappend=on")
sys.argv.append("-device")
sys.argv.append("isa-serial,chardev=charserial0,id=serial0")

for i in range(len(sys.argv)):
    logging.info(sys.argv[i])
    if '-boot' == sys.argv[i]:
        sys.argv[i+1] = 'c,menu=on,splash=/usr/lib/ksvd/etc/bootsplash.jpg,splash-time=800,strict=on'
    if '-serial' == sys.argv[i]:
        sys.argv[i] = '-chardev'
        sys.argv[i+1] = 'socket,id=charserial0,host=0.0.0.0,port=38443,server,nowait,logfile=/tmp/console.log,logappend=on'
        sys.argv.insert(i+2, "-device")
        sys.argv.insert(i+3, "isa-serial,chardev=charserial0,id=serial0")
```
