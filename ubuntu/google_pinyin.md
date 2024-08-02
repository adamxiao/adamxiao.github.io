# install google-pinyin

```
apt-get install fcitx-googlepinyin
im-config # config use google-pinyin
```

## FAQ

#### ubuntu 24.04安装某些软件包后无法使用fcitx

默认变为ibus了
需要如下脚本, 然后在用户登录页面选择使用x11,再进入wayland即可

/etc/X11/Xsession.d/70im-config_launch

```
# If already tweaked, keep hands off :-)
# If im-config is removed but not purged, keep hands off :-)
#if [ -z "$XMODIFIERS" ] && \
#   [ -z "$GTK_IM_MODULE" ] && \
#   [ -z "$QT_IM_MODULE" ] && \
#   [ -z "$CLUTTER_IM_MODULE" ] && \
#   [ -z "$SDL_IM_MODULE" ] && \
if   [ -r /usr/share/im-config/xinputrc.common ]; then
```
