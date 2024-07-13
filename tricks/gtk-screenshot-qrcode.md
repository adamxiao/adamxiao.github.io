# python二维码识别gtk截图

## 通过二维码图片传输文件

#### 截图指定窗口

TODO: gnome-screenshot 截图太慢了，待优化

获取窗口id
```
xdotool selectwindow
```

根据窗口id，截图
```
import os
import subprocess

window_id=31457287
# 确保窗口在最前
os.system(f"xdotool windowactivate {window_id}")

# 截取指定窗口的截图
screenshot_path = "/tmp/qrcode.png"
os.system(f"gnome-screenshot -w -B -f {screenshot_path}")
```

可以显示截图
```
# 显示截图
from PIL import Image
img = Image.open(screenshot_path)
img.show()
```

关键字《python3 gnome桌面截图，指定窗口》

[如何实现Python3在隐藏黑窗口的情况下截屏](https://blog.51cto.com/u_16213335/10438063)

```
from PIL import ImageGrab
screenshot = ImageGrab.grab()
screenshot.save("screenshot.png")
```

[通过python脚本截取屏幕截图.(Linux的)](https://cloud.tencent.com/developer/information/%E9%80%9A%E8%BF%87python%E8%84%9A%E6%9C%AC%E6%88%AA%E5%8F%96%E5%B1%8F%E5%B9%95%E6%88%AA%E5%9B%BE.%5BLinux%E7%9A%84%5D)
```
pip install PyQt5 PyQtWebEngine
```

#### 生成二维码图片

gpt关键字《python生成二维码，显示到gnome桌面上》
《python读取二进制文件，生成二维码》
```
import qrcode
import os

# 生成二维码
qr = qrcode.QRCode(
    version=1,
    error_correction=qrcode.constants.ERROR_CORRECT_L,
    box_size=10,
    border=4,
)

# 读取二进制文件内容
file_path = '/tmp/adam.bin'
with open(file_path, 'rb') as file:
    binary_data = file.read()

# 将二进制数据转换为十六进制字符串
hex_data = binary_data.hex()

# 最多2953个字符
qr.add_data(binary_data)
#qr.add_data('https://www.example.com')
qr.make(fit=True)

img = qr.make_image(fill='black', back_color='white')
img_path = "/tmp/qrcode.png"
img.save(img_path)

# 使用GNOME图像查看器显示图像
os.system(f'xdg-open {img_path}')
```

#### 解析识别二维码图片

关键字《python 二维码模块》

gpt《python3 识别二维码》
先安装cv2
```
pip3 install opencv-python pyzbar
apt install python3-opencv python3-pyzbar
```

然后识别二维码数据
```
import cv2
from pyzbar.pyzbar import decode

# 加载图像
image_path = '/tmp/qrcode.png'  # 替换为你的二维码图像路径
image = cv2.imread(image_path)

# 解码二维码
decoded_objects = decode(image)

# 打印解码信息
for obj in decoded_objects:
    print("Type:", obj.type)
    print("Data:", obj.data.decode("utf-8"))
    print("Data:", len(obj.data.decode("utf-8")))
```

## 旧的资料

关键字《python识别屏幕中指定区域的二维码》

https://wenku.csdn.net/answer/d022ca362c6f424dac074b3a1ab78ac0
使用 PyAutoGUI 库的 screenshot() 函数截取屏幕

https://www.readinghere.com/blog/python-pyautogui-cn/
Python + PyAutoGUI: 轻松实现用户界面自动化

PyAutoGUI 是一个 Python 库，使您能够通过控制鼠标和键盘来自动执行 GUI（图形用户界面）任务。 它可以模拟用户操作，例如移动光标、单击按钮、键入文本、按键、捕获屏幕截图等。它还可以识别和定位屏幕上的图像，这对于测试或与 GUI 应用程序交互非常有用。
```
pip install pyautogui -i https://pypi.tuna.tsinghua.edu.cn/simple
```

#### 二维码数据存储

关键字《二维码数据长度限制》

https://blog.csdn.net/weixin_39804265/article/details/124226127
二维码可以包含多少个字符？

https://tuzim.net/blog/233.html
QrCode二维码最大容量是多少？
- 可存储 UTF-8 字节数：2953 字节
- 可存储 UTF-8 数字/字母数量：2953 个
- 可存储 UTF-8 汉字数量：2953/3 = 984 个
