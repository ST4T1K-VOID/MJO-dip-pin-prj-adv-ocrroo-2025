class Bookmark:
    def __init__(self, id: int, user: str, video_id: str, timestamp: int, title: str):
        self.id = id
        self.user = user
        self.video_id = video_id
        self.timestamp = timestamp
        self.title = title