# git usage
## git data flow
```sequence
Working directory->Index(cache): git add
Index(cache)->Local repository: git commit
Local repository->Remote repository: git push
Remote repository->Local repository: git fetch
Local repository->Working directory: git checkout [HEAD]
Remote repository->Working directory: git pull
Remote repository->Local repository: git pull
```

## git configure

### user info
```ini
[user]
    name = Adam Xiao
    email = iefcuxy@gmail.com
```

### alias
```ini
[alias]
    st = !git status -s
    co = !git checkout
    ci = !git commit
    di = !git difftool -t vimdiff
```

### other
代理地址，推送远端仓库规则等
```ini
[https]
    proxy = http://dev-proxy.oa.com:8080
[http]
    proxy = http://dev-proxy.oa.com:8080
[push]
    default = simple
```