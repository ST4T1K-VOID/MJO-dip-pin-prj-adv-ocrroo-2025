import sqlite3
from pathlib import Path
import os


class BookmarkManager:
    def __init__(self, db_path: Path, user: str):
        """Initialize the bookmark manager for a specific user."""
        self.path = db_path
        self.user = user
        self.conn = sqlite3.connect(self.path, check_same_thread=False)
        self.cursor = self.conn.cursor()
        if not os.path.exists(db_path):
            self.create_bookmarks_db()


    def check_user_in_db(self):
        """Check if a user exists in the users table. If not, adds user to users table"""
        try:
            self.cursor.execute("Select * from users")
            users = self.cursor.fetchall()
            if not self.user in users:
                self.cursor.execute("INSERT INTO users (user_id) VALUES (?)", (self.user,))
                self.conn.commit()
        except sqlite3.OperationalError as e:
            print(e)

    def check_video_in_db(self, video_id):
        """Check if a user exists in the users table. If not, adds user to users table"""
        try:
            self.cursor.execute("Select video_id from videos")
            videos = self.cursor.fetchall()
            if not video_id in videos:
                self.cursor.execute("INSERT INTO videos (video_id) VALUES (?)", (video_id,))
                self.conn.commit()
        except sqlite3.OperationalError as e:
            print(e)

    def create_bookmarks_db(self):
        """Creates database tables required for BookmarkManager"""
        # create bookmarks table
        try:
            self.cursor.execute("CREATE TABLE IF NOT EXISTS bookmarks ("
                                "id INTEGER PRIMARY KEY AUTOINCREMENT, "
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
            print("Tables created successfully")
            self.conn.commit()
        except sqlite3.OperationalError as e:
            print(e)
            raise e



    def get_tables(self):
        """Returns all tables in the database.
        Returns:
            tables: any"""
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = self.cursor.fetchall()
        return tables

    def load_bookmarks_for_video(self, video_id: str):
        """Queries the database for all bookmarks for a specific video for a specific user_id.
        Returns:
            bookmarks: any"""
        try:
            self.cursor.execute(f"SELECT bookmarks.id, user_bookmarks.user_id, user_bookmarks.video_id,"
                                f" bookmarks.bookmark_time, bookmarks.title "
                                f"FROM user_bookmarks "
                                f"Inner JOIN bookmarks ON user_bookmarks.bookmark_id=bookmarks.id "
                                f"WHERE user_bookmarks.video_id = '{video_id}' "
                                f"AND user_bookmarks.user_id = '{self.user}'")
            bookmarks_data = self.cursor.fetchall()
            bookmarks = [{"id": bookmark_id, "user": user, "video": video, "time": time, "title": title} for
                         bookmark_id, user, video, time, title in bookmarks_data]
            # convert to list of Bookmark() instances
            return sorted(bookmarks, key=lambda b: b["time"])
        except sqlite3.OperationalError as e:
            print(e)
            raise e

    def get_bookmark(self, bookmark_id):
        """Returns the id, timestamp, and title for a specific bookmark id.
        Returns:
            bookmark: dict"""
        try:
            self.cursor.execute(f"SELECT * FROM bookmarks WHERE id = {bookmark_id}")
            id, time, title = self.cursor.fetchone()
            bookmark = {"id": id, "time": time, "title": title}
            return bookmark
        except sqlite3.OperationalError as e:
            print(e)
            raise e

    def get_user_bookmarks(self):
        """Returns all bookmarks for a specific user."""
        try:
            self.cursor.execute(f"SELECT bookmarks.id, bookmarks.bookmark_time, bookmarks.title "
                                f"FROM user_bookmarks "
                                f"Inner JOIN bookmarks ON bookmarks.id=user_bookmarks.bookmark_id "
                                f"WHERE user_bookmarks.user_id = '{self.user}'")
            bookmarks_data = self.cursor.fetchall()
            bookmarks = [{"id": bookmark_id, "bookmark_time": time, "title": title} for id, time, title in bookmarks_data]
            return bookmarks
        except sqlite3.OperationalError as e:
            print(e)
            raise e

    def add_bookmark(self, video_id, timestamp, title):
        """Adds a new bookmark to the database for a specific video and user."""
        try:
            self.cursor.execute(f"INSERT INTO bookmarks (bookmark_time, title) VALUES ('{timestamp}', '{title}')")
            bookmark_id = self.cursor.lastrowid
            self.cursor.execute(f"INSERT INTO user_bookmarks (bookmark_id, user_id, video_id) "
                                f"VALUES ({bookmark_id}, '{self.user}', '{video_id}')")
            self.conn.commit()
        except sqlite3.OperationalError as e:
            print(e)
            raise e

    def delete_bookmark(self, bookmark_id: int):
        """Deletes a bookmark from the database using the bookmark id"""
        try:
            self.cursor.execute(f"DELETE FROM user_bookmarks WHERE bookmark_id = {bookmark_id}")
            self.conn.commit()
            self.cursor.execute("DELETE FROM bookmarks WHERE bookmark_id = {bookmark_id}")
            self.conn.commit()
        except sqlite3.OperationalError as e:
            print(e)
            raise e
