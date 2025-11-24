import sqlite3
from pathlib import Path
from models.bookmark import Bookmark


class BookmarkManager:
    def __init__(self, db_path: Path, user: str):
        self.path = db_path
        self.user = user
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()

    def create_bookmarks_db(self):
        # create bookmarks table
        self.cursor.execute("CREATE TABLE IF NOT EXISTS bookmarks "
                            "(id INTEGER PRIMARY KEY, "
                            "bookmark_time INTEGER, "
                            "title TEXT)")
        # create users table
        self.cursor.execute("CREATE TABLE IF NOT EXISTS users "
                            "(user_id TEXT UNIQUE PRIMARY KEY)")
        # create video table
        self.cursor.execute("CREATE TABLE IF NOT EXISTS videos "
                            "(video_id TEXT UNIQUE PRIMARY KEY, "
                            "file_path TEXT)")
        # create user_bookmarks table
        self.cursor.execute("CREATE TABLE IF NOT EXISTS user_bookmarks "
                            "(bookmark_id INTEGER, "
                            "user_id TEXT, "
                            "video_id TEXT)")

    def load_bookmarks_for_video(self, video_id: str) -> list(Bookmark):
        self.cursor.execute(f"SELECT bookmarks.id, user_bookmarks.user_id, user_bookmarks.video_id,"
                            f" bookmarks.bookmark_time, bookmarks.title "
                            f"FROM user_bookmarks "
                            f"Inner JOIN bookmarks ON user_bookmarks.bookmark_id=bookmarks.id "
                            f"WHERE user_bookmarks.video_id = {video_id} "
                            f"AND user_bookmarks.user_id = {self.user}")
        bookmarks_data = self.cursor.fetchall()
        bookmarks = [{"id": bookmark_id, "user": user, "video": video, "time": time, "title": title} for
                     bookmark_id, user, video, time, title in bookmarks_data]
        # convert to list of Bookmark() instances
        return sorted(bookmarks, key=lambda b: b["time"])

    def get_bookmark(self, bookmark_id) -> Bookmark:
        self.cursor.execute(f"SELECT * FROM bookmarks WHERE id = {bookmark_id}")
        id, user, video, time, title = self.cursor.fetchone()
        return Bookmark(id, user, video, time, title)

    def get_user_bookmarks(self, user_id):
        self.cursor.execute(f"SELECT bookmarks.id, bookmarks.bookmark_time, bookmarks.title "
                            f"FROM user_bookmarks "
                            f"Inner JOIN bookmarks ON bookmarks.id=user_bookmarks.bookmark_id "
                            f"WHERE user_bookmarks.user_id = {self.user}")

    def add_bookmark(self, bookmark: Bookmark) -> True | None:
        pass

    def delete_bookmark(self, bookmark: Bookmark) -> True | None:
        pass