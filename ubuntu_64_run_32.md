# ubuntu 16.04 x86_64运行32位程序

以前据说装这个包就行了，现在不行了
`sudo apt-get install ia32-libs`

```bash
sudo apt install lib32ncurses5 lib32z1
sudo dpkg --add-architecture i386
sudo apt-get install libc6:i386 libstdc++6:i386
sudo apt-get install libstdc++6-dev:i386
```

# ubuntu 16.04 x86_64编译出32位程序
```bash
sudo apt-get install g++-multilib # 这样才能g++ -m32
# 其他i386 dev库
sudo apt-get install zlib1g-dev:i386 libevent-dev
```
