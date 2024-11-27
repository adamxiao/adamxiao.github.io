# docker运行nodejs模拟cgi

创建fakecgi的程序
```
var http = require('http');

var data = {
    test: 'ok'
}

var port = 22345;

http.createServer(function(req, res){
    //console.log(req,res)
    console.log('==> recv req: ' + req.url + '  ===============================================>')
    var body = ""

    console.log('commandpath: ' + req.headers['commandpath'])
    console.log('taskuuid: ' + req.headers['taskuuid'])

    req.on('data', function (chunk) {
        body += chunk;
    });

    req.on('end', function () {
        console.log(body)
        res.end();
    });

    //res.setHeader('ContentType', 'text/json: charset=UTF-8');
    //res.end(JSON.stringify(data));

}).listen(port, function(){
    console.log('listening on', port);
});
```

运行容器
```
docker run -it --rm \
  -v $PWD:/opt/app-root/src -w /opt/app-root/src \
  -p 22345:22345 \
  hub.iefcu.cn/public/node:14 \
  node_fakecgi.js
```

使用curl模拟测试:
```
curl -X POST -H "Content-Type:application/json" -H "commandpath:/path1/xxx/yyy" \
  -d '{"param1": "aaa", "param2": "bbb"}' \
  --retry 5 http://127.0.0.1:22345/test/aaa/bbb
```

## 提供http正向代理url

nodejs实现一个cgi接口，提供如下功能:
- 通过设置http或者socket代理，访问外部的一个http url接口，返回的数据，再返回给客户端
- 如何支持提供多个url地址，分别通过代理，访问不同的目标URL呢


```
const http = require('http');
const https = require('https');
const {HttpsProxyAgent} = require('https-proxy-agent');
const { URL } = require('url');

// 目标URL映射
const targetUrls = {
    '/api/serviceA': 'http://serviceA.example.com',
    '/api/serviceB': 'https://serviceB.example.com'
};

// 代理服务器的信息
const proxy = 'http://10.90.4.100:20172';

// 创建HTTP服务器
const server = http.createServer((req, res) => {
    const path = req.url;
    // 查找匹配的目标URL
    let targetUrl = Object.keys(targetUrls).find(key => path.startsWith(key));

    if (targetUrl) {
        // 构建完整的目标URL
        const fullTargetUrl = new URL(targetUrls[targetUrl]);
        const agent = new HttpsProxyAgent(proxy);

        console.log(req.headers)
        // 配置请求选项
        const options = {
          hostname: fullTargetUrl.hostname,
          port: fullTargetUrl.port || (fullTargetUrl.protocol === 'https:' ? 443 : 80),
          path: fullTargetUrl.pathname + fullTargetUrl.search,
          method: 'GET',
          agent: agent, // 使用代理
        };

        const request = https.request(options, (response) => {
            // 设置响应头
            //console.log(response.headers)
            //response.headers.forEach((value, key) => {
            //    res.setHeader(key, value);
            //});

            // 将响应数据流传递给客户端
            response.pipe(res);
        });

        // 处理请求错误
        request.on('error', (error) => {
            console.error('Request error:', error);
            res.writeHead(500, { 'Content-Type': 'text/plain' });
            res.end('Something went wrong.');
        });

        // 将请求体数据传递给代理请求
        req.pipe(request);
    } else {
        // 如果没有找到匹配的路径，则返回404错误
        res.writeHead(404, { 'Content-Type': 'text/plain' });
        res.end('Not Found');
    }
});

// 监听端口
const PORT = 8080;
server.listen(PORT, () => {
    console.log(`Server is running on port ${PORT}`);
});
```

配置一个nodejs容器运行这个程序
需要构建镜像，安装nodejs的相关模块`npm install http http-proxy http-proxy-agent https-proxy-agent`
```
# 使用官方Node.js镜像作为基础镜像
FROM node:14

# 设置工作目录
WORKDIR /usr/src/app

# 设置 npm 使用国内镜像源
RUN npm config set registry http://mirrors.cloud.tencent.com/npm/

# 将当前目录下的所有文件复制到容器的工作目录
COPY . .

# 安装应用程序依赖
RUN npm install http-proxy

# 暴露应用的服务端口
EXPOSE 8080

# 启动应用
CMD ["node", "index.js"]
```
