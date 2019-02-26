var http = require('http');

var data = {
    test: 'ok'
}

var port = 22345;

http.createServer(function(req, res){

    res.setHeader('ContentType', 'text/json: charset=UTF-8');
    res.end(JSON.stringify(data));

}).listen(port, function(){
    console.log('listening on', port);
});
