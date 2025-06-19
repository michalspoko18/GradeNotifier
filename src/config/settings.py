"""
Moduł konfiguracyjny aplikacji GradeNotifier
"""
import os
from dotenv import load_dotenv

# Załaduj zmienne środowiskowe
load_dotenv(override=True)

# Konfiguracja eDziekanatu
EDZIEKANAT_LOGIN_URL = os.getenv('LOGIN_URL', 'https://edziekanat.zut.edu.pl/WU/')
EDZIEKANAT_GRADE_URL = os.getenv('GRADE_URL', 'https://edziekanat.zut.edu.pl/WU/OcenyP.aspx')
EDZIEKANAT_INDEX = os.getenv('ZUT_INDEX')
EDZIEKANAT_PASSWORD = os.getenv('ZUT_PASSWORD')

# Konfiguracja Discord
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
DISCORD_USER_ID = os.getenv('DISCORD_USER_ID')

# Konfiguracja bazy danych
DB_PATH = os.getenv('DB_PATH', 'grades.db')

# Konfiguracja logów
LOG_PATH = os.getenv('LOG_PATH', 'gradenotifier.log')

# Konfiguracja cron
CRON_SCHEDULE = os.getenv('CRON_SCHEDULE', '15')  # Co 15 minut
