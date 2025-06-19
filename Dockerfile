FROM python:3.9-slim

WORKDIR /app

# Kopiuj pliki konfiguracyjne
COPY requirements.txt .
COPY .env.example .env

# Instaluj zależności
RUN pip install --no-cache-dir -r requirements.txt

# Kopiuj kod aplikacji
COPY main.py .
COPY src/ ./src/

# Utwórz katalog dla bazy danych i logów
RUN mkdir -p /app/data /app/logs

# Ustaw zmienne środowiskowe dla danych aplikacji
ENV DB_PATH=/app/data/grades.db
ENV LOG_PATH=/app/logs/gradenotifier.log

# Uruchom aplikację
CMD ["python", "main.py"]
