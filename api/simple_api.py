"""Provides a simple API for your basic OCR client

Drive the API to complete "interprocess communication"

Requirements
"""
from pathlib import Path

from library_basics import CodingVideo

from fastapi import FastAPI, HTTPException
from fastapi import Response
from pydantic import BaseModel

#NOTE: fastapi dev simple_api.py --port 8000
app = FastAPI()


# We'll create a lightweight "database" for our videos
# You can add uploads later (not required for assessment)
# For now, we will just hardcode are samples
VIDEOS: dict[str, Path] = {
    "oop": Path("./resources/oop.mp4"),
    "NotReal": Path("./resources/"),
    "JustTesting": Path("./resources/"),
}
# structure dict>count>int & video>list>dict>name>path
# name: you refer to this (e.g. demo) in api endpoints


class VideoMetaData(BaseModel):
    fps: float
    frame_count: int
    duration_seconds: float
    _links: dict | None = None


@app.get("/video")
def list_videos():
    """List all available videos with HATEOAS-style links."""
    return {
        "count": len(VIDEOS),
        "videos": [
            {
                "id": vid,
                "path": str(path), # Not standard for debug only
                "_links": {
                    "self": f"/video/{vid}",
                    "frame_example": f"/video/{vid}/frame/1.0"
                }
            }
            for vid, path in VIDEOS.items()
        ]
    }


def _open_vid_or_404(vid: str) -> CodingVideo:
    """open a video from specified path if it is valid"""
    path = VIDEOS.get(vid)
    print(path)
    if not path or not path.is_file():
        raise HTTPException(status_code=404, detail="Video not found")
    try:
        return CodingVideo(path)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Could not open video {e}")


def _meta(video: CodingVideo) -> VideoMetaData:
    return VideoMetaData(
            fps=video.fps,
            frame_count=video.frame_count,
            duration_seconds=video.duration
    )


@app.get("/video/{vid}", response_model=VideoMetaData)
def video(vid: str):
    """get video metadata and length in seconds"""
    video = _open_vid_or_404(vid)
    try:
        meta = _meta(video)
        meta._links = {
            "self": f"/video/{vid}",
            "frames": f"/video/{vid}/frame/{{seconds}}"
        }
        return meta
    finally:
        video.capture.release()


@app.get("/video/{vid}/frame/{t}", response_class=Response)
def video_frame(vid: str, t: float):
    """
    get a video frame as bytes
    """
    try:
        video = _open_vid_or_404(vid)
        return Response(content=video.get_image_as_bytes(t), media_type="image/png")
    finally:
        video.capture.release()


@app.get("/video/{vid}/frame/{t}/ocr", response_class=Response)
def frame_ocr(vid: str, t: int | float):
    """
    get the text (ocr) from a given video frame
    """
    try:
        video = _open_vid_or_404(vid)
        return Response(content=video.get_text_from_frame(t))
    finally:
        video.capture.release()
