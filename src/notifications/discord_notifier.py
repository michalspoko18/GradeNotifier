"""
Moduł odpowiedzialny za wysyłanie powiadomień poprzez Discord
"""
import asyncio
import logging
from typing import Dict, List
import discord

from src.config.settings import DISCORD_TOKEN, DISCORD_USER_ID

logger = logging.getLogger(__name__)

class DiscordNotifier:
    """Klasa odpowiedzialna za wysyłanie powiadomień poprzez Discord"""
    
    def __init__(self, token: str = DISCORD_TOKEN, user_id: str = DISCORD_USER_ID):
        self.token = token
        try:
            self.user_id = int(user_id) if user_id else None
        except ValueError:
            logger.error("Nieprawidłowy format DISCORD_USER_ID - musi być liczbą")
            self.user_id = None
        
        if not all([self.token, self.user_id]):
            logger.error("Brak wymaganych danych konfiguracyjnych Discord")
    
    async def _send_message(self, message: str) -> bool:
        """Wysyła wiadomość do użytkownika Discord"""
        if not all([self.token, self.user_id]):
            logger.error("Brak wymaganych danych konfiguracyjnych Discord")
            return False
            
        intents = discord.Intents.default()
        intents.messages = True
        client = discord.Client(intents=intents)
        success = False
        
        @client.event
        async def on_ready():
            nonlocal success
            try:
                # Pobierz obiekt użytkownika
                user = await client.fetch_user(self.user_id)
                
                if not user:
                    logger.error(f"Nie znaleziono użytkownika o ID {self.user_id}")
                    await client.close()
                    return
                
                # Wysyłamy prywatną wiadomość
                await user.send(message)
                logger.info(f"Wysłano powiadomienie do użytkownika {user.name}")
                success = True
                
            except discord.Forbidden:
                logger.error("Bot nie ma uprawnień do wysłania prywatnej wiadomości")
            except Exception as e:
                logger.error(f"Błąd przy wysyłaniu powiadomienia: {e}")
            finally:
                await client.close()
        
        # Uruchom klienta Discord
        try:
            await client.start(self.token)
        except Exception as e:
            logger.error(f"Nie udało się połączyć z Discord: {e}")
            
        return success
    
    def format_grade_message(self, grades: List[Dict[str, str]]) -> str:
        """Formatuje wiadomość o nowych ocenach"""
        if len(grades) == 1:
            grade = grades[0]
            message = (f"🎓 **Masz nową ocenę!** 🎓\n"
                      f"Przedmiot: {grade['subject']}\n"
                      f"Typ: {grade['subject_type']}\n"
                      f"Ocena: **{grade['grade']}**\n"
                      f"Data: {grade['date']}")
        else:
            message = f"🎓 **Masz {len(grades)} nowe oceny!** 🎓\n\n"
            for i, grade in enumerate(grades, 1):
                message += (f"**{i}. {grade['subject']} ({grade['subject_type']}):**\n"
                          f"   Ocena: **{grade['grade']}**\n"
                          f"   Data: {grade['date']}\n\n")
        return message
    
    def notify(self, grades: List[Dict[str, str]]) -> bool:
        """Wysyła powiadomienie o nowych ocenach"""
        if not grades:
            logger.info("Brak nowych ocen do powiadomienia")
            return True
            
        message = self.format_grade_message(grades)
        return asyncio.run(self._send_message(message))

def notify_new_grades(grades: List[Dict[str, str]]) -> bool:
    """Funkcja pomocnicza do wysyłania powiadomień o nowych ocenach"""
    notifier = DiscordNotifier()
    return notifier.notify(grades)
