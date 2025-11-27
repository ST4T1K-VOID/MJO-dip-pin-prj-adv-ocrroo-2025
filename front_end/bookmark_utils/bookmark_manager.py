"""
managed the bookmark database
comprised of the tables: users, videos, bookmarks and user_bookmarks (pivot)
"""

import sqlite3
from pathlib import Path
import os

class BookmarkManager:
    """
    class for managing the bookmarks, users and videos
    """
    def __init__(self, db_path: Path, user: str):
        """Initialize the bookmark manager for a specific user."""
        self.path = db_path
        self.user = user
        self.conn = sqlite3.connect(self.path, check_same_thread=False)
        self.cursor = None
        if not os.path.exists(db_path):
            self.create_bookmarks_db()

    def check_user_in_db(self):
        """Check if a user exists in the users table. If not, adds user to users table"""
        self.open_connection()

        query = self.cursor.execute("Select user_id from users Where user_id = ?",
                                    (self.user,)).fetchone()

        if not query:
            # if fetch result = None/empty list
            try:
                self.cursor.execute("INSERT INTO users (user_id) VALUES (?)", (self.user,))
                self.conn.commit()
            except sqlite3.OperationalError as e:
                print(e)
                raise e

        self.close_connection()


    def check_video_in_db(self, video_id):
        """Check if a video exists in the videos table.
        If not, adds the video to videos table"""
        self.open_connection()

        query = self.cursor.execute("SELECT video_id FROM videos WHERE video_id = ?",
                                    (video_id,)).fetchone()

        if not query:
            # if fetch result = None/empty list
            try:
                self.cursor.execute("INSERT INTO videos (video_id) VALUES (?)",
                                    (video_id,))
                self.conn.commit()
            except sqlite3.OperationalError as e:
                print(e)

        self.close_connection()


    def create_bookmarks_db(self):
        """Creates database tables required for BookmarkManager"""
        # create bookmarks table
        self.open_connection()
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
        finally:
            self.close_connection()


    def get_tables(self):
        """Returns all tables in the database.
        Returns:
            tables: any"""
        self.open_connection()

        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = self.cursor.fetchall()

        self.close_connection()
        return tables


    def load_bookmarks_for_video(self, video_id: str):
        """Queries the database for all bookmarks for a specific video for a specific user_id.
        Returns:
            bookmarks: any"""
        self.open_connection()
        try:
            self.cursor.execute(f"SELECT bookmarks.id,"
                                f" user_bookmarks.user_id,"
                                f" user_bookmarks.video_id,"
                                f" bookmarks.bookmark_time,"
                                f" bookmarks.title "

                                f"FROM user_bookmarks "
                                f"Inner JOIN bookmarks"
                                f" ON user_bookmarks.bookmark_id=bookmarks.id "

                                f"WHERE user_bookmarks.video_id = '{video_id}'"
                                f"AND user_bookmarks.user_id = '{self.user}'")

            bookmarks_data = self.cursor.fetchall()
            bookmarks = [{"id": bookmark_id, "user": user, "video": video,
                          "time": time, "title": title} for
                          bookmark_id, user, video, time, title in bookmarks_data]
            # convert to list of Bookmark() instances
            return sorted(bookmarks, key=lambda b: b["time"])
        except sqlite3.OperationalError as e:
            print(e)
            raise e
        finally:
            self.close_connection()

    def get_bookmark(self, bookmark_id):
        """Returns the id, timestamp, and title for a specific bookmark id.
        Returns:
            bookmark: dict"""
        self.open_connection()
        try:
            self.cursor.execute(f"SELECT * FROM bookmarks WHERE id = {bookmark_id}")
            bookmark_id, time, title = self.cursor.fetchone()
            bookmark = {"id": bookmark_id, "time": time, "title": title}
            return bookmark
        except sqlite3.OperationalError as e:
            print(e)
            raise e
        finally:
            self.close_connection()

    def get_user_bookmarks(self):
        """Returns all bookmarks for a specific user."""
        self.open_connection()
        try:
            self.cursor.execute(f"SELECT bookmarks.id, bookmarks.bookmark_time,"
                                f" bookmarks.title "
                                f""
                                f"FROM user_bookmarks "
                                f"Inner JOIN bookmarks ON bookmarks.id=user_bookmarks.bookmark_id "
                                f""
                                f"WHERE user_bookmarks.user_id = '{self.user}'")

            bookmarks_data = self.cursor.fetchall()
            bookmarks = [{"id": bookmark_id,
                          "bookmark_time": time,
                          "title": title} for id, time, title in
                         bookmarks_data]
            return bookmarks
        except sqlite3.OperationalError as e:
            print(e)
            raise e
        finally:
            self.close_connection()


    def add_bookmark(self, video_id, timestamp, title):
        """Adds a new bookmark to the database for a specific video and user."""
        self.open_connection()
        try:
            self.cursor.execute(f"INSERT INTO bookmarks (bookmark_time, title)"
                                f" VALUES ('{timestamp}', '{title}')")
            bookmark_id = self.cursor.lastrowid
            self.cursor.execute(f"INSERT INTO user_bookmarks (bookmark_id, user_id, video_id) "
                                f"VALUES ({bookmark_id}, '{self.user}', '{video_id}')")
            self.conn.commit()
        except sqlite3.OperationalError as e:
            print(e)
            raise e
        finally:
            self.close_connection()


    def delete_bookmark(self, bookmark_id: int):
        """Deletes a bookmark from the database using the bookmark id"""
        self.open_connection()
        try:
            self.cursor.execute(f"DELETE FROM user_bookmarks WHERE bookmark_id = {bookmark_id}")
            self.conn.commit()
            self.cursor.execute("DELETE FROM bookmarks WHERE bookmark_id = {bookmark_id}")
            self.conn.commit()
        except sqlite3.OperationalError as e:
            print(e)
            raise e
        finally:
            self.close_connection()


    def open_connection(self):
        """open database connection and set cursor"""
        self.conn = sqlite3.connect(self.path, check_same_thread=False)
        self.cursor = self.conn.cursor()

    def close_connection(self):
        """close cursor and database connection"""
        self.cursor.close()
        self.conn.close()
