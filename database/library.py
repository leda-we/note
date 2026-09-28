import sqlite3
import uuid
from contextlib import closing
from pathlib import Path
from database.database import Database


class Library:
    def __init__(self, root):
        self.root = Path(root).resolve()
        self.path = self.root / "data" / "library.db"
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with closing(self.connect()) as connection, connection:
            connection.execute("CREATE TABLE IF NOT EXISTS books (path TEXT PRIMARY KEY, opened TEXT NOT NULL DEFAULT '')")

    def connect(self):
        return sqlite3.connect(self.path)

    def key(self, path):
        path = Path(path).resolve()
        return path.relative_to(self.root).as_posix()

    def resolve(self, key):
        return (self.root / key).resolve()

    def register(self, path):
        with closing(self.connect()) as connection, connection:
            connection.execute("INSERT OR IGNORE INTO books(path) VALUES (?)", (self.key(path),))

    def mark_opened(self, path):
        with closing(self.connect()) as connection, connection:
            connection.execute("UPDATE books SET opened=strftime('%Y-%m-%d %H:%M:%f','now') WHERE path=?", (self.key(path),))

    def last_book(self):
        with closing(self.connect()) as connection:
            rows = connection.execute("SELECT path FROM books ORDER BY opened DESC, rowid DESC").fetchall()
        return next((self.resolve(row[0]) for row in rows if self.resolve(row[0]).is_file()), None)

    def create_book(self, title):
        path = self.root / "data" / "books" / uuid.uuid4().hex / "book.db"
        db = Database(path)
        try:
            db.set_setting("book_title", title.strip() or "Новая книга")
        finally:
            db.close()
        self.register(path)
        return path

    def books(self):
        with closing(self.connect()) as connection:
            rows = connection.execute("SELECT path, opened FROM books ORDER BY opened DESC, rowid DESC").fetchall()
        books = []
        for key, opened in rows:
            path = self.resolve(key)
            record = {"path": str(path), "title": path.stem, "words": 0, "chapters": 0, "target": 80000, "opened": opened, "available": False}
            if path.is_file():
                try:
                    with closing(sqlite3.connect(path.as_uri() + "?mode=ro", uri=True)) as db:
                        settings = dict(db.execute("SELECT key,value FROM settings"))
                        chapters = db.execute("SELECT text FROM chapters").fetchall()
                    record.update(title=settings.get("book_title", "Моя книга"), words=sum(len(row[0].split()) for row in chapters), chapters=len(chapters), target=max(1, int(settings.get("word_target", "80000"))), available=True)
                except (sqlite3.Error, ValueError):
                    pass
            books.append(record)
        return books
