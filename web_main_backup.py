from flask import Flask, request, send_file, render_template_string
import yt_dlp
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template_string('''
    <h2>视频下载器</h2>
    <form action="/download" method="post">
        <input name="url" placeholder="输入视频链接" style="width:300px">
        <button type="submit">下载</button>
    </form>
    ''')

@app.route('/download', methods=['POST'])
def download():
    url = request.form['url']
    output_path = 'downloaded_video.mp4'
    # 如果之前有同名文件，先删除
    if os.path.exists(output_path):
        os.remove(output_path)
    ydl_opts = {
        'outtmpl': output_path,
        'format': 'bestvideo+bestaudio/best',
        'merge_output_format': 'mp4'
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    return send_file(output_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)