"""
Moduł odpowiedzialny za scraping danych z eDziekanatu
"""
import logging
import requests
from typing import Dict, List
from bs4 import BeautifulSoup

from src.config.settings import (
    EDZIEKANAT_LOGIN_URL, 
    EDZIEKANAT_GRADE_URL,
    EDZIEKANAT_INDEX,
    EDZIEKANAT_PASSWORD
)

logger = logging.getLogger(__name__)

class GradeScraper:
    """Klasa odpowiedzialna za pobieranie ocen z dziekanatu"""
    
    def __init__(self, login_url: str = EDZIEKANAT_LOGIN_URL, 
                 grade_url: str = EDZIEKANAT_GRADE_URL,
                 index: str = EDZIEKANAT_INDEX, 
                 password: str = EDZIEKANAT_PASSWORD):
        self.login_url = login_url
        self.grade_url = grade_url
        self.index = index
        self.password = password
        self.session = requests.Session()
        
        if not all([self.login_url, self.grade_url, self.index, self.password]):
            logger.error("Brak wymaganych danych logowania do eDziekanatu")
    
    def login(self) -> bool:
        """Loguje się do systemu eDziekanat"""
        try:
            # Pobierz stronę logowania
            response = self.session.get(self.login_url)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Pobierz wartości dynamicznych pól
            viewstate = soup.find('input', {'id': '__VIEWSTATE'})['value']
            viewstategenerator = soup.find('input', {'id': '__VIEWSTATEGENERATOR'})['value']
            
            # Przygotuj dane do wysłania
            login_data = {
                '__VIEWSTATE': viewstate,
                '__VIEWSTATEGENERATOR': viewstategenerator,
                'ctl00$ctl00$ContentPlaceHolder$MiddleContentPlaceHolder$txtIdent': self.index,
                'ctl00$ctl00$ContentPlaceHolder$MiddleContentPlaceHolder$txtHaslo': self.password,
                'ctl00$ctl00$ContentPlaceHolder$MiddleContentPlaceHolder$rbKto': 'student',
                'ctl00$ctl00$ContentPlaceHolder$MiddleContentPlaceHolder$butLoguj': 'Zaloguj'
            }
            
            # Wyślij żądanie POST
            response = self.session.post(self.login_url, data=login_data)
            
            # Sprawdź czy logowanie się powiodło
            return "Wyloguj" in response.text
            
        except Exception as e:
            logger.error(f"Błąd podczas logowania do eDziekanatu: {e}")
            return False
    
    def get_grades(self) -> List[Dict[str, str]]:
        """Pobiera oceny z systemu eDziekanat"""
        if not self.login():
            logger.error("Nie udało się zalogować do eDziekanatu")
            return []
        
        try:
            # Pobierz stronę z ocenami
            response = self.session.get(self.grade_url)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Znajdź tabelę z ocenami
            grades_table = soup.find('table', {'id': 'ctl00_ctl00_ContentPlaceHolder_RightContentPlaceHolder_dgDane'})
            if not grades_table:
                logger.error("Nie znaleziono tabeli z ocenami")
                return []
            
            # Przetwórz dane z tabeli
            grades = []
            for row in grades_table.find_all('tr')[1:]:  # Pomijamy nagłówek tabeli
                cols = row.find_all('td')
                if len(cols) > 0:
                    subject = cols[0].text.strip()
                    subject_type = cols[1].text.strip()  # Pobierz typ przedmiotu
                    grade_cell = cols[5]
                    
                    # Sprawdź czy są <span class="ocena">
                    spans = grade_cell.find_all('span', class_='ocena')
                    if len(spans) == 2:
                        grade = spans[0].text.strip()
                        date = spans[1].text.strip()
                    else:
                        # Rozdziel po <br/> lub nowej linii
                        cell_text = grade_cell.get_text(separator='\n').strip()
                        parts = [p.strip() for p in cell_text.split('\n') if p.strip()]
                        if len(parts) == 2:
                            grade = parts[0]
                            date = parts[1]
                        elif len(parts) == 1:
                            grade = parts[0]
                            date = ""
                        else:
                            grade = ""
                            date = ""
                    
                    grades.append({
                        'subject': subject,
                        'subject_type': subject_type,
                        'grade': grade,
                        'date': date
                    })
            
            logger.info(f"Pobrano {len(grades)} ocen z eDziekanatu")
            return grades
            
        except Exception as e:
            logger.error(f"Błąd podczas pobierania ocen: {e}")
            return []
        finally:
            # Zawsze zamknij sesję
            self.session.close()
            
def get_grades() -> List[Dict[str, str]]:
    """Funkcja pomocnicza do pobrania ocen"""
    scraper = GradeScraper()
    return scraper.get_grades()
