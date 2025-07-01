# 跨平台超清视频下载器

## 🔧 项目目标

开发一个桌面工具，支持在 Mac 和 Windows 上运行，能够下载 YouTube、Bilibili 等视频平台的高清视频（支持1080p、4K），并生成一个可复制使用的独立桌面文件包，用户无需安装环境即可运行。

---

## ✅ 项目功能

| 功能模块         | 描述                                   |
|------------------|----------------------------------------|
| 视频平台支持     | 支持 YouTube、Bilibili（通过 yt-dlp）  |
| 视频质量选项     | 用户可选择 1080p、4K 等清晰度下载      |
| 图形用户界面（GUI） | 使用 Tkinter 构建图形界面，简洁友好    |
| 下载路径         | 下载文件自动保存至用户桌面              |
| 平台兼容         | 支持 macOS 和 Windows 操作系统          |
| 可执行打包       | 生成 .exe（Windows）或 .app（Mac） 文件，可直接运行 |

---

## 🧰 所需工具与依赖
- Python ≥ 3.10（建议安装最新版）
- Cursor IDE（用于 AI 辅助开发）
- yt-dlp：视频下载核心工具
- tkinter：图形界面（Python内建）
- pyinstaller（Windows） / py2app（macOS）：打包工具

安装依赖命令：

```bash
pip install yt-dlp tk
# 如果需要打包：
pip install pyinstaller
# 若在 macOS 打包 GUI 工具，也可使用：
pip install py2app
```

---

## 📁 项目文件结构

```
VideoDownloader/
├── main.py             # 主程序入口
├── README.txt          # 使用说明（含快捷方式指引）
├── icon.png            # 可选：自定义图标
├── dist/               # 打包生成的可执行文件（.exe 或 .app）
└── requirements.txt    # Python 依赖列表
```

---

## 💡 功能细节说明
- 启动后弹出图形窗口，用户粘贴链接、选择画质，点击"下载"按钮。
- 下载状态通过文本或进度条反馈。
- 下载成功后自动保存到当前用户的桌面目录下。
- 所有操作平台应兼容，无需用户修改路径。
- 用户可以复制整个文件夹，在另一台电脑（Mac 或 Windows）直接运行。

---

## 🛠️ 打包说明

### Windows 打包（.exe）

```bash
pyinstaller --onefile --windowed main.py
```

生成后的可执行文件位于 dist/main.exe

### macOS 打包（.app）

```bash
pyinstaller --windowed main.py
```

或使用 py2app：

1. 创建 setup.py：

```python
from setuptools import setup

APP = ['main.py']
OPTIONS = {
    'argv_emulation': True,
    'iconfile': 'icon.icns',  # 可选
}

setup(
    app=APP,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
```

2. 执行：

```bash
python setup.py py2app
```

---

## 📦 可交付内容
1. 桌面文件夹（含 .exe 或 .app 可执行文件）
2. 支持平台：Windows / macOS
3. 无需用户安装 Python 或命令行操作
4. 视频下载后自动保存到桌面

---

## 🚀 可扩展功能（开发后期）
- 自动识别视频标题作为文件名
- 支持批量粘贴多个链接
- 支持解析播放列表
- 下载封面图 / 字幕 / 弹幕
- 美化界面、添加主题切换
- 使用 Electron / Tauri 构建更美观界面 