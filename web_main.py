from flask import Flask, request, send_file, render_template_string, jsonify, abort
import yt_dlp
import os
import signal
import multiprocessing

app = Flask(__name__)

download_progress = {"percent": 0, "status": "idle"}  # 用于保存下载进度
current_ydl_process = None

def progress_hook(d):
    if d['status'] == 'downloading':
        # 优先用 downloaded_bytes/total_bytes 计算百分比
        downloaded = d.get('downloaded_bytes') or 0
        total = d.get('total_bytes') or d.get('total_bytes_estimate') or 0
        if total:
            percent = downloaded / total * 100
        else:
            percent = 0
        download_progress["percent"] = percent
        download_progress["status"] = "downloading"
    elif d['status'] == 'finished':
        download_progress["percent"] = 100
        download_progress["status"] = "finished"

def run_ydl(ydl_opts, url):
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    download_progress["status"] = "finished"

@app.route('/')
def index():
    return render_template_string('''
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <title>视频下载器</title>
        <style>
            body {
                background: #f7faf7;
                color: #222;
                font-family: "PingFang SC", "Microsoft YaHei", Arial, sans-serif;
                margin: 0;
                padding: 0;
            }
            .main-container {
                display: flex;
                flex-direction: column;
                align-items: center;
                min-height: 100vh;
                justify-content: flex-start;
                padding-top: 60px;
            }
            .title {
                font-size: 2.5rem;
                font-weight: bold;
                margin-bottom: 32px;
                color: #222;
                letter-spacing: 1px;
            }
            .download-box {
                background: #fff;
                border-radius: 16px;
                box-shadow: 0 4px 24px rgba(0,0,0,0.08);
                padding: 32px 32px 24px 32px;
                width: 520px;
                max-width: 95vw;
                display: flex;
                flex-direction: column;
                align-items: center;
            }
            .input-row {
                display: flex;
                width: 100%;
                margin-bottom: 18px;
            }
            .input-row input {
                flex: 1;
                padding: 14px 16px;
                font-size: 1.1rem;
                border: 2px solid #b2dfdb;
                border-radius: 8px 0 0 8px;
                outline: none;
                transition: border 0.2s;
                height: 48px;
                box-sizing: border-box;
            }
            .input-row input:focus {
                border-color: #43a047;
            }
            .input-row select {
                width: 160px;
                border: 2px solid #b2dfdb;
                border-left: none;
                border-radius: 0;
                font-size: 1rem;
                outline: none;
                padding: 0 8px;
                height: 48px;
                box-sizing: border-box;
            }
            .input-row button {
                background: #7ed957;
                color: #fff;
                border: none;
                border-radius: 0 8px 8px 0;
                font-size: 1.1rem;
                font-weight: bold;
                padding: 0 28px;
                cursor: pointer;
                transition: background 0.2s;
                height: 48px;
            }
            .input-row button:hover {
                background: #43a047;
            }
            .desc {
                color: #888;
                font-size: 0.98rem;
                margin-bottom: 18px;
                text-align: center;
            }
            .tag-row {
                display: flex;
                gap: 16px;
                justify-content: center;
                margin-bottom: 18px;
            }
            .tag {
                background: #e8f5e9;
                color: #388e3c;
                border-radius: 8px;
                padding: 6px 18px;
                font-size: 1rem;
                font-weight: 500;
                display: flex;
                align-items: center;
                gap: 6px;
            }
            .progress-bar-bg {
                width: 100%;
                background: #c8e6c9;
                border-radius: 8px;
                height: 18px;
                margin-bottom: 10px;
                overflow: hidden;
                display: none;
            }
            .progress-bar {
                height: 100%;
                background: #43a047;
                width: 0%;
                transition: width 0.3s;
            }
            #progress-text {
                text-align: center;
                color: #388e3c;
                font-size: 1.05rem;
                min-height: 22px;
            }
            .footer {
                margin-top: 40px;
                color: #888;
                font-size: 14px;
                text-align: center;
            }
            @media (max-width: 600px) {
                .download-box { width: 98vw; padding: 18px 4vw 12px 4vw;}
                .input-row input { font-size: 1rem;}
                .input-row select { font-size: 1rem;}
                .input-row button { font-size: 1rem;}
            }
        </style>
    </head>
    <body>
        <div class="main-container">
            <div class="title">YouTube 视频下载器</div>
            <div class="download-box">
                <form id="download-form" style="width:100%;">
                    <div class="input-row">
                        <input id="url" name="url" placeholder="粘贴你的视频链接" required>
                        <select id="quality" name="quality">
                            <option value="best">最高清（自动）</option>
                            <option value="4320">4K</option>
                            <option value="2160">2K</option>
                            <option value="1080">1080P</option>
                            <option value="720">720P</option>
                        </select>
                        <button type="submit">下载</button>
                    </div>
                </form>
                <button type="button" id="pause-btn" style="display:none;margin-bottom:10px;">暂停</button>
                <div class="desc">
                    使用本工具即表示你同意我们的服务条款。<br>
                    支持YouTube、B站等主流平台，支持多种清晰度下载。
                </div>
                <div class="tag-row">
                    <div class="tag">🎬 YouTube</div>
                    <div class="tag">🎵 MP4/MP3</div>
                    <div class="tag">📺 4K/2K/1080P</div>
                </div>
                <div class="progress-bar-bg" id="progress-bar-bg">
                    <div class="progress-bar" id="progress-bar"></div>
                </div>
                <div id="progress-text"></div>
            </div>
            <div class="footer">© 2024 视频下载器 | 护眼配色设计</div>
        </div>
        <script>
            const form = document.getElementById('download-form');
            const progressBarBg = document.getElementById('progress-bar-bg');
            const progressBar = document.getElementById('progress-bar');
            const progressText = document.getElementById('progress-text');
            const pauseBtn = document.getElementById('pause-btn');

            let polling = false;
            let downloadStarted = false;

            form.onsubmit = function(e) {
                e.preventDefault();
                progressBarBg.style.display = 'block';
                progressBar.style.width = '0%';
                progressText.innerText = '等待下载开始...';
                downloadStarted = true;
                pauseBtn.style.display = 'inline-block';

                const url = document.getElementById('url').value;
                const quality = document.getElementById('quality').value;

                // 启动轮询
                if (!polling) {
                    polling = true;
                    pollProgress();
                }

                fetch('/download', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded'
                    },
                    body: new URLSearchParams({url, quality})
                }).then(response => {
                    if (response.ok) {
                        return response.blob();
                    } else {
                        return response.text().then(text => { throw new Error(text); });
                    }
                }).then(blob => {
                    const a = document.createElement('a');
                    a.href = window.URL.createObjectURL(blob);
                    a.download = 'video.mp4';
                    a.click();
                    polling = false;
                    downloadStarted = false;
                    pauseBtn.style.display = 'none';
                }).catch(err => {
                    progressText.innerText = '下载失败：' + err.message;
                    polling = false;
                    downloadStarted = false;
                    pauseBtn.style.display = 'none';
                });
            };

            pauseBtn.onclick = function() {
                fetch('/pause', {method: 'POST'})
                    .then(() => {
                        progressText.innerText = '已暂停下载';
                        pauseBtn.style.display = 'none';
                        polling = false;
                        downloadStarted = false;
                    });
            };

            function pollProgress() {
                if (!downloadStarted) return;
                fetch('/progress').then(res => res.json()).then(data => {
                    if (data.status === 'downloading') {
                        progressBar.style.width = data.percent + '%';
                        progressText.innerText = `正在下载... ${data.percent.toFixed(1)}%`;
                        setTimeout(pollProgress, 500);
                    } else if (data.status === 'finished') {
                        progressBar.style.width = '100%';
                        progressText.innerText = '下载完成！';
                        polling = false;
                        pauseBtn.style.display = 'none';
                    } else if (data.status === 'paused') {
                        progressText.innerText = '已暂停下载';
                        polling = false;
                        pauseBtn.style.display = 'none';
                    } else {
                        progressText.innerText = '等待下载开始...';
                        setTimeout(pollProgress, 500);
                    }
                });
            }
        </script>
    </body>
    </html>
    ''')

