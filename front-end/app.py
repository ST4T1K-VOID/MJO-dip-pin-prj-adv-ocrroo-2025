import requests

from flask import Flask
from flask import render_template, redirect
from flask import request, url_for, session


app = Flask(__name__)
app.secret_key = "very_secret_key"

# NOTE: flask run --port 8001 --debug

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
    video_id = request.form.get('video')
    user = request.form.get('username')

    path = f"front-end/static/media/{video_id}.mp4"

    session['video'] = video_id
    session['user'] = user

    print(video_id, user)

    # try get user bookmarks for video

    return redirect(url_for("video"))


@app.route("/video")
def video():
    """
    (TODO: loads the stored (in the session) video)
    and a sends a transcript to the template if possible
    """
    transcript = request.args.get("transcript")
    video_path = session.get('video')

    print(video_path)

    if transcript:
        return render_template("video.html", transcript=transcript, video=video_path)

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

    return redirect(url_for('video', transcript=response))
