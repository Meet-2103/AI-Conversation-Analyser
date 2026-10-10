import sqlite3
from typing import List, Dict, Optional
from domain.interfaces import ITranscriptRepository
from domain.models import Transcript, Chunk
from infrastructure.logger import get_logger

logger = get_logger(__name__)

class SQLiteTranscriptRepository(ITranscriptRepository):
    def __init__(self, db_path: str = "./meet_project.db"):
        self.db_path = db_path
        self._init_db()

    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS transcripts (
                        id TEXT PRIMARY KEY,
                        expert_name TEXT NOT NULL,
                        role TEXT NOT NULL,
                        market TEXT NOT NULL,
                        raw_text TEXT NOT NULL
                    )
                """)
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS chunks (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        transcript_id TEXT NOT NULL,
                        text TEXT NOT NULL,
                        timestamp TEXT NOT NULL,
                        speaker TEXT NOT NULL,
                        chunk_index INTEGER NOT NULL,
                        FOREIGN KEY(transcript_id) REFERENCES transcripts(id)
                    )
                """)
                conn.commit()
        except sqlite3.Error as e:
            logger.error(f"Failed to initialize SQLite database: {e}")
            raise

    def save(self, transcript: Transcript, raw_text: str) -> None:
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO transcripts (id, expert_name, role, market, raw_text)
                    VALUES (?, ?, ?, ?, ?)
                """, (transcript.id, transcript.expert_name, transcript.role, transcript.market, raw_text))

                cursor.execute("DELETE FROM chunks WHERE transcript_id = ?", (transcript.id,))
                
                for i, chunk in enumerate(transcript.chunks):
                    cursor.execute("""
                        INSERT INTO chunks (transcript_id, text, timestamp, speaker, chunk_index)
                        VALUES (?, ?, ?, ?, ?)
                    """, (transcript.id, chunk.text, chunk.timestamp, chunk.speaker, i))
                
                conn.commit()
                logger.info(f"Saved transcript {transcript.id} to SQLite.")
        except sqlite3.Error as e:
            logger.error(f"Error saving transcript {transcript.id} to SQLite: {e}")
            raise

    def get_by_id(self, transcript_id: str) -> Optional[Transcript]:
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM transcripts WHERE id = ?", (transcript_id,))
                t_row = cursor.fetchone()
                
                if not t_row:
                    return None
                    
                cursor.execute("SELECT * FROM chunks WHERE transcript_id = ? ORDER BY chunk_index", (transcript_id,))
                c_rows = cursor.fetchall()
                
                chunks = [
                    Chunk(text=row['text'], timestamp=row['timestamp'], speaker=row['speaker'])
                    for row in c_rows
                ]
                
                return Transcript(
                    id=t_row['id'],
                    expert_name=t_row['expert_name'],
                    role=t_row['role'],
                    market=t_row['market'],
                    chunks=chunks,
                    raw_text=t_row['raw_text']
                )
        except sqlite3.Error as e:
            logger.error(f"Error retrieving transcript {transcript_id}: {e}")
            return None

    def get_all(self) -> List[Transcript]:
        try:
            transcripts = []
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id FROM transcripts")
                for row in cursor.fetchall():
                    t = self.get_by_id(row['id'])
                    if t:
                        transcripts.append(t)
            return transcripts
        except sqlite3.Error as e:
            logger.error(f"Error retrieving all transcripts: {e}")
            return []

    def get_raw_text(self, transcript_id: str) -> Optional[str]:
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT raw_text FROM transcripts WHERE id = ?", (transcript_id,))
                row = cursor.fetchone()
                return row['raw_text'] if row else None
        except sqlite3.Error as e:
            logger.error(f"Error getting raw text for {transcript_id}: {e}")
            return None
            
    def get_raw_text_by_expert(self, expert_name: str) -> Optional[str]:
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                # Use LIKE to handle slight variations in expert name matching
                cursor.execute("SELECT raw_text FROM transcripts WHERE expert_name LIKE ?", (f"%{expert_name}%",))
                row = cursor.fetchone()
                return row['raw_text'] if row else None
        except sqlite3.Error as e:
            logger.error(f"Error getting raw text for expert {expert_name}: {e}")
            return None

    def get_all_raw_texts(self) -> Dict[str, str]:
        try:
            result = {}
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT expert_name, raw_text FROM transcripts")
                for row in cursor.fetchall():
                    result[row['expert_name']] = row['raw_text']
            return result
        except sqlite3.Error as e:
            logger.error(f"Error getting all raw texts: {e}")
            return {}

    def count(self) -> int:
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) as count FROM transcripts")
                row = cursor.fetchone()
                return row['count']
        except sqlite3.Error as e:
            logger.error(f"Error counting transcripts: {e}")
            return 0
