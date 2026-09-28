import sqlite3
from contextlib import closing
from datetime import datetime
from pathlib import Path


class Database:
    def __init__(self, database_path=None):
        self.path = Path(database_path) if database_path else Path(__file__).resolve().parent.parent / "book_writer.db"
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(self.path)
        self.connection.row_factory = sqlite3.Row
        tables = {r[0] for r in self.connection.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        if "chapters" in tables and "settings" not in tables:
            backup = self.path.with_name(self.path.stem + ".backup-" + datetime.now().strftime("%Y%m%d-%H%M%S-%f") + ".db")
            with closing(sqlite3.connect(backup)) as target:
                self.connection.backup(target)
        self.create_tables()

    def create_tables(self):
        with self.connection:
            self.connection.execute("""CREATE TABLE IF NOT EXISTS chapters (
                id TEXT PRIMARY KEY, title TEXT NOT NULL, text TEXT NOT NULL DEFAULT '',
                position INTEGER NOT NULL DEFAULT 0)""")
            self.connection.execute("""CREATE TABLE IF NOT EXISTS linked_items (
                id TEXT PRIMARY KEY, name TEXT NOT NULL, item_type TEXT NOT NULL)""")
            self.connection.execute("CREATE TABLE IF NOT EXISTS parts (id TEXT PRIMARY KEY, title TEXT NOT NULL, position INTEGER NOT NULL)")
            self.connection.execute("CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT NOT NULL)")
            additions = {
                "chapters": ["content_html", "part_id"],
                "linked_items": ["description", "image_path", "country", "period", "tags", "quote", "notes"],
            }
            for table, names in additions.items():
                present = {r["name"] for r in self.connection.execute(f"PRAGMA table_info({table})")}
                for name in names:
                    if name not in present:
                        self.connection.execute(f"ALTER TABLE {table} ADD COLUMN {name} TEXT NOT NULL DEFAULT ''")

    def create_chapter(self, chapter_id, title, position=None, part_id=""):
        if position is None:
            position = self.connection.execute("SELECT COALESCE(MAX(position), -1)+1 FROM chapters").fetchone()[0]
        with self.connection:
            self.connection.execute("INSERT INTO chapters (id, title, position, part_id) VALUES (?, ?, ?, ?)", (chapter_id, title, position, part_id))

    def get_chapters(self):
        return self.connection.execute("SELECT * FROM chapters ORDER BY position, rowid").fetchall()

    def update_chapter_content(self, chapter_id, text, content_html):
        with self.connection:
            self.connection.execute("UPDATE chapters SET text=?, content_html=? WHERE id=?", (text, content_html, chapter_id))

    def rename_chapter(self, chapter_id, title):
        with self.connection:
            self.connection.execute("UPDATE chapters SET title=? WHERE id=?", (title, chapter_id))

    def delete_chapter(self, chapter_id):
        with self.connection:
            self.connection.execute("DELETE FROM chapters WHERE id=?", (chapter_id,))

    def move_chapter(self, chapter_id, part_id):
        with self.connection:
            self.connection.execute("UPDATE chapters SET part_id=? WHERE id=?", (part_id, chapter_id))

    def get_parts(self):
        return self.connection.execute("SELECT * FROM parts ORDER BY position, rowid").fetchall()

    def create_part(self, part_id, title):
        with self.connection:
            self.connection.execute("INSERT INTO parts VALUES (?, ?, (SELECT COALESCE(MAX(position), -1)+1 FROM parts))", (part_id, title))

    def rename_part(self, part_id, title):
        with self.connection:
            self.connection.execute("UPDATE parts SET title=? WHERE id=?", (title, part_id))

    def delete_part(self, part_id):
        with self.connection:
            self.connection.execute("UPDATE chapters SET part_id='' WHERE part_id=?", (part_id,))
            self.connection.execute("DELETE FROM parts WHERE id=?", (part_id,))

    def create_linked_item(self, item_id, name, item_type):
        with self.connection:
            self.connection.execute("INSERT INTO linked_items (id, name, item_type) VALUES (?, ?, ?)", (item_id, name, item_type))

    def get_linked_item(self, item_id):
        return self.connection.execute("SELECT * FROM linked_items WHERE id=?", (item_id,)).fetchone()

    def get_items(self, item_type=None):
        if item_type:
            return self.connection.execute("SELECT * FROM linked_items WHERE item_type=? ORDER BY name", (item_type,)).fetchall()
        return self.connection.execute("SELECT * FROM linked_items ORDER BY name").fetchall()

    def update_item(self, item_id, values):
        allowed = {"name", "description", "image_path", "country", "period", "tags", "quote", "notes"}
        values = {k: v for k, v in values.items() if k in allowed}
        if values:
            with self.connection:
                self.connection.execute("UPDATE linked_items SET " + ", ".join(f"{k}=?" for k in values) + " WHERE id=?", (*values.values(), item_id))

    def update_linked_item_description(self, item_id, description):
        self.update_item(item_id, {"description": description})

    def setting(self, key, default=""):
        row = self.connection.execute("SELECT value FROM settings WHERE key=?", (key,)).fetchone()
        return row[0] if row else default

    def set_setting(self, key, value):
        with self.connection:
            self.connection.execute("INSERT INTO settings VALUES (?, ?) ON CONFLICT(key) DO UPDATE SET value=excluded.value", (key, str(value)))

    def close(self):
        self.connection.close()
