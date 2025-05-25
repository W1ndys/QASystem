import sqlite3
from typing import List, Tuple, Optional


class QADatabaseManager:
    def __init__(self, db_path: str = "qa_data.db"):
        self.db_path = db_path
        self._create_table()

    def _create_table(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS qa_pairs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    question TEXT NOT NULL,
                    answer TEXT NOT NULL
                )
            """
            )
            conn.commit()

    def add_qa_pair(self, question: str, answer: str) -> Optional[int]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO qa_pairs (question, answer) VALUES (?, ?)",
                (question, answer),
            )
            conn.commit()
            return cursor.lastrowid

    def get_qa_pair(self, qa_id: int) -> Optional[Tuple[int, str, str]]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, question, answer FROM qa_pairs WHERE id = ?", (qa_id,)
            )
            return cursor.fetchone()

    def get_all_qa_pairs(self) -> List[Tuple[int, str, str]]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, question, answer FROM qa_pairs")
            return cursor.fetchall()

    def update_qa_pair(self, qa_id: int, question: str, answer: str) -> bool:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE qa_pairs SET question = ?, answer = ? WHERE id = ?",
                (question, answer, qa_id),
            )
            conn.commit()
            return cursor.rowcount > 0

    def delete_qa_pair(self, qa_id: int) -> bool:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM qa_pairs WHERE id = ?", (qa_id,))
            conn.commit()
            return cursor.rowcount > 0
