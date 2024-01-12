# gtk clipboard使用

- 剪切板
- clipboard
- gnome gtk

https://github.com/bstpierre/gtk-examples/blob/master/c/clipboard_watch.c
监听剪切版本变化的示例代码
```
// This example demonstrates monitoring the clipboard for changes in
// ownership.
//
// There is no "main window". This program prints the contents of the
// clipboard to stdout whenever the clipboard owner changes. Exit with
// Ctrl-C.
//
// For more info on the X11 clipboard, see:
//
//     http://www.jwz.org/doc/x-cut-and-paste.html
//

#include <gdk/gdk.h>
#include <gtk/gtk.h>

// This callback is invoked when the clipboard owner changes.
void handle_owner_change(GtkClipboard *clipboard,
                         GdkEvent *event,
                         gpointer data)
{
    // Avoid 'unused arg' warnings.
    (void)event;
    (void)data;

    // Get the selected text from the clipboard; note that we could
    // get back NULL if the clipboard is empty or does not contain
    // text.
    char* text = gtk_clipboard_wait_for_text(clipboard);
    if(text)
    {
        printf("%s\n", text);
    }
}

int main(int argc, char** argv)
{
    // Standard boilerplate: initialize the toolkit.
    gtk_init(&argc, &argv);

    // Get a handle to the given clipboard. You can also ask for
    // GDK_SELECTION_PRIMARY (the X "primary selection") or
    // GDK_SELECTION_SECONDARY.
    GtkClipboard* clipboard = gtk_clipboard_get(GDK_SELECTION_PRIMARY);

    // Connect to the "owner-change" signal which means that ownership
    // of the X clipboard has changed.
    g_signal_connect(clipboard, "owner-change",
                     G_CALLBACK(handle_owner_change), NULL);

    // Run the GTK main loop so that we get the owner-change signal
    // until the user kills the program (^C).
    gtk_main();

    return 0;
}
```

## python 监听gtk 剪切板

https://hicham.fedorapeople.org/gi/python/Gtk-3.0.html#Gtk.Clipboard

```
#!/usr/bin/python3 -t
# -*- coding:utf-8 -*-

from gi.repository import Gtk, Gdk
import signal

def test(*args):
  clip = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
  data = clip.wait_for_text()
  print(data)

def main():
  clip = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
  clip.connect('owner-change',test)
  signal.signal(signal.SIGINT, signal.SIG_DFL)

  Gtk.main()

if __name__ == '__main__':
  main()
```

关键字《python gtk clipboard owner-change》

https://unix.stackexchange.com/questions/399914/dump-clipboard-to-stdout-in-follow-mode-for-piping
```
#!/usr/bin/env python
import sys 
import signal
import gi
gi.require_version("Gtk", "3.0")
from   gi.repository import Gtk, Gdk 

def pcallBack(*args):
	print pclip.wait_for_text() 

if __name__ == '__main__':    
	import signal    
	signal.signal(signal.SIGINT, signal.SIG_DFL)    
	pclip = Gtk.Clipboard.get(Gdk.SELECTION_PRIMARY)
	pclip.connect('owner-change',pcallBack)
	Gtk.main()
```

https://fedorapeople.org/~elmarco/clipsync.py

## python Gtk add socket server

https://stackoverflow.com/questions/47265105/how-to-listen-socket-when-app-is-running-in-gtk-main
```
GLib.IOChannel.add_watch
```

客户端代码
https://jcoppens.com/soft/howto/gtk/chat_socket.en.php

https://rox.sourceforge.net/desktop/node/413.html
=> 代码未验证成功

Gtk.Socket ??

关键字《python Gtk tcp server》
https://stackoverflow.com/questions/45187406/how-to-implement-a-tcp-server-in-gtk-based-application-using-giochannel

## 其他

https://blog.csdn.net/Sakuya__/article/details/89874642
剪贴板(Clipboard)是由操作系统维护的一块内存区域，这块内存区域不属于任何单独的进程，但是每一个进程又都可以访问这块内存区域，而实质上当在一个进程中复制数据时，就是将数据放到该内存区域中，而当在另一个进程中粘贴数据时，则是从该块内存区域中取出数据。

从剪切板的定义中我们可以看出，剪切板和共享内存差不多，都是在系统中使用一块公共的内存，只是共享内存的公共内存是我们自己申请创建的，剪切板是由操作系统维护的。剪切板可以用来实现进程间通信，只是通常我们只在广义上把它认为是进程间通信的一种。因为剪切板是一种非常松散的交换媒介，不像共享内存中，我们在一个进程访问共享内存时会设置锁防止其他程序在此时访问该内存，而在剪切板中是没有这种机制的。

https://developer.aliyun.com/article/484980
1、监视剪贴板

原理：

(1) WM_DRAWCLIPBOA

系统提供了WM_DRAWCLIPBOARD消息用于监视剪贴板的变。如果调用

