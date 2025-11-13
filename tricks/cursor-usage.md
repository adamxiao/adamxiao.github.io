# cursor使用

## 使用经验

### agent写代码 - 实现功能, 解决问题

cursor chat聊天

Ctrl-I打开compose模式?

主动说要做什么
=> 实现一个功能逻辑

- 实现一个功能
- 添加一个参数

- 删除无用的代码
- 去除一些无用的调试日志

- 重构代码?
  更优雅?
  要有合适的功能测试
  cursor: image-tool.py和special.c还有什么地方有优化
  => 优化后有问题，提示跑测试用例不通过，会自己修正 => 就是认为write接口成功返回的是size, 而ufs write接口成功返回是0
- 测试全覆盖?

**难点就是知道要干嘛!**

@image-tool.py 这个脚本有什么可以优化的地方? 有什么潜在的bug需要立即修正?
=> 可维护性增强而已

有些知道怎么做，也要花时间做的,繁杂的，让cursor做很合适
=> 现在花时间的就是，探索要做什么

目前对cursor多次写的代码，可维护性不好感到不满意，觉得应该早些配置rules
=> 毕竟后续修正也费时间呢, 不怎么想做了

建议就是提前准备好测试用例

### cursor tab补全

https://www.youtube.com/watch?v=lypPoT8lZ2M
核心功能: 光标预测

### cursor MCP

https://zhuanlan.zhihu.com/p/1894120179887223638
Cursor+MCP实现用嘴操纵数据库

https://modelscope.cn/mcp
看看有哪些MCP可以用

### cursor rules

https://docs.cursor.com/zh/context/rules
=> 官方文档

- project rules
- user rules
- AGENTS.md

好像可以自然语言描述规则

```
project/
  .cursor/rules/        # 项目范围的规则
  backend/
    server/
      .cursor/rules/    # 后端特定规则
  frontend/
    .cursor/rules/      # 前端特定规则
```

user rules (json_ola@hotmail.com)
=> 云配置, 多处登录都生效
- go语言代码空行不要tab
- 修改代码需要确认
- 不要修改编码格式
- 新增的所有注释使用中文
- Always respond in Chinese-simplified

c++项目规则
生成项目级别的rules：
- 函数的大括号新起一行
- 每行结尾不要有空格或者tab

### cursor index

给文件建立索引

### 其他

了解使用cursor可以做什么事情:
- 轻松开发chrome插件?

https://www.youtube.com/watch?v=a6J2zPH24Ok
5分钟上手AI代码编辑器Cursor，零基础开发Chrome插件 ，从此以后你也是高级程序员了！

https://www.cnblogs.com/echolun/p/18721499
20 分钟高效掌握 cursor

https://www.youtube.com/watch?v=mk05U9iPmxs
Cursor设计者总结的12条高效用法：以及我的实战解读 feat.我写了一本Cursor书 (程序员御风)
=> 还推荐了一个cursor的书

https://www.youtube.com/watch?v=v5uUacAeQtE&ab_channel=%E6%9E%81%E5%AE%A2%E5%8F%B0
全面对比Cursor和Claude Code
=> claude code 命令行工具, 随地使用


## 防火墙放通

看看在限制网络的情况下，放通那些域名，接口，能让cursor正常使用

使用fiddler验证一下?
wireshark抓包看看?
cursor ask这个问题?

gpt: 在一个隔离网络中，如何配置防火墙规则，才让cursor能够正常使用。列举cursor需要使用到的域名端口等信息。

=> 最后配置了`*.cursor.sh`, `cursor.com`验证可以了

- api2.cursor.sh
  开发者模式
  https://api2.cursor.sh/auth/full_stripe_profile

cursor登录
- cursor.com
  => 主页
- authenticator.cursor.sh
  => 跳转到这里登录的

## cursor功能测试

#### 生成带lvm分区的qcow2文件测试

生成一个脚本, 创建一个qcow2文件, 里面存在lvm分区，lvm分区又格式化为ext4文件系统，往里面随便创建一些文件
=> cursor半天没get到我的意思，一直有问题，使用元宝一下子生成了比较正确的脚本(也不太正确)
  => 可能少了关键步骤没有描述，ai不知道怎么做 => 但最终cursor不停的运行检查，不停的修改，还是不行
  => 用cursor的ask写的脚本好像好一点 => 难道背后的模型不一样?
     => 最终成功!

=> 方向要自己把握 => (自己把握方向，再叫ai写可能更快更好)

## FAQ

#### 如何查看auto模式用了哪些模型?

看看用了哪些模型?

能在官网看见消耗和使用什么模型?

#### claude模型限制

https://www.youtube.com/watch?v=77yw6NWaG10
=> 配置http代理，禁用http2

先更新至最新的版本，直接在 文件→首选项→cursor setting找到network，改成 HTTP/1.1 ，代理开全局，重启cursor就可以了

#### cursor sign in 网页登录成功但是不可用

原来是cursor使用了vscode的配置，配置了代理，去除即可

https://blog.csdn.net/IT_Octopus/article/details/145702734

1.cursor 打开开发者模式
=> 发现有报错

2.然后打开设置，去除代理即可

https://kerrynotes.com/cursor-cannot-log-in/
=> 还有文章说要禁用http2, 不知道是否需要

