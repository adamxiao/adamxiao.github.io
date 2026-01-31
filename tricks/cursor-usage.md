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

browser-use-MCP-Server

https://juejin.cn/post/7492271292155756583
browser-use 是一个让 AI 操作浏览器的工具。你只需给出指令，AI 就能帮你完成浏览器操作任务。browser-use 官方开发了 mcp-server-browser-use，通过这个 MCP，其他软件也能调用 browser-use 来操作浏览器。下面的画面展示了我在 Cline 中让 AI 打开 Google 并找到 MCP 官网的过程，全程我完全没有操作浏览器，都是AI自主完成的。


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

#### Qoder

[阿里发布国际版AI编程工具Qoder,初版惊喜值得期待](https://www.youtube.com/watch?v=KeqRckq9wyM)
=> 说memory长期? quest mode 先设计文档
=> 没有说repo wiki
[Qoder实测：新项目+老项目双场景，重新认识AI编程](https://www.youtube.com/watch?v=ow-s9dx1xKk)
=> 2:48 有一个repo wiki的后台任务在跑?

- quest mode
  => 多个任务并行执行? => 会有互相影响，虽然可以，但是某些不建议
  先做任务拆解, 确认无误后执行?
- memory => cursor也有的
  项目规划，架构设计, 技术栈选型, 阶段性调整
- repo wiki
  系统总揽，如何上手，核心架构, 还有图示

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

## cursor cli

关键字《cursor cli 怎么做计划》

https://cursor.com/cn/docs/cli/overview

#### 是否有memory? 如何查看

#### 是否共享cursor rules?

## cursor cli分享

- 分享TODO实现 => ok
- 分享模型使用量, 一次消耗多少token => todo
- 先自己写spec，然后让ai写代码，或者spec让ai扩展
  展示经典的历史会话
- ssh分析环境问题
  /data/local/tmp/git2-build => 截图
- 重构代码, 减少代码行数
  python, c++均可
- 建议git保存代码
- 总体架构自己注意把握，或者先问问ai
  我经常问网页版本的ai

https://www.youtube.com/watch?v=sOvi9Iu1Dq8
终端ai优势
- 1.自由度大
  可以调用系统的一切能力
- 2.认知负担最小
  直接说问题，ai解决问题, 不用学习界面操作，直接开始即可
- 3.工具链天然融合
  工作流...

技巧 => 谋，定，动
谋，确定需求; 定，规划清晰路线; 动，快速执行;
=> 将需求文档化, 改需求比后续改代码容易
=> 制定执行计划, 标明哪些任务要先做，哪些可以并行, TODO.md
=> 让ai狂飙，发现跑偏, 也可以随时调整方向

提示词技巧, 把话说清楚, 正面表达, 说要做什么，而不是不要做什么

https://www.youtube.com/watch?v=FwSNWgTnUIQ
markdown to EPUB这个电子书生成skill => 我要to html的吧!

- 考虑让ai写的代码，给它合适的环境测试一下!
  要么ssh，要么本地环境?

- cursor使用问题?
  慢，中断?

- 移动工作目录，或者工作目录改名，cursor还能有这个工作目录的记忆，以及会话吗？

## skills应用

看看有什么好用的skills使用一下
=> 了解这个就是了解ai能帮助我们做一些什么任务, 或者遵守什么流程
  => 例如说markdown 转换为 html, 视频下载, 提取字幕等

我想到的是查uniqb问题的skills，例如开机调度失败，指导查看哪个日志, 等等

https://zhuanlan.zhihu.com/p/1996913009034024863
obra/superpowers - 开发者的"全家桶"

测试和调试类
Systematic Debugging - 结构化调试流程

能干啥：

根本原因分析 → 假设测试 → 解决方案 → 文档记录

obsidian-skills -Obsidian知识库

https://blog.csdn.net/qq_44866828/article/details/156400175
⭐⭐⭐⭐⭐ No.1：PDF（必装中的必装）
能干什么？
猫头虎真实使用场景：
⭐⭐⭐⭐⭐ No.2：skill-creator（神中神）
能干什么？
我怎么用？
⭐⭐⭐⭐ No.3：webapp-testing
能干什么？
使用场景：
⭐⭐⭐⭐ No.4：mcp-builder
能干什么？
⭐⭐⭐ No.5：brand-guidelines
能干什么？

## cursor功能测试

#### 生成带lvm分区的qcow2文件测试

生成一个脚本, 创建一个qcow2文件, 里面存在lvm分区，lvm分区又格式化为ext4文件系统，往里面随便创建一些文件
=> cursor半天没get到我的意思，一直有问题，使用元宝一下子生成了比较正确的脚本(也不太正确)
  => 可能少了关键步骤没有描述，ai不知道怎么做 => 但最终cursor不停的运行检查，不停的修改，还是不行
  => 用cursor的ask写的脚本好像好一点 => 难道背后的模型不一样?
     => 最终成功!

=> 方向要自己把握 => (自己把握方向，再叫ai写可能更快更好)

## claude code使用

https://sites.google.com/view/yueliangxiabanle/windows%E4%B8%8B%E7%94%A8docker-desktop%E8%BF%90%E8%A1%8Cclaude-code%E7%9A%84%E5%AE%8C%E6%95%B4%E6%8C%87%E5%8D%97
旧的安装方式
```
npm install -g @anthropic-ai/claude-code
```

https://help.apiyi.com/claude-code-china-usage-guide.html
中转, vpn, 代理，海外服务器 => API易中转服务

https://easyclaude.com/post/claude-code-comprehensive-guide
Easy Claude Code => api中转

```
# 检查当前配置
cat ~/.claude/config.json

# 如果使用 Easy Claude Code
# 确保配置正确：
{
  "apiKey": "sk-xxxx",  # 从官网获取
  "baseUrl": "https://code.ai2api.dev"
}

# 测试连接
claude
```

https://www.cnblogs.com/wh2005/p/18984584
=> 或者环境变量?
```
# 设置环境变量（替换为你的API KEY）
ANTHROPIC_AUTH_TOKEN=sk-PxD3240xxxmCFM3
#ANTHROPIC_API_KEY=sk-PxD3240xxxmCFM3
ANTHROPIC_BASE_URL=https://anyrouter.top
```

https://devstation.connect.huaweicloud.com/space/devportal/casecenter/b7663af9fcd74623bd36307f5f817f3d/1
1.4 配置大模型KAT-Coder
```
echo 'export ANTHROPIC_BASE_URL="https://wanqing.streamlakeapi.com/api/gateway/v1/endpoints/ep-xxx-xxx/claude-code-proxy"' >> ~/.bash_profile
echo "export ANTHROPIC_AUTH_TOKEN='YOUR_WANQING_API_KEY'" >> ~/.bash_profile
echo 'export ANTHROPIC_MODEL="KAT-Coder"' >> ~/.bash_profile
echo 'export ANTHROPIC_SMALL_FAST_MODEL="KAT-Coder"' >> ~/.bash_profile
source ~/.bash_profile
```

## FAQ

#### AGENTS.md 规范

https://jimmysong.io/zh/book/ai-handbook/sdd/agents/

#### cursor感觉比较慢

https://blog.yasking.org/a/1765505478.html
Cursor 巨慢到一定程度，17:45 提交的任务，18:21 还在 “吭哧瘪肚” 的输出。
=> 重建下索引试试，然后问题就这样解决了?

https://blog.csdn.net/qq_39632646/article/details/151580966
模型/路由、网络/代理、扩展冲突、索引/缓存、项目体量与上下文边界。

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

