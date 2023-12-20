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

## 参考资料

https://lazka.github.io/pgi-docs/Gtk-3.0/classes/Clipboard.html
=> python clipboard api文档

https://docs.gtk.org/gtk3/method.Clipboard.get_owner.html
=> c接口 api文档

https://api.gtkd.org/gtk.Clipboard.Clipboard.html
