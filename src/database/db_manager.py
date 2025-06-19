"""
Moduł odpowiedzialny za zarządzanie bazą danych
"""
import os
import sqlite3
import logging
from typing import Dict, List, Optional, Any

from src.config.settings import DB_PATH

logger = logging.getLogger(__name__)

class Database:
    """Klasa obsługująca operacje bazodanowe"""
    
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._ensure_database_exists()
    
    def _ensure_database_exists(self) -> None:
        """Upewnia się, że baza danych istnieje, jeśli nie - tworzy tabele"""
        if not os.path.exists(self.db_path):
            self._initialize_database()
    
    def _initialize_database(self) -> None:
        """Inicjalizuje bazę danych, tworząc wymagane tabele"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Tworzenie tabeli przedmiotów
        c.execute('''
            CREATE TABLE IF NOT EXISTS subjects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE
            )
        ''')
        
        # Tworzenie tabeli ocen
        c.execute('''
            CREATE TABLE IF NOT EXISTS grades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                subject_id INTEGER,
                subject_type TEXT,
                grade TEXT,
                date TEXT,
                FOREIGN KEY (subject_id) REFERENCES subjects (id),
                UNIQUE (subject_id, subject_type, grade, date)
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("Inicjalizacja bazy danych zakończona pomyślnie")
    
    def get_connection(self) -> sqlite3.Connection:
        """Zwraca połączenie do bazy danych"""
        self._ensure_database_exists()
        conn = sqlite3.connect(self.db_path)
        return conn
    
    def get_recent_grades(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Pobiera ostatnie oceny z bazy danych"""
        conn = self.get_connection()
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        
        try:
            c.execute('''
                SELECT s.name, g.subject_type, g.grade, g.date
                FROM grades g
                JOIN subjects s ON g.subject_id = s.id
                ORDER BY g.id DESC
                LIMIT ?
            ''', (limit,))
            
            result = [dict(row) for row in c.fetchall()]
        except sqlite3.OperationalError as e:
            logger.error(f"Błąd podczas pobierania ocen: {e}")
            result = []
        
        conn.close()
        return result
    
    def save_grade_data(self, grades_data: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """
        Zapisuje dane ocen do bazy danych
        Zwraca listę nowych ocen, które zostały dodane do bazy
        """
        if not grades_data:
            return []
            
        conn = self.get_connection()
        c = conn.cursor()
        
        # Lista nowych ocen
        new_grades = []
        
        for grade_data in grades_data:
            subject_name = grade_data['subject']
            grade_value = grade_data.get('grade', '')
            grade_date = grade_data.get('date', '')
            subject_type = grade_data.get('subject_type', '')
            
            # Pomijamy oceny puste
            if not grade_value:
                continue
            
            # Sprawdź czy przedmiot istnieje, jeśli nie - dodaj
            c.execute('SELECT id FROM subjects WHERE name = ?', (subject_name,))
            subject_result = c.fetchone()
            
            if subject_result:
                subject_id = subject_result[0]
            else:
                c.execute('INSERT INTO subjects (name) VALUES (?)', (subject_name,))
                subject_id = c.lastrowid
            
            # Próba dodania oceny (zadziała tylko dla nowych ocen dzięki UNIQUE)
            try:
                c.execute(
                    'INSERT INTO grades (subject_id, subject_type, grade, date) VALUES (?, ?, ?, ?)',
                    (subject_id, subject_type, grade_value, grade_date)
                )
                
                # Jeśli dotarliśmy tutaj, to znaczy że dodano nową ocenę
                if c.rowcount > 0:
                    new_grades.append({
                        'subject': subject_name,
                        'subject_type': subject_type,
                        'grade': grade_value,
                        'date': grade_date
                    })
                    
            except sqlite3.IntegrityError:
                # Ocena już istnieje, ignorujemy
                pass
        
        conn.commit()
        conn.close()
        
        if new_grades:
            logger.info(f"Dodano {len(new_grades)} nowych ocen")
            
        return new_grades
