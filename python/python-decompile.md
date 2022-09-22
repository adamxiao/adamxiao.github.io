# python pyc反编译

使用uncompyle
https://blog.csdn.net/lclfans1983/article/details/107255346

```bash
# Uncompyle6安装, 使用python3.5的镜像安装使用 (使用其他环境遇到了一些问题)
docker run -it --network host --rm -v $HOME/Downloads:/data -w /data python:3.5 bash

git clone https://github.com/rocky/python-uncompyle6.git
git checkout python-3.3-to-3.5
python3 setup.py install

# 2.2反编译
uncompyle6 -o . *.pyc
=> 报错, 没有验证成功, ImportError: No module named 'importlib.metadata'

直接使用pip进行安装
pip install uncompyle6
=> 验证反编译成功
```

关键字`python 反编译`                                                                                                                                                                                              到这个网站去在线反编译
https://tool.lu/pyc/

=> 10分钟使用一次，而且有些还无法反编译出来
