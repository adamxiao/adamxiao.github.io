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
