import requests

from flask import Flask
from flask import render_template, redirect
from flask import request, url_for, session
from .bookmark_utils import BookmarkManager, Bookmark
import json

app = Flask(__name__)
app.secret_key = "very_secret_key"
# NOTE: flask run --port 8001 --debug

# Bookmark format: { id: timestamp(seconds) }
BOOKMARK_DB_PATH = './bookmark_utils/resources/bookmarks.db'
bookmark_manager = None

@app.route("/")
def index():

    videos = requests.get("http://127.0.0.1:8000/video").json()

    if videos['count'] == 0:
        videos = None

    print(videos['videos'])

    return render_template("index.html", videos=videos['videos'])

@app.route("/login", methods=["POST"])
def login():
    global bookmark_manager, BOOKMARK_DB_PATH
    video_id = request.form.get('video')
    user = request.form.get('username')

    path = f"front-end/static/media/{video_id}.mp4"

    session['video'] = {'video_id': video_id, 'frontend_path': path}
    session['user'] = user
    bookmark_manager = BookmarkManager(BOOKMARK_DB_PATH, user)
    tables = bookmark_manager.get_tables()
    if len(tables) == 0:
        bookmark_manager.create_bookmarks_db()
    bookmark_manager.check_existing_user()
    print(video_id, user)

    #try get user bookmarks for video

    return redirect(url_for("video"))

@app.route("/video")
def video():
    global bookmark_manager
    transcript = request.args.get("transcript")
    current_time = request.args.get("current_time")
    bookmarks = bookmark_manager.load_bookmarks_for_video(session['video']['video_id'])
    print(transcript)

    if bookmarks:
        if transcript:
            if current_time:
                return render_template("video.html", bookmarks=bookmarks, transcript=transcript, current_time=current_time)
            else:
                return render_template("video.html", bookmarks=bookmarks, transcript=transcript)
        else:
            if current_time:
                return render_template("video.html", bookmarks=bookmarks, current_time=current_time)
            else:
                return render_template("video.html", bookmarks=bookmarks)
    else:
        if transcript:
            if current_time:
                return render_template("video.html", current_time=current_time, transcript=transcript)
            else:
                return render_template("video.html", transcript=transcript)
        else:
            if current_time:
                return render_template("video.html", current_time=current_time)
            else:
                return render_template("video.html")

@app.route("/generate-transcript", methods=["POST"])
def get_transcript():
    video_position = request.form['video_pos']

    url = f"http://127.0.0.1:8000/video/OOP/frame/{video_position}/ocr"
    response = requests.get(url).content

    response = response.decode(encoding='utf-8')

    return redirect(url_for('video', current_time=video_position, transcript=response))


@app.route("/load-bookmark", methods=["POST"])
def load_bookmark():
    """Loads the timestamp associated with the bookmark"""
    global bookmark_manager
    bookmark_id = request.form['bookmark_id']
    bookmark = bookmark_manager.get_bookmark(bookmark_id)
    return redirect(url_for("video", current_time=bookmark['time']))


@app.route("/add-bookmark", methods=["POST"])
def add_bookmark():
    global bookmark_manager
    time = request.form['bookmark_pos']
    title = request.form['bookmark_title']
    video_id = session['video']['video_id']
    bookmark_manager.add_bookmark(video_id, time, title)
    return redirect(url_for("video", current_time=time))