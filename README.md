# GradeNotifier - System Powiadomień o Ocenach

Aplikacja automatycznie sprawdzająca i powiadamiająca o nowych ocenach z dziekanatu.

## Opis

System automatycznie łączy się z dziekanatem co 15 minut, pobiera oceny i wysyła powiadomienia bezpośrednio do użytkownika Discord jako wiadomość prywatną, gdy pojawi się nowa ocena.

### Funkcje

- Automatyczne pobieranie ocen z systemu dziekanatowego
- Przechowywanie ocen w lokalnej bazie danych SQLite
- Wykrywanie nowych ocen
- Powiadamianie o nowych ocenach przez prywatne wiadomości Discord

## Wymagania

- Python 3.7+
- BeautifulSoup4
- Requests
- Discord.py
- SQLite3
- python-dotenv
- schedule

## Instalacja lokalna

1. Klonuj repozytorium
```bash
git clone https://github.com/michalspoko18/GradeNotifier.git
cd GradeNotifier
```

2. Zainstaluj wymagane pakiety
```bash
pip install -r requirements.txt
```

3. Utwórz plik `.env` z odpowiednimi zmiennymi
```
# Konfiguracja dostępu do eDziekanatu
LOGIN_URL=https://edziekanat.zut.edu.pl/WU/
GRADE_URL=https://edziekanat.zut.edu.pl/WU/OcenyP.aspx
ZUT_INDEX=twoj_indeks
ZUT_PASSWORD=twoje_haslo

# Konfiguracja Discord
DISCORD_TOKEN=twoj_token_discord_bota
DISCORD_USER_ID=twoje_id_uzytkownika_discord

# Konfiguracja aplikacji
CRON_SCHEDULE=15
```

> **Uwaga dotycząca DISCORD_TOKEN**:
> Potrzebujesz utworzyć bota Discord na stronie [Discord Developer Portal](https://discord.com/developers/applications), aby uzyskać token. Bot potrzebuje uprawnienia do wysyłania wiadomości prywatnych.

> **Uwaga dotycząca DISCORD_USER_ID**:
> Aby uzyskać swoje ID użytkownika Discord, włącz "Tryb dewelopera" w ustawieniach Discord, następnie kliknij prawym przyciskiem myszy na swoją nazwę użytkownika i wybierz "Kopiuj ID".

## Uruchomienie lokalne

```bash
# Uruchom program w trybie ciągłego sprawdzania co 15 minut
python main.py

# Lub jednorazowe sprawdzenie ocen
python main.py --once
```

## Wdrożenie na serwerze

### Opcja 1: Docker (zalecana)

1. Przygotuj plik `.env` na podstawie `env.example`

2. Uruchom za pomocą Docker Compose:
```bash
docker-compose up -d
```

3. Sprawdź logi:
```bash
docker logs gradenotifier
# lub
tail -f logs/gradenotifier.log
```

### Opcja 2: Systemd (Linux)

1. Stwórz plik usługi systemd:
```bash
sudo nano /etc/systemd/system/gradenotifier.service
```

2. Dodaj następującą zawartość (dostosuj ścieżki):
```
[Unit]
Description=GradeNotifier Service
After=network.target

[Service]
User=twojuser
WorkingDirectory=/ścieżka/do/GradeNotifier
ExecStart=/usr/bin/python3 /ścieżka/do/GradeNotifier/main.py
Restart=always
RestartSec=10
StandardOutput=syslog
StandardError=syslog
SyslogIdentifier=gradenotifier

[Install]
WantedBy=multi-user.target
```

3. Włącz i uruchom usługę:
```bash
sudo systemctl enable gradenotifier.service
sudo systemctl start gradenotifier.service
```

4. Sprawdź status:
```bash
sudo systemctl status gradenotifier.service
```

### Opcja 3: Screen/Tmux na serwerze

Jeśli nie masz uprawnień administratora:

```bash
# Instalacja
ssh twoj_serwer
cd /ścieżka/do/GradeNotifier
pip install -r requirements.txt --user

# Uruchomienie (Screen)
screen -S gradenotifier
python main.py
# Naciśnij Ctrl+A, a następnie D aby odłączyć

# Aby wrócić do sesji
screen -r gradenotifier
```

## Struktura plików

- `main.py` - główny skrypt aplikacji
- `grades.db` - baza danych SQLite z ocenami
- `.env` - plik konfiguracyjny (nie umieszczony w repozytorium)
- `src/` - katalog z modułami aplikacji:
  - `config/` - konfiguracja aplikacji
  - `database/` - zarządzanie bazą danych
  - `notifications/` - moduły do wysyłania powiadomień
  - `scraper/` - moduły do pobierania danych z dziekanatu
  - `utils/` - narzędzia pomocnicze

## Baza danych

Aplikacja używa SQLite do przechowywania danych. Struktura bazy:

### Tabela `subjects` (przedmioty)
- `id` - klucz główny
- `name` - nazwa przedmiotu (unikalna)

### Tabela `grades` (oceny)
- `id` - klucz główny
- `subject_id` - klucz obcy do tabeli subjects
- `grade` - ocena
- `date` - data wystawienia oceny
- `added_date` - data dodania oceny do systemu