SetClipboardViewer函数设置了窗口为剪贴板查看器，那么当剪贴板中的内容变化时，所注册的查看器窗口会收到WM_CHANGECBCHAIN消息和WM_DRAWCLIPBOARD消息。

    当剪贴板中的内容变化时，窗口会收到WM DRAWCLIPBOARD消息。当查看器链新的节点加入或有节点退出窗口会收到WM_CHANGECBCHAIN消息。

(2) SetClipboardViewer函数
2、剪贴板数据格式

    剪贴板中可能会存在各种各样的数据。因此剪贴板中在保存数据的同时还需要保存数据的格式信息。

    系统使用一个UINT类型的数据来表示剪贴板中的数据格式。在这些格式信息中，有很多是各种应用程序之间通用的，比如文本、位图等。这些数据格式已经由系统预先定义，称为标准格式。

    还有一些应用程序也希望自行定义剪贴板的数据格式，这样可以方便地在同一个应用程序的不同实例间进行数据传递而不需要对数据的格式进行过多的处理(典型的就包括Word)。

https://www.cnblogs.com/yifi/p/6596558.html
在数据提供进程创建了剪贴板数据后，一直到有其他进程获取剪贴板数据前，
这些数据都要占据内存空间。如在剪贴板放置的数据量过大，就会浪费内存空间，
降低对资源的利用率。
为避免这种浪费，可以采取延迟提交（Delayed rendering）技术，
即由数据提供进程先创建一个指定数据格式的空（NULL）剪贴板数据块，
直到有其他进程需要数据或自身进程要终止运行时才真正提交数据。

