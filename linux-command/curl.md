# curl 使用

命令行发送http请

#### curl使用sock代理
```bash
curl -x socks5://127.0.0.1:20170 google.com
```

#### 1.显示内容包含返回的http头
```
curl -i xxx
```

#### 2.使用HEAD方法仅仅返回http头
```bash
curl -I xxx
```

#### 3.指定ip和端口
```bash
curl -x 123.45.67.89:1080 xxx
```
#### 4.输出内容存到文件中
```bash
curl -o xxx
```
#### 5.存储返回http头到文件中去
```bash
curl -D @file xxx
```
#### 6.请求头指定cookie文件
```bash
curl -b @cookiefile xxx
```
#### 7.自定义请求头的User-Agent(浏览器信息)
```bash
curl -A "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.0)" xxx
```

#### 用curl模拟浏览器发送请求
```bash
curl -v -o page.html -D cookie0002.txt -b cookie0001.txt -A "Mozilla/5.0 (X11; U; Linux i686; zh-CN; rv:1.9.2.13) Gecko/20101206 Ubuntu/10.04 (lucid) Firefox/3.6.13" -e www.baidu.com -H "Content-Type: application/x-www-form-urlencoded" -d "username=xxx&password=xxx"
//www.baidu.com
```
