# deepseek ai使用

[DeepSeek的API，我们普通人都能用在哪？](https://zhuanlan.zhihu.com/p/20482196795)

- 1.浏览器插件
  eg. 沉浸式翻译插件

- 3.AI脑暴会
  可以实现多个AI就一个议题进行多轮讨论，并在讨论中延伸出新的观点。
  https://zhuanlan.zhihu.com/p/20622135121


https://github.com/LLM-Red-Team/deepseek-free-api

https://github.com/reorx/awesome-chatgpt-api/blob/master/README.cn.md
CR.GPT
由ChatGPT驱动的代码审查机器人

AI Shell
将自然语言转换为shell命令的CLI。受Github Copilot X CLI的启发，对所有人开放源代码。

一些应用场景
https://deepseek.csdn.net/67abf75e82931a478c54afa8.html

- 代码开发
- 多语言翻译
- 企业客服

## 使用api入门

[创建你的第一个使用 OpenAI ChatGPT API 的程序](https://linux.cn/article-15865-1.html)



使用curl
使用python
使用nodejs

## 本地模型部署使用

使用ollama部署运行容器
```
curl -fsSL https://ollama.com/install.sh | sh
ollama run deepseek-r1:7b  # 自动下载并启动。
```

https://www.cnblogs.com/qubernet/p/18702147
=> 可以通过浏览器插件, 或者部署web ui服务，在web访问本地模型

#### Dify本地知识库

```
git clone https://github.com/langgenius/dify.git
```

## ai应用场景思考

邮件自动归类?

手机上，存储ai处理，清理照片，app等

浏览器插件，扫描wiki数据, 做本地知识库

微信小程序，获取聊天记录，总结整理等?
