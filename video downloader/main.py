import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import threading
import sys
import yt_dlp

os.environ["PATH"] += os.pathsep + "/opt/homebrew/bin"

class VideoDownloaderApp:
    def __init__(self, root):
        # 护眼配色
        bg_color = '#e6f4ea'  # 浅绿色
        entry_bg = '#f5fff8'  # 更浅的绿色
        btn_bg = '#b7e1cd'    # 按钮绿色
        btn_fg = '#205522'    # 按钮字体深绿
        label_fg = '#205522'  # 标签深绿
        status_fg = '#388e3c' # 状态栏深绿
        root.configure(bg=bg_color)
        self.root = root
        self.root.title('跨平台超清视频下载器')
        self.root.geometry('500x400')
        self.root.resizable(False, False)

        # 链接输入（多行）
        tk.Label(root, text='视频链接（每行一个）：', bg=bg_color, fg=label_fg).pack(anchor='w', padx=20, pady=(20, 0))
        self.url_text = tk.Text(root, height=5, width=60, bg=entry_bg, fg=label_fg, insertbackground=label_fg)
        self.url_text.pack(padx=20, pady=5)

        # 画质选择
        frame1 = tk.Frame(root, bg=bg_color)
        frame1.pack(anchor='w', padx=20, pady=(10, 0))
        tk.Label(frame1, text='选择画质：', bg=bg_color, fg=label_fg).pack(side='left')
        self.quality_var = tk.StringVar(value='原画(最高清)')
        quality_options = ['原画(最高清)', '2K', '1080p', '720p']
        quality_box = ttk.Combobox(frame1, textvariable=self.quality_var, values=quality_options, state='readonly', width=12)
        quality_box.pack(side='left', padx=5)

        # 下载与暂停按钮
        frame2 = tk.Frame(root, bg=bg_color)
        frame2.pack(anchor='w', padx=20, pady=10)
        self.download_btn = tk.Button(frame2, text='下载', command=self.download_video, bg=btn_bg, fg=btn_fg, activebackground=btn_fg, activeforeground='white')
        self.download_btn.pack(side='left')
        self.pause_btn = tk.Button(frame2, text='暂停', state='disabled', command=self.pause_download, bg=btn_bg, fg=btn_fg, activebackground=btn_fg, activeforeground='white')
        self.pause_btn.pack(side='left', padx=10)

        # 进度条
        style = ttk.Style()
        style.theme_use('default')
        style.configure('TProgressbar', background='#388e3c', troughcolor=bg_color, bordercolor=bg_color, lightcolor=bg_color, darkcolor=bg_color)
        self._progress_value = 0
        self._progress_running = False
        self.progress = ttk.Progressbar(root, orient='horizontal', length=440, mode='determinate', style='TProgressbar', maximum=100)
        self.progress.pack(padx=20, pady=5)
        self._refresh_progress()

        # 状态显示
        self.status_var = tk.StringVar(value='请粘贴视频链接（可批量），选择画质后点击下载')
        tk.Label(root, textvariable=self.status_var, fg=status_fg, bg=bg_color, font=('微软雅黑', 10, 'bold')).pack(pady=5)

        # 下载控制
        self._stop_flag = False
        self._current_total = 1
        self._current_index = 0

        # 下载路径选择
        self.download_path = self.get_default_desktop()
        path_frame = tk.Frame(root, bg=bg_color)
        path_frame.pack(anchor='w', padx=20, pady=(0, 5))
        tk.Label(path_frame, text='下载保存路径：', bg=bg_color, fg=label_fg).pack(side='left')
        self.path_var = tk.StringVar(value=self.download_path)
        self.path_label = tk.Label(path_frame, textvariable=self.path_var, bg=bg_color, fg=label_fg)
        self.path_label.pack(side='left', padx=5)
        tk.Button(path_frame, text='选择路径', command=self.choose_path, bg=btn_bg, fg=btn_fg, activebackground=btn_fg, activeforeground='white').pack(side='left', padx=5)

    def _refresh_progress(self):
        self.progress['value'] = self._progress_value
        self.progress.update_idletasks()
        if self._progress_running:
            self.root.after(100, self._refresh_progress)

    def pause_download(self):
        # 设置停止标志，终止下载线程
        self._stop_flag = True
        self.status_var.set('下载已暂停。')
        self.download_btn.config(state='normal')
        self.pause_btn.config(state='disabled')
        self._progress_running = False

    def download_video(self):
        urls = self.url_text.get('1.0', 'end').strip().splitlines()
        urls = [u.strip() for u in urls if u.strip()]
        quality = self.quality_var.get()
        if not urls:
            messagebox.showwarning('提示', '请输入至少一个视频链接！')
            return
        self.download_btn.config(state='disabled')
        self.pause_btn.config(state='normal')
        self._progress_value = 0
        self._progress_running = True
        self._refresh_progress()
        self._stop_flag = False
        self._current_total = len(urls)
        self._current_index = 0
        threading.Thread(target=self._batch_download_thread, args=(urls, quality), daemon=True).start()

    def _batch_download_thread(self, urls, quality):
        for idx, url in enumerate(urls):
            if self._stop_flag:
                self.status_var.set('下载已暂停。')
                break
            self._current_index = idx + 1
            self.status_var.set(f'正在下载第{self._current_index}/{self._current_total}个...')
            self._progress_value = int(((self._current_index - 1) / self._current_total) * 100)
            self._download_thread(url, quality, batch=True)
        self._progress_value = 100
        self.download_btn.config(state='normal')
        self.pause_btn.config(state='disabled')
        if not self._stop_flag:
            self.status_var.set('全部下载完成！')
        self._progress_running = False

    def _download_thread(self, url, quality, batch=False):
        try:
            desktop = self.download_path
            # 画质参数
            if quality == '原画(最高清)':
                ydl_format = 'bestvideo+bestaudio/best'
            elif quality == '2K':
                ydl_format = 'bestvideo[height<=1440]+bestaudio/best[height<=1440]/best[height<=1440]/best'
            elif quality == '1080p':
                ydl_format = 'bestvideo[height<=1080]+bestaudio/best[height<=1080]/best[height<=1080]/best'
            elif quality == '720p':
                ydl_format = 'bestvideo[height<=720]+bestaudio/best[height<=720]/best[height<=720]/best'
            else:
                ydl_format = 'bestvideo+bestaudio/best'
            self.last_filename = None
            def hook(d):
                if self._stop_flag:
                    raise Exception('用户主动暂停')
                self._progress_hook(d)
                if d['status'] == 'finished':
                    self.last_filename = d.get('filename')
            ydl_opts = {
                'outtmpl': os.path.join(desktop, '%(title)s.%(ext)s'),
                'format': ydl_format,
                'noplaylist': True,
                'progress_hooks': [hook],
                'quiet': True,
                'merge_output_format': 'mp4',
                'ffmpeg_location': os.path.join(os.path.dirname(sys.argv[0]), 'ffmpeg-mac'),
            }
            self.status_var.set(f'正在下载：{url[:40]}...')
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            if self.last_filename:
                filename = os.path.basename(self.last_filename)
                self.status_var.set(f'下载完成：{filename}')
            else:
                self.status_var.set('下载完成！已保存到目标文件夹。')
        except Exception as e:
            if str(e) == '用户主动暂停':
                self.status_var.set('下载已暂停。')
            else:
                self.status_var.set('下载失败，请检查链接或网络。')
                messagebox.showerror('错误', f'下载失败：{e}')
        finally:
            self._progress_value = 0
            self._progress_running = False

    def _progress_hook(self, d):
        if d['status'] == 'downloading':
            percent = d.get('_percent_str', '').replace('%','').strip()
            try:
                self._progress_value = float(percent)
            except:
                self._progress_value = 0
            speed = d.get('_speed_str', '').strip()
            eta = d.get('_eta_str', '').strip()
            self.root.after(0, self.status_var.set, f'下载中：{percent}% 速度:{speed} 剩余:{eta}')
        elif d['status'] == 'finished':
            self._progress_value = 100
            self.root.after(0, self.status_var.set, '正在合并视频...')

    def get_default_desktop(self):
        if sys.platform == 'win32':
            desktop = os.path.join(os.path.expanduser('~'), 'Desktop')
        else:
            desktop = os.path.join(os.path.expanduser('~'), '桌面')
            if not os.path.exists(desktop):
                desktop = os.path.join(os.path.expanduser('~'), 'Desktop')
        return desktop

    def choose_path(self):
        path = filedialog.askdirectory(initialdir=self.download_path, title='选择下载保存文件夹')
        if path:
            self.download_path = path
            self.path_var.set(path)

if __name__ == '__main__':
    root = tk.Tk()
    app = VideoDownloaderApp(root)
    root.mainloop() 