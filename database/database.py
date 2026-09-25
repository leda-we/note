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

    def update_chapter_text(self, chapter_id, text):
        cursor = self.connection.cursor()
        cursor.execute(
            """
            UPDATE chapters
            SET text = ?
            WHERE id = ?
            """,
            (
                text,
                chapter_id,
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
        SELECT id, title, text, position
        FROM chapters
        ORDER BY position
        """)
        return cursor.fetchall()
        
