import sqlite3
from pathlib import Path

class Database:
    def __init__(self):
        project_dir = Path(__file__).resolve().parent.parent

        data_dir = project_dir
        data_dir.mkdir(exist_ok=True)

        database_path = data_dir / "book_writer.db"

        self.connection = sqlite3.connect(database_path)
        self.connection.row_factory = sqlite3.Row

        self.create_tables()

    def create_tables(self):
        cursor = self.connection.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chapters (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            text TEXT NOT NULL DEFAULT '',
            position INTEGE NOT NULL DEFAULT 0
            )
        """)

        cursor.execute("""PRAGMA table_info(chapters)""")
        columns = {
            row["name"]
            for row in cursor.fetchall()
        }
        if "content_html" not in columns:
            cursor.execute("""
                ALTER TABLE chapters
                ADD COLUMN content_html TEXT NOT NULL DEFAULT ''
            """)
        cursor.execute(
        """CREATE TABLE IF NOT EXISTS linked_items(
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            item_type TEXT NOT NULL
            )
        """
        )
        cursor.execute("""PRAGMA table_info(linked_items)""")
        linked_columns = {row["name"] for row in cursor.fetchall()}
        if "description" not in linked_columns:
            cursor.execute("""
                ALTER TABLE linked_items
                ADD COLUMN description TEXT NOT NULL DEFAULT ''
            """)

        self.connection.commit()

    def create_chapter(self, chapter_id, title, position):
        cursor = self.connection.cursor()
        cursor.execute(
            """
            INSERT INTO chapters (id, title, text, position)
            VALUES (?, ?, ?, ?)
            """,
            (
                chapter_id,
                title,
                "",
                position,
            )
        )
        self.connection.commit()

    def update_chapter_content(self, chapter_id, text, content_html):
        cursor = self.connection.cursor()
        cursor.execute(
        """UPDATE chapters
        SET text = ?, content_html = ?
        WHERE id = ?
        """,
        (
            text, content_html, chapter_id,
        )
        )
        self.connection.commit()

    def rename_chapter(self, chapter_id, new_title):
        cursor = self.connection.cursor()

        cursor.execute(
        """UPDATE chapters
        SET title = ?
        WHERE id = ?
        """,
        (
            new_title,
            chapter_id,
        )
        )
        self.connection.commit()

    def delete_chapter(self, chapter_id):
        cursor = self.connection.cursor()

        cursor.execute(
        """ DELETE FROM chapters
        WHERE id = ?
        """,
        (chapter_id,)
        )
        self.connection.commit()

    def get_chapters(self):
        cursor = self.connection.cursor()

        cursor.execute("""
        SELECT id, title, text, content_html, position
        FROM chapters
        ORDER BY position
        """)
        return cursor.fetchall()

    def create_linked_item(self, item_id, name, item_type):
        cursor = self.connection.cursor()
        cursor.execute(
        """INSERT INTO linked_items (id, name, item_type)
        VALUES (?, ?, ?)
        """,
        (
            item_id, name, item_type,
        )
        )
        self.connection.commit()

    def get_linked_item(self, item_id):
        cursor = self.connection.cursor()

        cursor.execute(
        """
        SELECT id, name, item_type, description
        FROM linked_items
        WHERE id = ?
        """,
        (item_id,)
        )
        return cursor.fetchone()

    def update_linked_item_description(self, item_id, description):
        cursor = self.connection.cursor()
        cursor.execute(
        """
        UPDATE linked_items
        SET description = ?
        WHERE id = ?
        """,
        (description, item_id,)
        )
        self.connection.commit()