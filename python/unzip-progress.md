# unzip显示进度

思路:
- 解压接口本身能获取进度
- 根据已解压的文件大小来判断
- 7z命令行解压能获取到进度
  7z x xxx.gvm
  `7za -bsp1 x ../adam.zip | tee adam.txt`
  => stdout console才会有进度。

关键字《python zipfile获取进度》

https://www.twblogs.net/a/5b8e9fe82b71771883468413/?lang=zh-cn
【例子】实时显示解压进度
针对zip文件的解压缩使用zipfile.ZipFile()方法，但是ZipFile()方法不支持回调函数，只能考虑逐文件解压，将tqdm()包装到迭代器上。

可以用ZipFile.namelist()返回整个压缩文件的名字列表，然后逐个解压。
```
if not isdir('dir_path'):
    with ZipFile('imgs.zip', 'r') as zipf:   
        for name in tqdm(zipf.namelist()[:1000],desc='Extract files', unit='files'):
            zipf.extract(name, path='dir_path')
        zipf.close()
```
=> 按文件数量解压显示进度, 可能不是很合适

逐文件解压会增加解压时间：
同样解压10000张图片，zipf.extractall()方法耗时 8.81s；上述方法耗时 9.86s，多花时间 12%。

https://learn.fuming.site/python/python-basic/常用模块-系统交互.html
```
# 解压
t=tarfile.open('/tmp/data.tar','r')
t.extractall('/users/dandan')
t.close()
```

https://docs.python.org/zh-cn/3/library/tarfile.html

7z可能有进度?

https://www.cnblogs.com/huzhongqiang/p/17709965.html
```
from tqdm import tqdm
import zipfile

def unzip(zipFile):
    '''把ZIP文件解压到以文件名命名的目录中'''
    # 获得文件名(不含后缀)，作为解压缩的目录
    dir_name = os.path.dirname(zipFile) # 获取zip文件所在的目录名
    filename = os.path.basename(zipFile)    # 获取zip文件名, 形如: xxx.zip
    name, ext = os.path.splitext(filename) # 分离文件名和后缀
    target_path = os.path.join(dir_name, name) # 设置解压的目标目录
    with zipfile.ZipFile(zipFile) as zf:
        for member in tqdm(zf.infolist(), desc='Extracting '):
            try: zf.extract(member, target_path)
            except zipfile.error as e: raise Exception(f'20211018_1547: 解压缩出现错误.')
```

https://www.cnblogs.com/danhuai/p/15778172.html
```
import zipfile
def read_zip(zip_file_path: str, unpack_path: str, ws_msg: WebSocketMsg):
    """
    解压ZIP文件
    @param zip_file_path: ZIP文件路径（ex. E:\aaa\a.zip）
    @param unpack_path: 解压文件输出路径（ex. E:\aaa）
    @param ws_msg: 用来放实时进度的类（可干掉）
    """

    file_list = zipfile.ZipFile(zip_file_path)
    info = file_list.infolist()

    ''' 1 计算解压后的文件总大小（单位：字节B） '''
    all_size = 0
    for i in info:
        all_size += i.file_size
    # 1.1 字节B转换为兆字节MB （字符串）
    all_size_str = str(int(all_size / 1024 / 1024)) + 'MB'

    ''' 2 当前已解压的文件总大小（单位：字节B） '''
    now_size = 0
    for i in info:
        file_list.extract(i, unpack_path)
        now_size += i.file_size
        # 2.1 字节B转换为兆字节MB （字符串）
        now_size_str = str(int(now_size / 1024 / 1024)) + 'MB'
        ws_msg.msg.append(f'解压进度：{int(now_size / all_size * 100)}% ({now_size_str}/{all_size_str})')
        # print(f'解压进度：{int(now_size / all_size * 100)}% ({now_size_str}/{all_size_str})')
    file_list.close()
```

#### 7z解压zip文件获取进度

关键字《7z 解压获取进度》

https://ningto.com/post/34898D06EC5D0E3FD13FA80037FDBF13
通过获取输出进度得到

https://www.cnblogs.com/zhb2020/p/4569932.html
7z 压缩类 进度条 回调函数
首先去7z官网下载代码 7z的源代码或者lzma都可以，但是推荐下7z的源代码，里面东西比较全

## ova镜像解压进度

=> 验证使用7za也是可以的!

https://support.huaweicloud.com/ims_faq/ims_faq_0043.html
file命令查看
MyVm.ova: POSIX tar archive (GNU)
