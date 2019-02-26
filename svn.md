# svn usage
## svn data flow
```{mermaid}
sequenceDiagram
    Working directory->>Remote repository: svn commit
    Remote repository->>Working directory: svn update
```

## 1. svn configure
### auth
配置gnome-keyring存储密码
```ini
[auth]
password-stores = gnome-keyring
store-passwords = yes
store-auth-creds = yes
```

### tunnel
支持ssh协议访问svn
```ini
[tunnels]
ssh = ssh -i /data/adamxiao/.ssh/adam -p 22 -q
```

### other
```ini
[helpers]
editor-cmd = vi
diff-cmd = /data/adamxiao/bin/diffwrap.sh # vimdiff比较svn 版本差异
```
```ini
[miscellany]
global-ignores = *.o *.lo *.la *.al .libs *.so *.so.[0-9]* *.a *.pyc *.pyo \
                 work.vim .obj tags
no-unlock = yes # 不自动释放锁

enable-auto-props = yes
[auto-props]
* = svn:needs-lock=native # 新增文件自动加只读属性
```

## 2. svn cmd

### local
```bash
svn add [FILE]
svn add [DIR]
svn mv [FILE] [FILE]

svn commit -m "commit" [FILE]
svn checkout [FILE]

svn diff [FILE]
svn info [FILE]

svn lock [FILE]
svn unlock [FILE]

svn log [FILE]
svn ls [DIR]
svn relocate
svn resolved
svn revert
svn rm
svn status
svn svn
svn unlock
svn up
```