[(好)GTK+学习笔记（二）](https://www.cnblogs.com/silvermagic/p/9087648.html)
为了能让剪切板能同时处理多种格式的数据，剪切板提供了回调函数的机制来处理实际数据。当你设置剪切板数据的时候，你可以使用gtk_clipboard_set_text()直接设置数据，或者使用gtk_clipboard_set_with_data()和gtk_clipboard_set_with_owner()提供一个当剪切板的数据被使用时，才设置剪切板数据的回调函数。如果是构件提供剪切板内容，就用gtk_clipboard_set_with_owner()，如果拷贝的是基础类型数据，比如字符串，就用gtk_clipboard_set_with_data()。

[(好)spice agent 剪贴板共享机制分析](https://blog.csdn.net/weixin_34278190/article/details/91580927)
spice 协议定义了一组用于spice客户端和spice agent之间通信的双向通信通道。spice只提供了一个通信通道，具体的传输数据内容对协议而言是不透明的。此通道可用于各种用途，如客户端和客户机之间剪贴板共享，分辨率设置等。

https://github.com/239144498/ClipSync
ClipSync是一个全平台剪贴板同步服务，可以很好做到多设备连接并且同步剪贴板内容。该服务主打无感同步，不需要用户手动操作，操作配置界面在Web端进行。

https://blog.csdn.net/u011720508/article/details/115509260
qt-wayland平台下复制粘贴原理
setImageData()

https://blog.51cto.com/u_15314083/3193103
如要使用自定义的数据类型，就有点麻烦了。

[spice协议——vdagent](https://www.jianshu.com/p/cc0e4002ffb8)
剪切板相关消息
spice剪切板用于在guest和client之间拷贝数据，前提是guest和client都需要实现VD_AGENT_CAP_CLIPBOARD_SELECTION功能，guest和client都能对剪切板进行如下操作，这些操作通过后面括号中的消息触发。
- 申明所有权(VD_AGENT_CLIPBOARD_GRAB)
- 释放所有权(VD_AGENT_CLIPBOARD_RELEASE)
- 请求数据(VD_AGENT_CLIPBOARD_REQUEST)
- 发送数据（VD_AGENT_CLIPBOARD）

接下来以guest->client拷贝文本为例，反向的逻辑是相同的：

虚拟机中agent会监听系统事件，当监听到复制事件时，会触发回调向client端发送VD_AGENT_CLIPBOARD_GRAB消息，获取剪切板的所有权。
client端接收到GRAB消息之后，会发送通过信号触发clipboard_grab回调，回调中会调用gtk的gtk_clipboard_set_with_owner接口注册剪切板的clipboard_get和clipboard_clear操作，并设置owner用于监听粘贴操作。
当客户端有粘贴操作时，会触发clipboard_get回调，回调中先连接VD_AGENT_CLIPBOARD消息的回调clipboard_got_from_guest，然后向guest发送VD_AGENT_CLIPBOARD_RELEASE消息，请求剪切板数据，然后会启动一个mainloop等待数据到来。
guest收到VD_AGENT_CLIPBOARD_RELEASE消息时，就会通过VD_AGENT_CLIPBOARD消息将剪切板数据发送给client。
client接收到消息，会调到clipboard_got_from_guest，将数据拷贝到系统剪切板。
然后在系统事件循环中会将系统剪切板的数据拷贝到目标组件。
至此完成一次粘贴操作。

https://cloud.tencent.com/developer/article/2168913
Spice 架构

#### python gtk tcp服务

问chatgtp问题:
- python3 gtk tcp server communicate with clipboard
- python3 gtk clipboard set_text not working
  it's possible that the clipboard ownership might be getting lost or not properly acquired.
- python3 gtk tcp echo server

关键字《python3 "gtk" tcp chat server》

https://stackoverflow.com/questions/8826523/gtk-main-and-unix-sockets
- One solution is to integrate your events into the event loop of Gtk+.
- Another solution would be to use Gtk+ networking functionality.
- A third solution is to start a second thread that handles your networking, e.g. with posix threads or Gtk+ threading functionality.

#### 剪切板类型

vim selection clipboard
https://vi.stackexchange.com/questions/84/how-can-i-copy-text-to-the-system-clipboard-from-vim

For X11-based systems (ie. Linux and most other UNIX-like systems) there are two clipboards which are independent of each other:

- PRIMARY - This is copy-on-select, and can be pasted with the middle mouse button.
- CLIPBOARD - This is copied with (usually) ^C, and pasted with ^V (It's like MS Windows).

OS X and Windows systems only have one clipboard.

For X11 systems there are also number of tools that synchronize these clipboards for you; so if they appear to be the same, you may have one of them running.

Vim has two special registers corresponding to these clipboards:

- `*` uses PRIMARY; mnemonic: Star is Select (for copy-on-select)
- `+` uses CLIPBOARD; mnemonic: CTRL PLUS C (for the common keybind)

https://www.elecfans.com/d/1233855.html
ubuntu默认没有开启vim支持系统clipboard, 需要安装
```
apt install vim-gtk
```

#### 剪切板设置二进制数据

关键字《python3 gtk clipboard set binary data》

```
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk

def set_clipboard_data(binary_data):
    # Create a new clipboard
    clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)

    # Specify the type of data you are setting (binary data)
    target = Gdk.Atom.intern('application/octet-stream', True)

    # Specify the data and its length
    data = Gtk.SelectionData.new_for_target(target)
    data.set(data.get_target(), 8, binary_data)

    # Set the data on the clipboard
    clipboard.set_with_data([target], lambda clipboard, selection_data, info: on_clipboard_set(selection_data), data)

def on_clipboard_set(selection_data):
    print("Data set in the clipboard successfully!")

# Example binary data (replace this with your actual binary data)
binary_data = b'\x01\x02\x03\x04\x05'

# Call the function to set binary data in the clipboard
set_clipboard_data(binary_data)

# Start the GTK main loop (if not already started)
Gtk.main()
```

获取二进制数据
```
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk

def on_clipboard_received(clipboard, selection_data, user_data):
    # Check if the data was received successfully
    if selection_data.get_format() == 8:
        binary_data = selection_data.get_data()
        print("Binary data received from clipboard:", binary_data)
    else:
        print("Failed to retrieve binary data from the clipboard.")

def get_clipboard_data():
    # Create a new clipboard
    clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)

    # Request contents asynchronously and connect the callback
    clipboard.request_contents('application/octet-stream', on_clipboard_received, None)

# Call the function to get binary data from the clipboard
get_clipboard_data()

# Start the GTK main loop (if not already started)
Gtk.main()
```


## 旧的资料

2019-11-10

TODO:
spice_copy项目

思路：搜索关键字“ubuntu 监控剪切板变化”
python监控gtk剪切板变化

http://cn.voidcc.com/question/p-dhnjcmij-bbq.html
在ubuntu 18.04上测试生效
```
from gi.repository import Gtk, Gdk

def test(*args):
    print "Clipboard changed"

clip = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
clip.connect('owner-change',test)
Gtk.main()
```

python操作系统剪切板
python gtk+库
https://thebigdoc.readthedocs.io/en/latest/PyGObject-Tutorial/clipboard.html

```
clip = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD) 
data = clip.wait_for_text()
clip.set_text(data, len(data))
```


三种方法:
https://www.jb51.net/article/169771.htm
使用第三方库pyperclip
```
import pyperclip
data = pyperclip.paste()
data = data[7:12]
pyperclip.copy(data)
pyperclip.paste()
```

优点： 跨平台，接口调用方便简洁
缺点： 剪切板的数据格式只支持utf-8文本，频繁读写速度较慢
PyGTK - Clipboard Class
https://www.tutorialspoint.com/pygtk/pygtk_clipboard_class.htm


## 参考资料

https://lazka.github.io/pgi-docs/Gtk-3.0/classes/Clipboard.html
=> python clipboard api文档

https://docs.gtk.org/gtk3/method.Clipboard.get_owner.html
=> c接口 api文档

https://api.gtkd.org/gtk.Clipboard.Clipboard.html
