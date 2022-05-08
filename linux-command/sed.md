# sed使用

#### sed插入多行到文件

关键字《sed 添加多行》

参考: https://blog.csdn.net/yibeijiu9/article/details/105560964

首先写一个测试的文件test.txt
```bash
echo -e "1\n2\n3\n4\n5" > test.txt

cat test.txt 
1
2
3
4
5
```

然后插入多行, 创建脚本test.sh并运行
```bash
#!/bin/bash
line1=1
line2=2
line3=3
sed -i '/2/i\
insert '$line1' line\
insert '$line2' line\
insert '$line3' line
' test.txt
```
