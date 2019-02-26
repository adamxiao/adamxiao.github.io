# gollum 安装使用
参考gollum github地址
<https://github.com/gollum/gollum>

## 1. 安装要求
使用ubuntu 16.04安装，ubuntu 14.04不满足ruby一些条件
通过Gem安装 gollum
```bash
sudo gem install gollum
# http代理安装方法 sudo gem install --http-proxy http://dev-proxy.oa.com:8080 gollum
gollum --v
```
### 遇到的依赖问题依次解决
```bash
sudo apt-get install ruby ruby-dev make zlib1g-dev libicu-dev build-essential git
```

## 2. 创建自己的wiki系统
```bash
mkdir wiki
cd wiki
git init
gollum
```

成功创建http服务器如下：
```
WEBrick::HTTPServer#start: pid=24323 port=4567
```

使用浏览器访问
```
http://localhost:4567/
```

## 使用技巧
- 实时编辑预览
```
gollum --live-preview
```
- 作为服务自动启动, 参考<https://github.com/gollum/gollum/wiki/Gollum-as-a-service>
使用systemd系统，创建`gollum.service`文件
```
ExecStart=/usr/local/bin/gollum --live-preview "/home/adam/adam_wiki.wiki/"
```
然后注册启动gollum服务
```
sudo systemctl enable gollum.service
sudo systemctl start gollum.service
sudo service gollum start
```
- 自定义css

## 3. FAQ

### 1. gollum中文问题解决
refer to  <https://github.com/gollum/gollum/issues/843>

1. $ gem env ,  找到你的gem  安装目录, 

2. 进入到 gitlab-grit目录中.
```bash
$ cd /var/lib/gems/2.3.0/gems/gitlab-grit-2.8.1
```

3. vim lib/grit/index.rb,  176行左右, 做如下修改:
```ruby
#        tree_contents[k] = "%s %s\0%s" % [tmode, obj.name, sha]
        tree_contents[k] = "%s %s\0%s" % [tmode, obj.name.force_encoding('ASCII-8BIT'), sha]
```

### 遗留问题
- 创建`_Sidebar.md`文件, 测试失败
- 展示和github wiki不一样，识别markdown有点问题
