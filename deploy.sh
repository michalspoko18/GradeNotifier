#!/bin/bash

# Skrypt do budowy i wdrażania GradeNotifier
# Autor: Michal Walczak
# Data: 2025-06-19

# Kolory do wyświetlania
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}=== GradeNotifier - Skrypt wdrożeniowy ===${NC}"
echo

# Sprawdź czy Docker jest zainstalowany
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Docker nie jest zainstalowany. Proszę zainstalować Docker i spróbować ponownie.${NC}"
    exit 1
fi

# Sprawdź czy docker-compose jest zainstalowany
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}Docker Compose nie jest zainstalowany. Proszę zainstalować Docker Compose i spróbować ponownie.${NC}"
    exit 1
fi

# Sprawdź czy plik .env istnieje
if [ ! -f .env ]; then
    echo -e "${YELLOW}Plik .env nie istnieje.${NC}"
    
    # Sprawdź czy plik env.example istnieje
    if [ -f env.example ]; then
        echo -e "${YELLOW}Kopiuję env.example do .env...${NC}"
        cp env.example .env
        echo -e "${GREEN}Utworzono plik .env na podstawie env.example.${NC}"
        echo -e "${YELLOW}Proszę edytować plik .env i uzupełnić dane logowania.${NC}"
    else
        echo -e "${RED}Plik env.example nie istnieje. Nie można utworzyć pliku .env automatycznie.${NC}"
        exit 1
    fi
fi

# Utwórz katalogi na dane i logi, jeśli nie istnieją
mkdir -p data logs
echo -e "${GREEN}Utworzono katalogi data/ i logs/ (jeśli nie istniały).${NC}"

# Buduj i uruchom kontenery
echo -e "${YELLOW}Budowanie i uruchamianie kontenerów Docker...${NC}"
docker-compose up --build -d

# Sprawdź czy uruchomienie się powiodło
if [ $? -eq 0 ]; then
    echo -e "${GREEN}Kontenery zostały uruchomione pomyślnie!${NC}"
    echo 
    echo -e "Użyj poniższych komend do zarządzania aplikacją:"
    echo -e "${YELLOW}docker-compose logs -f${NC} - aby śledzić logi"
    echo -e "${YELLOW}docker-compose stop${NC} - aby zatrzymać aplikację"
    echo -e "${YELLOW}docker-compose start${NC} - aby uruchomić zatrzymaną aplikację"
    echo -e "${YELLOW}docker-compose down${NC} - aby usunąć kontenery (dane pozostaną)"
else
    echo -e "${RED}Wystąpił błąd podczas uruchamiania kontenerów.${NC}"
    exit 1
fi

echo
echo -e "${GREEN}Aplikacja GradeNotifier działa w tle. Sprawdzaj logi, aby monitorować jej działanie.${NC}"
