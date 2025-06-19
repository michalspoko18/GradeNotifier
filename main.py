"""
GradeNotifier - główny moduł aplikacji
Aplikacja automatycznie sprawdzająca i powiadamiająca o nowych ocenach z dziekanatu
"""
import logging
import os
import sys
from typing import Dict, List

# Importowanie modułów
from src.config.settings import CRON_SCHEDULE, LOG_PATH

# Konfiguracja logowania
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_PATH),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)
from src.database.db_manager import Database
from src.scraper.edziekanat_scraper import get_grades
from src.notifications.discord_notifier import notify_new_grades

def check_for_new_grades() -> None:
    """
    Główna funkcja sprawdzająca nowe oceny i wysyłająca powiadomienia
    """
    logger.info("Rozpoczynam sprawdzanie nowych ocen...")
    
    # Krok 1: Pobierz oceny z eDziekanat
    scraped_grades = get_grades()
    
    if not scraped_grades:
        logger.warning("Nie udało się pobrać ocen lub brak ocen do przetworzenia")
        return
        
    logger.info(f"Pobrano {len(scraped_grades)} ocen z eDziekanatu")
    
    # Krok 2: Zapisz oceny do bazy danych i wykryj nowe
    db = Database()
    new_grades = db.save_grade_data(scraped_grades)
    
    # Krok 3: Wyślij powiadomienia o nowych ocenach
    if new_grades:
        logger.info(f"Wykryto {len(new_grades)} nowych ocen, wysyłam powiadomienie...")
        success = notify_new_grades(new_grades)
        
        if success:
            logger.info("Powiadomienie wysłane pomyślnie")
        else:
            logger.error("Nie udało się wysłać powiadomienia")
    else:
        logger.info("Brak nowych ocen")
def run_scheduled():
    """
    Uruchamia harmonogram sprawdzania ocen
    """
    try:
        from src.utils.scheduler import run_scheduler
        
        # Obsługuje wartość cron_schedule jako liczbę minut
        try:
            interval = int(CRON_SCHEDULE)
            logger.info(f"Uruchamianie harmonogramu co {interval} minut")
            run_scheduler(interval, check_for_new_grades)
        except ValueError as e:
            logger.error(f"Nieprawidłowa wartość CRON_SCHEDULE: {CRON_SCHEDULE}. Powinna być liczbą całkowitą (minut).")
            sys.exit(1)
    except ImportError:
        logger.error("Nie znaleziono modułu schedule. Zainstaluj go używając: pip install schedule")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Błąd podczas uruchamiania harmonogramu: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # Sprawdź argumenty wiersza poleceń
    if len(sys.argv) > 1 and sys.argv[1] == "--once":
        # Uruchom pojedyncze sprawdzenie
        check_for_new_grades()
    else:
        # Uruchom w trybie harmonogramu
        run_scheduled()