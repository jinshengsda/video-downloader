【跨平台超清视频下载器 使用说明】

一、软件简介
本工具支持在 Windows/macOS 上下载 YouTube、Bilibili 等平台的高清视频（1080p/4K），操作简单，下载文件自动保存到桌面。

二、依赖安装
1. 安装 Python 3.10 及以上版本。
2. 安装依赖：
   pip install -r requirements.txt

三、使用方法
1. 运行 main.py：
   python main.py
2. 粘贴视频链接，选择画质，点击"下载"。
3. 下载完成后，视频自动保存到桌面。

四、打包方法
- Windows：
  pyinstaller --onefile --windowed main.py
- macOS：
  pyinstaller --windowed main.py
  或参考 README.md 使用 py2app 打包。

五、常见问题
- 下载失败请检查网络或链接是否有效。
- 桌面路径自动识别，无需手动设置。

六、快捷方式指引
- 可将 dist 目录下的可执行文件创建桌面快捷方式，或直接复制整个文件夹到其他电脑使用。 