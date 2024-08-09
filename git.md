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

https://www.npmjs.com/package/git-alias
有更多的alias可以参考使用
```
lg                      log --stat --color
lgg                     log --graph --color
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
# 比较两个分支的差异, 挺好用的
git log --graph --decorate --oneline --simplify-by-decoration 2dae956539..a5f51f8772
```

* git show merge commits
  git merge show branch commits
方法1：使用 git log 显示合并分支的提交
例如，如果你已经将 feature-branch 合并到 main，并且想查看合并过程中包含的所有提交，可以这样做：
```
git log main..feature-branch
=> 我的环境, 需要填真实的commit id
```
方法2:
```
git diff --name-only main..feature-branch
```
feature-branch还没有merge呢
方法1:
方法2：使用 git log 的对比选项
你也可以使用 --left-right 选项来区分哪些提交在 feature-branch，哪些在 main 中：
```
git log --left-right --graph --oneline main...feature-branch
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

#### git generate patch

制作rpm的补丁方法
```
1.git config --global user.email "xxx@kylinos.com.cn"　
2.git config --global user.name "xxx"
3.rpmbuild -bp　“rpm包spec文件”
4.git init --初始化git
5.git add -A　和　git commit -m "git base" --建立备份（对比）文件
6.git checkout -b fixed --创建并切换至新分支fixed
7.进行内容修改，修改后再次使用git add和git commit -m "补丁名称"
8.git format-patch -M master --生成补丁
```

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

#### write error: Bad file descriptor

最后strace验证发现是write报错，文件系统是ubuntu 20.04 nfs 4.2挂载truenas scale 22.12.0导致的!!!

```
$ git gc
Enumerating objects: 275105, done.
Counting objects: 100% (275105/275105), done.
Delta compression using up to 12 threads
Compressing objects: 100% (64709/64709), done.
fatal: sha1 file '.git/objects/pack/tmp_pack_kgSgPZ' write error: Bad file descriptor
fatal: failed to run repack
```

```
$ git fetch module
remote: Enumerating objects: 1711, done.
remote: Counting objects: 100% (1010/1010), done.
remote: Compressing objects: 100% (18/18), done.
fatal: write error: Bad file descriptor.00 KiB | 20.00 KiB/s
fatal: index-pack failed
```

https://stackoverflow.com/questions/18563246/git-gc-error-failed-to-run-repack-message
=> 验证可以
```
git gc --aggressive --prune=now
```

https://stackoverflow.com/questions/67820763/loose-object-file-bad-file-descriptor-while-doing-git-pull
```
git config core.fsyncObjectFiles false
```

gpt关键字《git fetch write error: Bad file descriptor》
```
GIT_TRACE_PACKET=1 GIT_TRACE=1 GIT_CURL_VERBOSE=1 git fetch module
```

#### git pull: The requested URL returned error: 503

git clone http://gitlab.iefcu.cn/openstack/devstack.git

抓包发现没有80端口的包
原来是开了代理, 代理访问不到这个git仓库