@app.route('/download', methods=['POST'])
def download():
    import yt_dlp
    url = request.form['url']
    quality = request.form.get('quality', 'best')
    output_path = 'downloaded_video.mp4'
    if os.path.exists(output_path):
        os.remove(output_path)
    quality_map = {
        'best': 'bestvideo+bestaudio/best',
        '4320': 'bestvideo[height=4320]+bestaudio/best',
        '2160': 'bestvideo[height=2160]+bestaudio/best',
        '1080': 'bestvideo[height=1080]+bestaudio/best',
        '720': 'bestvideo[height=720]+bestaudio/best',
    }
    download_progress["percent"] = 0
    download_progress["status"] = "downloading"
    ydl_opts = {
        'outtmpl': output_path,
        'format': quality_map.get(quality, 'bestvideo+bestaudio/best'),
        'merge_output_format': 'mp4',
        'progress_hooks': [progress_hook]
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            result = ydl.download([url])
        if not os.path.exists(output_path):
            return "下载失败：未生成视频文件", 400
        return send_file(output_path, as_attachment=True)
    except Exception as e:
        download_progress["status"] = "failed"
        return f"下载失败：{str(e)}", 400

@app.route('/progress')
def progress():
    return jsonify(download_progress)

@app.route('/pause', methods=['POST'])
def pause():
    global current_ydl_process
    if current_ydl_process and current_ydl_process.is_alive():
        current_ydl_process.terminate()
        current_ydl_process = None
    download_progress["status"] = "paused"
    return '', 204

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)