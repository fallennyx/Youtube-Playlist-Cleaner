import os
import sys

from flask import Flask, render_template, request, redirect, url_for

print(sys.path)
import backend

app = Flask(__name__)

chrome_path = "/opt/render/project/.render/chrome/opt/google/chrome/google-chrome"

# Set Chrome as the default browser for webbrowser module
os.environ["WEBBROWSER"] = chrome_path




@app.route('/')
def index():
    return render_template('index.html')


@app.route('/initial.py', methods=['POST'])
def process_form():
    video_id = request.form['youtube_link']
    if 'list=' in video_id:
        start_index = video_id.find('list=') + len('list=')
        end_index = video_id.find('&', start_index)
        if end_index == -1:
            video_id = video_id[start_index:]
        else:
            video_id = video_id[start_index:end_index]
    else:
        return render_template('error.html')
    if video_id:
        backend.final(video_id)
        return redirect(url_for('success'))
    else:
        return render_template('error.html')


@app.route('/success')
def success():
    return redirect("https://www.youtube.com/feed/playlists")


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=True)