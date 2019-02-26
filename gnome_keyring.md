# gnome-keyring使用
https://support.wandisco.com/index.php?/Knowledgebase/Article/View/362/0/how-to-setup-encrypted-svn-password-storage-using-gnome-keyring-in-an-ssh-session
http://blogs.collab.net/subversion/subversion-16-security-improvements#.WDAapnV948p

https://wiki.archlinux.org/index.php/GNOME/Keyring#Use_Without_GNOME

0. svn支持gnome-keyring
http://share.weiyun.com/85c1770c5322487305b4a5ee0760d5f5

1. gck库
http://archive.ubuntu.com/ubuntu/pool/main/g/gcr/gcr_3.10.1.orig.tar.xz

1. seahorse
查看保存的key

2. svn支持gnome-keyring
`sudo apt-get install libsvn-auth-gnome-keyring`

3. 启动gnome-keyring
```bash
eval `dbus-launch --sh-syntax`
export `gnome-keyring-daemon`

export $(nohup gnome-keyring-daemon 2>/dev/null)
The output that gets sent to export looks something like this:

GNOME_KEYRING_SOCKET=/tmp/keyring-OpuUEI/socket
GNOME_KEYRING_PID=9256
```

4. 停止gnome-keyring
```
kill $DBUS_SESSION_BUS_PID > /dev/null 2>&1

killall dbus-daemon
killall gnome-keyring-daemon
```
