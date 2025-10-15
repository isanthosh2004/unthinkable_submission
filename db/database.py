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
    
    def _ensure_db_directory(self):
        """Ensure database directory exists"""
        db_dir = os.path.dirname(self.db_path)
        if not os.path.exists(db_dir):
            os.makedirs(db_dir)
    
    def _init_database(self):
        """Initialize database schema"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Create reports table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS reports (
                        id TEXT PRIMARY KEY,
                        files TEXT NOT NULL,
                        pdf_path TEXT NOT NULL,
                        review_content TEXT NOT NULL,
                        metadata TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Create indexes for better performance
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_reports_created_at 
                    ON reports(created_at)
                ''')
                
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_reports_files 
                    ON reports(files)
                ''')
                
                conn.commit()
                
        except sqlite3.Error as e:
            raise Exception(f"Failed to initialize database: {str(e)}")
    
    def save_report(self, files: List[str], pdf_path: str, 
                   review_content: str, metadata: Dict[str, Any]) -> str:
        """
        Save a new code review report to the database
        
        Args:
            files: List of file names that were reviewed
            pdf_path: Path to the generated PDF file
            review_content: The review content (markdown)
            metadata: Additional metadata about the review
            
        Returns:
            Report ID
        """
        try:
            report_id = str(uuid.uuid4())
            files_str = ', '.join(files)
            metadata_str = json.dumps(metadata) if metadata else None
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO reports (id, files, pdf_path, review_content, metadata)
                    VALUES (?, ?, ?, ?, ?)
                ''', (report_id, files_str, pdf_path, review_content, metadata_str))
                
                conn.commit()
                
            return report_id
            
        except sqlite3.Error as e:
            raise Exception(f"Failed to save report: {str(e)}")
    
    def get_report(self, report_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific report by ID
        
        Args:
            report_id: The report ID
            
        Returns:
            Report data dictionary or None if not found
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT id, files, pdf_path, review_content, metadata, created_at, updated_at
                    FROM reports WHERE id = ?
                ''', (report_id,))
                
                row = cursor.fetchone()
                
                if row:
                    return self._row_to_dict(row)
                
                return None
                
        except sqlite3.Error as e:
            raise Exception(f"Failed to get report: {str(e)}")
    
    def get_all_reports(self, limit: Optional[int] = None, 
                       offset: int = 0) -> List[Dict[str, Any]]:
        """
        Get all reports with optional pagination
        
        Args:
            limit: Maximum number of reports to return
            offset: Number of reports to skip
            
        Returns:
            List of report dictionaries
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                query = '''
                    SELECT id, files, pdf_path, review_content, metadata, created_at, updated_at
                    FROM reports 
                    ORDER BY created_at DESC
                '''
                
                params = []
                if limit:
                    query += ' LIMIT ?'
                    params.append(limit)
                
                if offset:
                    query += ' OFFSET ?'
                    params.append(offset)
                
                cursor.execute(query, params)
                rows = cursor.fetchall()
                
                return [self._row_to_dict(row) for row in rows]
                
        except sqlite3.Error as e:
            raise Exception(f"Failed to get reports: {str(e)}")
    
    def search_reports(self, search_term: str) -> List[Dict[str, Any]]:
        """
        Search reports by filename or content
        
        Args:
            search_term: Search term to look for
            
        Returns:
            List of matching report dictionaries
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT id, files, pdf_path, review_content, metadata, created_at, updated_at
                    FROM reports 
                    WHERE files LIKE ? OR review_content LIKE ?
                    ORDER BY created_at DESC
                ''', (f'%{search_term}%', f'%{search_term}%'))
                
                rows = cursor.fetchall()
                return [self._row_to_dict(row) for row in rows]
                
        except sqlite3.Error as e:
            raise Exception(f"Failed to search reports: {str(e)}")
    
    def update_report(self, report_id: str, **kwargs) -> bool:
        """
        Update a report's metadata
        
        Args:
            report_id: The report ID
            **kwargs: Fields to update
            
        Returns:
            True if update was successful
        """
        try:
            if not kwargs:
                return False
            
            # Build dynamic update query
            set_clauses = []
            params = []
            
            for key, value in kwargs.items():
                if key in ['files', 'pdf_path', 'review_content', 'metadata']:
                    set_clauses.append(f"{key} = ?")
                    if key == 'metadata' and isinstance(value, dict):
                        params.append(json.dumps(value))
                    else:
                        params.append(value)
            
            if not set_clauses:
                return False
            
            # Add updated_at timestamp
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
        """
        Delete a report from the database
        
        Args:
            report_id: The report ID
            
        Returns:
            True if deletion was successful
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('DELETE FROM reports WHERE id = ?', (report_id,))
                conn.commit()
                
                return cursor.rowcount > 0
                
        except sqlite3.Error as e:
            raise Exception(f"Failed to delete report: {str(e)}")
    
    def get_reports_count(self) -> int:
        """
        Get total number of reports in the database
        
        Returns:
            Total count of reports
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT COUNT(*) FROM reports')
                return cursor.fetchone()[0]
                
        except sqlite3.Error as e:
            raise Exception(f"Failed to get reports count: {str(e)}")
    
    def get_reports_by_date_range(self, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """
        Get reports within a date range
        
        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            
        Returns:
            List of report dictionaries
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT id, files, pdf_path, review_content, metadata, created_at, updated_at
                    FROM reports 
                    WHERE DATE(created_at) BETWEEN ? AND ?
                    ORDER BY created_at DESC
                ''', (start_date, end_date))
                
                rows = cursor.fetchall()
                return [self._row_to_dict(row) for row in rows]
                
        except sqlite3.Error as e:
            raise Exception(f"Failed to get reports by date range: {str(e)}")
    
    def _row_to_dict(self, row: tuple) -> Dict[str, Any]:
        """Convert database row to dictionary"""
        try:
            metadata = json.loads(row[4]) if row[4] else {}
        except (json.JSONDecodeError, TypeError):
            metadata = {}
        
        return {
            'id': row[0],
            'files': row[1],
            'pdf_path': row[2],
            'review_content': row[3],
            'metadata': metadata,
            'created_at': row[5],
            'updated_at': row[6]
        }
    
    def cleanup_old_reports(self, days_old: int = 30) -> int:
        """
        Clean up old reports and their PDF files
        
        Args:
            days_old: Number of days after which to delete reports
            
        Returns:
            Number of reports deleted
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get old reports
                cursor.execute('''
                    SELECT id, pdf_path FROM reports 
                    WHERE created_at < datetime('now', '-{} days')
                '''.format(days_old))
                
                old_reports = cursor.fetchall()
                deleted_count = 0
                
                for report_id, pdf_path in old_reports:
                    # Delete PDF file if it exists
                    if os.path.exists(pdf_path):
                        try:
                            os.remove(pdf_path)
                        except OSError:
                            pass  # Continue even if file deletion fails
                    
                    # Delete database record
                    cursor.execute('DELETE FROM reports WHERE id = ?', (report_id,))
                    deleted_count += 1
                
                conn.commit()
                return deleted_count
                
        except sqlite3.Error as e:
            raise Exception(f"Failed to cleanup old reports: {str(e)}")
    
    def get_database_stats(self) -> Dict[str, Any]:
        """
        Get database statistics
        
        Returns:
            Dictionary with database statistics
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get total reports count
                cursor.execute('SELECT COUNT(*) FROM reports')
                total_reports = cursor.fetchone()[0]
                
                # Get oldest and newest reports
                cursor.execute('''
                    SELECT MIN(created_at), MAX(created_at) FROM reports
                ''')
                oldest, newest = cursor.fetchone()
                
                # Get database file size
                db_size = os.path.getsize(self.db_path) if os.path.exists(self.db_path) else 0
                
                return {
                    'total_reports': total_reports,
                    'oldest_report': oldest,
                    'newest_report': newest,
                    'database_size_bytes': db_size,
                    'database_size_mb': round(db_size / (1024 * 1024), 2)
                }
                
        except sqlite3.Error as e:
            raise Exception(f"Failed to get database stats: {str(e)}")

