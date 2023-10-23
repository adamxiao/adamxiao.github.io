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
    console.log(req.url)
    var body = ""

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
