"""A basic introduction to Open CV

Instructions
------------

Implement the functions below based on their docstrings.

Notice some docstrings include references to third-party documentation
Some docstrings **require** you to add references to third-party documentation.

Make sure you read the docstrings C.A.R.E.F.U.L.Y (yes, I took the L to check that you are awake!)
"""

# imports - add all required imports here
from pathlib import Path
import cv2
import numpy as np
from PIL import Image


VID_PATH = Path("../resources/oop.mp4")
OUT_PATH = Path("../resources/images/")


class CodingVideo:
    capture: cv2.VideoCapture

    def __init__(self, video: Path | str):
        self.capture = cv2.VideoCapture(video)
        if not self.capture.isOpened():
            raise ValueError(f"Cannot open {video}")

        self.fps = self.capture.get(cv2.CAP_PROP_FPS)
        self.frame_count = self.capture.get(cv2.CAP_PROP_FRAME_COUNT)
        self.duration = round(self.frame_count / self.fps)

    def __str__(self) -> str:
        """Displays key metadata from the video

        Specifically, the following information is shown:
            FPS - Number of frames per second rounded to two decimal points
            FRAME COUNT - The total number of frames in the video
            DURATION (minutes) - Calculated total duration of the video given FPS and FRAME COUNT

        Reference
        ----------
        https://docs.opencv.org/3.4/d4/d15/group__videoio__flags__base.html#gaeb8dd9c89c10a5c63c139bf7c4f5704d
        """

        formatted_duration = str(round(self.duration / 60, 2)).replace(".", ":")

        return f"Total Frames: {int(self.frame_count)}, FPS: {round(self.fps)}, Duration(mm:ss): {formatted_duration}"

    def get_frame_number_at_time(self, seconds: int) -> int:
        """Given a time in seconds, returns the value of the nearest frame"""
        return round(seconds * self.fps)

    def get_frame_rgb_array(self, frame_number: int) -> np.ndarray:
        """Returns a numpy N-dimensional array (ndarray)

        The array represents the RGB values of each pixel in a given frame

        Note: cv2 defaults to BGR format, so this function converts the color space to RGB

        Reference
        ---------
        https://docs.opencv.org/3.4/db/d64/tutorial_js_colorspaces.html
        https://docs.opencv.org/3.4/d8/d01/group__imgproc__color__conversions.html#gga4e0972be5de079fed4e3a10e24ef5ef0ad3db9ff253b87d02efe4887b2f5d77ee
        https://www.geeksforgeeks.org/python/convert-bgr-and-rgb-with-python-opencv/
        """

        self.capture.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
        ok, frame_data = self.capture.read()

        frame_data = cv2.cvtColor(frame_data, cv2.COLOR_BGR2RGB)

        return frame_data

    def get_image_as_bytes(self, seconds: int) -> bytes:
        self.capture.set(cv2.CAP_PROP_POS_FRAMES, self.get_frame_number_at_time(seconds))
        ok, frame = self.capture.read()
        if not ok or frame is None:
            raise ValueError("Invalid frame in target location")
        ok, buf = cv2.imencode(".png", frame)
        if not ok:
            raise ValueError("Failed to encode frame")
        return buf.tobytes()

    def save_as_image(self, seconds: int, output_path: Path | str = 'output.png') -> None:
        """Saves the given frame as a png image

        # TODO: Requires a third-party library to convert ndarray to png
        # TODO: Identify the library and add a reference to its documentation

        Reference
        ----------
        https://pillow.readthedocs.io/en/stable/index.html
        """
        if isinstance(output_path, str):
            output_path = OUT_PATH/output_path

        frame = self.get_frame_rgb_array(self.get_frame_number_at_time(seconds))
        if frame is None:
            raise ValueError("Invalid frame in target location")

        image = Image.fromarray(frame)
        image.save(output_path)

def test():
    """Try out your class here"""
    oop = CodingVideo("../resources/oop.mp4")
    print(oop)
    oop.save_as_image(42)


if __name__ == '__main__':
    test()
