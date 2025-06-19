"""
Moduł zawierający mechanizmy harmonogramowania
"""
import time
import logging
import schedule
from typing import Callable
import threading

logger = logging.getLogger(__name__)

def run_scheduler(interval_minutes: int, job_function: Callable, run_once_at_start: bool = True):
    """
    Uruchamia zadanie cyklicznie co określoną liczbę minut
    
    Args:
        interval_minutes: Interwał w minutach
        job_function: Funkcja do uruchomienia
        run_once_at_start: Czy uruchomić job od razu przy starcie
    """
    if run_once_at_start:
        logger.info(f"Uruchamianie zadania po raz pierwszy...")
        job_function()
        
    logger.info(f"Harmonogram ustawiony co {interval_minutes} minut")
    schedule.every(interval_minutes).minutes.do(job_function)
    
    while True:
        schedule.run_pending()
        time.sleep(1)

def run_threaded(job_function: Callable):
    """
    Uruchamia zadanie w osobnym wątku
    
    Args:
        job_function: Funkcja do uruchomienia
    """
    job_thread = threading.Thread(target=job_function)
    job_thread.start()
