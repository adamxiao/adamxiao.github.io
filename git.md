# git usage

## git tutorial

```
man gittutorial
```

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

## git workflow

1. github workflow

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
	;proxy = sock5h://dev-proxy.oa.com:8080
[http]
    proxy = http://dev-proxy.oa.com:8080
	;proxy = sock5h://dev-proxy.oa.com:8080
[push]
    default = simple
```

ssh协议代理, 配置~/.ssh/config配置文件
```
Host github.com *.github.com
    User git
    # SSH默认端口22， HTTPS默认端口443
    Port 22
    Hostname %h
    # 这里放你的SSH私钥
    IdentityFile ~/.ssh/id_rsa
    # 设置代理, 127.0.0.1:10808 换成你自己代理软件监听的本地地址
    # HTTPS使用-H，SOCKS使用-S
    #ProxyCommand connect -S proxy.iefcu.cn:20170 %h %p
    ProxyCommand nc -v -x proxy.iefcu.cn:20170 %h %p
```

## git FAQ

1. cancel a local git commit
git reset --hard HEAD~1
git reset --soft HEAD~1

2. sync fork repo
git remote add upstream git://org.xxx.git
git fetch upstream
git merge upstream/master

3. git revert remote commit
https://www.bynicolas.com/code/git-revert-commit-already-pushed-remote-repository/

4. git change commit message
git commit --amend

5. on-my-zsh git hi
https://stackoverflow.com/questions/12765344/oh-my-zsh-slow-but-only-for-certain-git-repo
git config --add oh-my-zsh.hide-dirty 1

6. git branch fork log
git log --graph --decorate --oneline --simplify-by-decoration --all

7. git offline repo sync
refer: http://juanmanueldehoyos.com/synchronize-git-repositories-offline-with-bundle/
```bash
git bundle create ../mybundle.gitbundle f8469b7a4b..develop
git bundle verify ../mybundle.gitbundle
git pull mybundle.gitbundle develop develop
```

8. git status 中文文件名乱码
```
git config --global core.quotepath false
```

9. git 提交到新的分支
git push --set-upstream origin 8.1.7-24436

10. git log(docker) 中文commit乱码
```
git config --global i18n.commitencoding utf-8
git config --global i18n.logoutputencoding utf-8
export LESSCHARSET=utf-8
```

11. git run command for each submodule
```
git submodule foreach 'git log --pretty=format:"%h%x09%an%x09%ad%x09%s" @{u}..HEAD'
git submodule foreach 'git status -s'
```

12. git query push upstream
https://git-scm.com/book/en/v2/Git-Basics-Working-with-Remotes
```
git remote show origin
```

13. git cherry-pick
```
git cherry-pick <HashA> <HashB>
git cherry-pick A..B
git cherry-pick A^..B
```

14. git checkout previous branch
git checkout -
git checkout @{-1}

#### git project migrate

关键字[git project offline migrate]

https://gitenterprise.me/2016/03/30/how-to-migrate-a-git-repository/

* Step 1 – Mirror clone
  `git clone --mirror ssh://myuser@gitent-scm.com/git/myorg/myrepo.git`
* Step 2 – Create empty repo on the new Git Server
* Step 3 – Push to the new Git Server
  `git push --mirror git@github.myorg/myrepo.git`
* Step 4 – Import into GerritHub.io (Optional)

## FAQ

#### git pull: The requested URL returned error: 503

git clone http://gitlab.iefcu.cn/openstack/devstack.git

抓包发现没有80端口的包
原来是开了代理, 代理访问不到这个git仓库
