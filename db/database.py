"""
Database Management Service for Code Review Assistant
Handles SQLite database operations for storing report metadata and content
"""

import sqlite3
import os
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
import uuid


class DatabaseManager:
    """Manages SQLite database operations for code review reports"""

    def __init__(self, db_path: str = "db/code_reviews.db"):
        """
        Initialize database manager

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self._ensure_db_directory()
        self._init_database()

    # -------------------------------------------------------------------------
    # 📁 Setup & Schema Management
    # -------------------------------------------------------------------------
    def _ensure_db_directory(self):
        """Ensure database directory exists"""
        db_dir = os.path.dirname(self.db_path)
        if not os.path.exists(db_dir):
            os.makedirs(db_dir)

    def _init_database(self):
        """Initialize or migrate database schema"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Create reports table (fresh DBs)
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS reports (
                        id TEXT PRIMARY KEY,
                        username TEXT NOT NULL,
                        files TEXT NOT NULL,
                        pdf_path TEXT NOT NULL,
                        review_content TEXT NOT NULL,
                        metadata TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')

                # 🧩 Schema Migration Check — Ensure "username" column exists
                cursor.execute("PRAGMA table_info(reports)")
                columns = [row[1] for row in cursor.fetchall()]

                if "username" not in columns:
                    print("🧩 Migrating database: Adding missing 'username' column...")
                    cursor.execute("ALTER TABLE reports ADD COLUMN username TEXT DEFAULT 'unknown'")
                    cursor.execute(
                        "UPDATE reports SET username = 'unknown' WHERE username IS NULL OR username = ''"
                    )
                    conn.commit()
                    print("✅ Migration complete: Added 'username' column.")

                # Create indexes for performance
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_reports_created_at ON reports(created_at)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_reports_files ON reports(files)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_reports_username ON reports(username)')

                conn.commit()

        except sqlite3.Error as e:
            raise Exception(f"Failed to initialize database: {str(e)}")

    # -------------------------------------------------------------------------
    # 💾 CRUD Operations
    # -------------------------------------------------------------------------
    def save_report(
        self,
        username: str,
        files: List[str],
        pdf_path: str,
        review_content: str,
        metadata: Dict[str, Any],
    ) -> str:
        """Save a new code review report"""
        try:
            report_id = str(uuid.uuid4())
            files_str = ", ".join(files)
            metadata_str = json.dumps(metadata) if metadata else None

            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    '''
                    INSERT INTO reports (id, username, files, pdf_path, review_content, metadata)
                    VALUES (?, ?, ?, ?, ?, ?)
                    ''',
                    (report_id, username, files_str, pdf_path, review_content, metadata_str),
                )
                conn.commit()
            return report_id

        except sqlite3.Error as e:
            raise Exception(f"Failed to save report: {str(e)}")

    def get_report(self, report_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific report by ID"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT id, username, files, pdf_path, review_content, metadata, created_at, updated_at
                    FROM reports WHERE id = ?
                ''', (report_id,))
                row = cursor.fetchone()
                return self._row_to_dict(row) if row else None
        except sqlite3.Error as e:
            raise Exception(f"Failed to get report: {str(e)}")

    def get_all_reports(self, limit: Optional[int] = None, offset: int = 0) -> List[Dict[str, Any]]:
        """Get all reports with optional pagination"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                query = '''
                    SELECT id, username, files, pdf_path, review_content, metadata, created_at, updated_at
                    FROM reports ORDER BY created_at DESC
                '''
                params = []
                if limit:
                    query += " LIMIT ?"
                    params.append(limit)
                if offset:
                    query += " OFFSET ?"
                    params.append(offset)
                cursor.execute(query, params)
                return [self._row_to_dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            raise Exception(f"Failed to get reports: {str(e)}")

    def get_reports_for_user(self, username: str) -> List[Dict[str, Any]]:
        """Get all reports created by a specific user"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT id, username, files, pdf_path, review_content, metadata, created_at, updated_at
                    FROM reports WHERE username = ? ORDER BY created_at DESC
                ''', (username,))
                return [self._row_to_dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            raise Exception(f"Failed to get reports for user {username}: {str(e)}")

    def search_reports(self, search_term: str) -> List[Dict[str, Any]]:
        """Search reports by filename, content, or username"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT id, username, files, pdf_path, review_content, metadata, created_at, updated_at
                    FROM reports
                    WHERE username LIKE ? OR files LIKE ? OR review_content LIKE ?
                    ORDER BY created_at DESC
                ''', (f"%{search_term}%", f"%{search_term}%", f"%{search_term}%"))
                return [self._row_to_dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            raise Exception(f"Failed to search reports: {str(e)}")

    def update_report(self, report_id: str, **kwargs) -> bool:
        """Update a report record"""
        try:
            if not kwargs:
                return False

            set_clauses, params = [], []
            for key, value in kwargs.items():
                if key in ["username", "files", "pdf_path", "review_content", "metadata"]:
                    set_clauses.append(f"{key} = ?")
                    params.append(json.dumps(value) if key == "metadata" and isinstance(value, dict) else value)

            if not set_clauses:
                return False

            set_clauses.append("updated_at = CURRENT_TIMESTAMP")
            params.append(report_id)
            query = f"UPDATE reports SET {', '.join(set_clauses)} WHERE id = ?"

            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                conn.commit()
                return cursor.rowcount > 0
        except sqlite3.Error as e:
            raise Exception(f"Failed to update report: {str(e)}")

    def delete_report(self, report_id: str) -> bool:
        """Delete a report from the database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM reports WHERE id = ?", (report_id,))
                conn.commit()
                return cursor.rowcount > 0
        except sqlite3.Error as e:
            raise Exception(f"Failed to delete report: {str(e)}")

    def get_reports_count(self) -> int:
        """Get total number of reports"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM reports")
                return cursor.fetchone()[0]
        except sqlite3.Error as e:
            raise Exception(f"Failed to get reports count: {str(e)}")

    def get_reports_by_date_range(self, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """Get reports within a date range"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT id, username, files, pdf_path, review_content, metadata, created_at, updated_at
                    FROM reports
                    WHERE DATE(created_at) BETWEEN ? AND ?
                    ORDER BY created_at DESC
                ''', (start_date, end_date))
                return [self._row_to_dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            raise Exception(f"Failed to get reports by date range: {str(e)}")

    # -------------------------------------------------------------------------
    # 🧹 Maintenance & Analytics
    # -------------------------------------------------------------------------
    def cleanup_old_reports(self, days_old: int = 30) -> int:
        """Remove reports older than N days"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(f'''
                    SELECT id, pdf_path FROM reports
                    WHERE created_at < datetime('now', '-{days_old} days')
                ''')
                old_reports = cursor.fetchall()
                deleted_count = 0
                for report_id, pdf_path in old_reports:
                    if os.path.exists(pdf_path):
                        try:
                            os.remove(pdf_path)
                        except OSError:
                            pass
                    cursor.execute("DELETE FROM reports WHERE id = ?", (report_id,))
                    deleted_count += 1
                conn.commit()
                return deleted_count
        except sqlite3.Error as e:
            raise Exception(f"Failed to cleanup old reports: {str(e)}")

    def get_database_stats(self) -> Dict[str, Any]:
        """Return database size and report stats"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM reports")
                total_reports = cursor.fetchone()[0]
                cursor.execute("SELECT MIN(created_at), MAX(created_at) FROM reports")
                oldest, newest = cursor.fetchone()
                db_size = os.path.getsize(self.db_path) if os.path.exists(self.db_path) else 0
                return {
                    "total_reports": total_reports,
                    "oldest_report": oldest,
                    "newest_report": newest,
                    "database_size_bytes": db_size,
                    "database_size_mb": round(db_size / (1024 * 1024), 2)
                }
        except sqlite3.Error as e:
            raise Exception(f"Failed to get database stats: {str(e)}")

    # -------------------------------------------------------------------------
    # 🔁 Utilities
    # -------------------------------------------------------------------------
    def _row_to_dict(self, row: tuple) -> Dict[str, Any]:
        """Convert DB row to dictionary"""
        try:
            metadata = json.loads(row[5]) if row[5] else {}
        except (json.JSONDecodeError, TypeError):
            metadata = {}

        return {
            "id": row[0],
            "username": row[1],
            "files": row[2],
            "pdf_path": row[3],
            "review_content": row[4],
            "metadata": metadata,
            "created_at": row[6],
            "updated_at": row[7],
        }
