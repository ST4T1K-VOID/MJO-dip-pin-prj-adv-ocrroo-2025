"""
responsible for front_end rendering and validation/logic
"""

import requests

from flask import Flask
from flask import render_template, redirect
from flask import request, url_for, session

import bleach

from .bookmark_utils import BookmarkManager


app = Flask(__name__)
app.secret_key = "very_secret_key"

# NOTE: flask run --port 8001 --debug

# Bookmark format: { id: timestamp(seconds) }
BOOKMARK_DB_PATH = './bookmark_utils/resources/bookmarks.db'

@app.route("/")
def index():
    """gets a list of videos from the api and loads the indexs/login page"""

    videos = requests.get("http://127.0.0.1:8000/video").json()
    is_invalid = request.args.get("is_invalid")

    if videos['count'] == 0:
        videos = None

    print(videos['videos'])

    print("valid?: ", is_invalid)

    return render_template("index.html", videos=videos['videos'], is_invalid=bool(is_invalid))


@app.route("/login", methods=["POST"])
def login():
    """
    gets the username and selected video entered by the user,
    enters video id and path, and the user's name to the session.
    """

    global bookmark_manager, BOOKMARK_DB_PATH

    user = request.form.get('username')
    if not validate(user):
        return redirect(url_for("index", is_invalid="True"))

    video_id = request.form.get('video')

    session['video'] = video_id
    session['user'] = user

    bookmark_manager = BookmarkManager(BOOKMARK_DB_PATH, user)
    tables = bookmark_manager.get_tables()
    # check if database has been populated with tables
    if len(tables) == 0:
        bookmark_manager.create_bookmarks_db()
    # if user not in database, add them
    bookmark_manager.check_user_in_db()
    # if video not in database, add it
    bookmark_manager.check_video_in_db(video_id)
    bookmark_manager.conn.close()

    return redirect(url_for("video"))


@app.route("/video")
def video():
    """
    loads selected video current time (upon reload)
    and a sends a transcript to the template if possible
    """
    global bookmark_manager
    bookmark_manager = BookmarkManager(BOOKMARK_DB_PATH, session['user'])

    transcript = request.args.get("transcript") or None
    current_time = request.args.get("current_time") or None
    video_path = session.get('video') or None

    bookmarks = bookmark_manager.load_bookmarks_for_video(session['video']) or None

    bookmark_manager.conn.close()

    return render_template("video.html",
                           video=video_path,
                           bookmarks=bookmarks,
                           transcript=transcript,
                           current_time=current_time)

@app.route("/generate-transcript", methods=["POST"])
def get_transcript():
    """
    get the ocr for a given time (in seconds) from the API
    redirect to /video with the transcript
    """
    video_id = session.get('video')
    video_position = request.form['video_pos']

    url = f"http://127.0.0.1:8000/video/{video_id}/frame/{video_position}/ocr"
    response = requests.get(url).content

    print("url: ", url)

    response = response.decode(encoding='utf-8')

    return redirect(url_for('video', current_time=video_position, transcript=response))


@app.route("/load-bookmark", methods=["POST"])
def load_bookmark():
    """Loads the timestamp associated with the bookmark"""

    global bookmark_manager
    bookmark_id = request.form['bookmark_id']
    bookmark = bookmark_manager.get_bookmark(bookmark_id)

    bookmark_manager.conn.close()

    return redirect(url_for("video", current_time=bookmark['time']))


@app.route("/add-bookmark", methods=["POST"])
def add_bookmark():
    """
    save a time(as seconds) in the opened video in the database as a bookmark,
    the bookmark is tied to the user.
    """

    time = request.form['bookmark_pos']
    title = request.form['bookmark_title']
    video_id = session['video']

    bookmark_manager = BookmarkManager(BOOKMARK_DB_PATH, session['user'])
    bookmark_manager.add_bookmark(video_id, time, title)

    bookmark_manager.conn.close()

    return redirect(url_for("video", current_time=time))


def validate(username: str):
    """
    sanitize and validate entered string(username)
    """
    username = bleach.clean(username)

    if len(username) > 32 or len(username) < 2:
        return False

    return username
