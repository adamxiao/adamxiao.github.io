# 中文乱码gbk问题

对GBK，GB2312，GB18030字符集的支持

#### GB 2312

GB 2312 标准由中国国家标准总局 1980 年发布，GB 即国标，共收录 6763 个汉字，其中一级汉字 3755 个，二级汉字 3008 个。
对于人名、古汉语等方面出现的罕用字，GB 2312 不能处理，这导致了后来 GBK 及 GB 18030 汉字字符集的出现。
GB 2312 兼容 ASCII 码（0 - 127），之后对任意一个图形字符都采用两个字节表示，高位字节和低位字节都大于127。

#### Big5

Big5，大五码，台湾地区繁体中文标准字符集，采用双字节编码，共收录 13053 个中文字，于 1984 年实施。

Big5 码是一套双字节字符集，使用了双八码存储方法，以两个字节来安放一个字。第一个字节称为“高位字节”，第二个字节称为“低位字节”。
“高位字节”使用了 0x81-0xFE，“低位字节”使用了 0x40-0x7E，及 0xA1-0xFE。


#### GBK

=> 特别不一样?

于 1995 年 12 月发布的汉字编码国家标准。

GBK 共收录 21886 个汉字和图形字符
GB2312 中的全部汉字（ 6763 个）、非汉字符号
Big5 中的全部汉字
与 ISO 10646 相应的国家标准 GB 13000 中的其他 CJK（中日韩） 汉字
其他汉字、部首、符号，共计 984 个

GBK 采用双字节表示，总体编码范围为 8140-FEFE 之间，首字节在 81-FE 之间，尾字节在 40-FE 之间，不再规定低位字节大于 127，剔除 XX7F 一条线。

#### GB 18030

GB 18030，国家标准 GB 18030-2005，是中国目前最新的内码字集，于 2000 年 3 月发布的汉字编码国家标准，与 GB 2312-1980 和 GBK 兼容，共收录汉字 70244 个

GB 18030 编码是一二四字节变长编码
单字节，其值从 0 到 0x7F，与 ASCII 码兼容
双字节，第一个字节的值从 0x81 到 0xFE，第二个字节的值从 0x40 到 0xFE（不包括 0x7F），与 GBK 标准兼容
四字节，第一个字节的值从 0x81 到 0xFE，第二个字节的值从 0x30 到 0x39，第三个字节从0x81 到 0xFE，第四个字节从 0x30 到 0x39。

## 乱码案例

#### ftp服务器文件名中文乱码


只有windows 10出现?
```
云计算.pdf => 算和.会乱码
初稿.doc => 稿和.会乱码?
分布.doc => 布和.会乱码?
```

#### 参考

- [GBK 编码表](https://toolhelper.cn/Encoding/GBK)
