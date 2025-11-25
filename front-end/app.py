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
    """gets a list of videos from the api and loads the indexs/login page"""

    videos = requests.get("http://127.0.0.1:8000/video").json()

    if videos['count'] == 0:
        videos = None

    print(videos['videos'])

    return render_template("index.html", videos=videos['videos'])


@app.route("/login", methods=["POST"])
def login():
    """
    gets the username and selected video entered by the user,
    enters video id and path, and the user's name to the session.
    """
   
    global bookmark_manager, BOOKMARK_DB_PATH
    
    video_id = request.form.get('video')
    user = request.form.get('username')

    path = f"front-end/static/media/{video_id}.mp4"

    session['video'] = video_id
    session['user'] = user
    bookmark_manager = BookmarkManager(BOOKMARK_DB_PATH, user)
    tables = bookmark_manager.get_tables()
    # check if database has been populated with tables
    if len(tables) == 0:
        bookmark_manager.create_bookmarks_db()
    # if user not in database, add them
    bookmark_manager.check_existing_user()
    # if video not in database, add it
    bookmark_manager.check_video_in_db(video_id)
    print(video_id, user)

    return redirect(url_for("video"))


@app.route("/video")
def video():
    """
    (TODO: loads the stored (in the session) video)
    and a sends a transcript to the template if possible
    """
    global bookmark_manager
    
    transcript = request.args.get("transcript")
    video_path = session.get('video')
    current_time = request.args.get("current_time")
    bookmarks = bookmark_manager.load_bookmarks_for_video(session['video']['video_id'])
    print(transcript)

    if bookmarks:
        if transcript:
            if current_time:
                return render_template("video.html", video=video_path, bookmarks=bookmarks, transcript=transcript, current_time=current_time)
            else:
                return render_template("video.html", video=video_path, bookmarks=bookmarks, transcript=transcript)
        else:
            if current_time:
                return render_template("video.html", video=video_path, bookmarks=bookmarks, current_time=current_time)
            else:
                return render_template("video.html", video=video_path, bookmarks=bookmarks)
    else:
        if transcript:
            if current_time:
                return render_template("video.html", video=video_path, current_time=current_time, transcript=transcript)
            else:
                return render_template("video.html", video=video_path, transcript=transcript)
        else:
            if current_time:
                return render_template("video.html", video=video_path, current_time=current_time)
            else:
                return render_template("video.html", video=video_path)

@app.route("/generate-transcript", methods=["POST"])
def get_transcript():
    """
    get the ocr for a given time (in seconds) from the API
    redirect to /video with the transcript
    """
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