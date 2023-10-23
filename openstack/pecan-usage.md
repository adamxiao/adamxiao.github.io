# pecan框架使用

关键字《pecan框架使用》

https://yangsijie666.github.io/2018/08/15/Pecan%E6%A1%86%E6%9E%B6/
```
在RootController类中，一般会写上如下的代码：

from pecan import rest
import pecan


class RootController(rest.RestController):
    
    @pecan.expose()
    def get(self):
        return 'This is RootController GET.'
当存在以上代码时，使用以下命令调用就会有返回值：

curl -X GET http://127.0.0.1:8080
返回值为:

This is RootController GET.
```
