# golang使用

golang 1.16容器编译golang项目
```
go mod download
go mod vendor # 会在本地构建一个vendor目录, 放置依赖库
go build .
```

#### go mod使用

```
export GOPROXY=https://mirrors.aliyun.com/goproxy
export GOPROXY=https://goproxy.cn,direct
```

初始化创建go.mod文件
```
go mod init xxx
```

增加依赖库
```
go get github.com/gin-gonic/gin
```

会在本地构建一个vendor目录, 放置依赖库
```
go mod vendor
```

获取所有子模块
```
go mod tidy
```

文件解析
- go.sum
- go.mod

go.mod 映射本地目录库
https://blog.csdn.net/qq_32439305/article/details/121425153
```
replace golang.zx2c4.com/wireguard => /home/adam/workspaces/tmp/wireguard-go.new/
```

[Go Module 工程化实践（二）：go get 取包原理篇](https://studygolang.com/articles/18726)

## 其他

[Go socket编程](https://www.cnblogs.com/Yunya-Cnblogs/p/13815864.html)
