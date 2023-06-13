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
    proxy = http://proxy.iefcu.cn:20172
	;proxy = sock5h://proxy.iefcu.cn:20172
[http]
    proxy = http://proxy.iefcu.cn:20172
	;proxy = sock5h://proxy.iefcu.cn:20172
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

* cancel a local git commit

```
git reset --hard HEAD~1
git reset --soft HEAD~1
```

* sync fork repo

```
git remote add upstream git://org.xxx.git
git fetch upstream
git merge upstream/master
```

* git revert remote commit

https://www.bynicolas.com/code/git-revert-commit-already-pushed-remote-repository/

* git change commit message

```
git commit --amend
```

* on-my-zsh git hi

https://stackoverflow.com/questions/12765344/oh-my-zsh-slow-but-only-for-certain-git-repo
```
git config --add oh-my-zsh.hide-dirty 1
```

* git branch fork log

```
git log --graph --decorate --oneline --simplify-by-decoration --all
```

* git offline repo sync

refer: http://juanmanueldehoyos.com/synchronize-git-repositories-offline-with-bundle/
```bash
git bundle create ../mybundle.gitbundle f8469b7a4b..develop
git bundle verify ../mybundle.gitbundle
git pull mybundle.gitbundle develop develop
```

* git status 中文文件名乱码

```
git config --global core.quotepath false
```

* git 提交到新的分支

```
git push --set-upstream origin 8.1.7-24436
```

* git log(docker) 中文commit乱码

```
git config --global i18n.commitencoding utf-8
git config --global i18n.logoutputencoding utf-8
export LESSCHARSET=utf-8
```

* git run command for each submodule

```
git submodule foreach 'git log --pretty=format:"%h%x09%an%x09%ad%x09%s" @{u}..HEAD'
git submodule foreach 'git status -s'
```

* git query push upstream

https://git-scm.com/book/en/v2/Git-Basics-Working-with-Remotes
```
git remote show origin
```

* git cherry-pick

```
git cherry-pick <HashA> <HashB>
git cherry-pick A..B
git cherry-pick A^..B
```

* git checkout previous branch

```
git checkout -
git checkout @{-1}
```

* git push origin tag_name

#### git project migrate

关键字`git project offline migrate`

https://gitenterprise.me/2016/03/30/how-to-migrate-a-git-repository/

* Step 1 – Mirror clone
  `git clone --mirror ssh://myuser@gitent-scm.com/git/myorg/myrepo.git`
* Step 2 – Create empty repo on the new Git Server
* Step 3 – Push to the new Git Server
  `git push --mirror git@github.myorg/myrepo.git`
* Step 4 – Import into GerritHub.io (Optional)

或者clone和push, 这样只能迁移代码.
```
git clone xxx
git branch -a  | grep remote | awk '{print $1}' |sed -e 's#remotes/origin/##'  | grep -v HEAD |xargs -I % git co %
git remote add new xxx
git push -u new --all
git push -u new --tags
```

## ~/.gitconfig example

```
[user]
    name = Adam Xiao
    email = iefcuxy@gmail.com
[alias]
    st = !git status -s
    co = !git checkout
    ci = !git commit
    di = !git difftool -t vimdiff
[https]
#       proxy = http://127.0.0.1:20172
[http]
#       proxy = http://127.0.0.1:20172
[pull]
        rebase = false
[push]
        default = simple
[i18n]
    commitencoding = utf-8
    logoutputencoding = utf-8
[core]
    quotepath = false
```

## FAQ

#### git pull: The requested URL returned error: 503

git clone http://gitlab.iefcu.cn/openstack/devstack.git

抓包发现没有80端口的包
原来是开了代理, 代理访问不到这个git仓库
