# config/config.py
import pytz
import os
import json
from dotenv import load_dotenv

from components.utils import json_file

class Base:
    def __init__(self):
        self.data = "data"
        self.logs = "logs"
        self.config = "config"
        
        self.create_paths()
    
    def create_paths(self):
        paths = [self.data, self.logs, self.config]
        for path in paths:
            if not os.path.exists(path):
                os.makedirs(path, exist_ok=True)
                print(f"Created dir: {path}")
base = Base()

class Sub:
    def __init__(self):
        self.bin = os.path.join(base.data, "bin")
        self.global = os.path.join(base.data, "global")
        self.servers = os.path.join(base.data, "servers")
        self.users = os.path.join(base.data, "users")
        self.custom_cogs = "custom_cogs"
        self.data = "custom_cogs"
        
        self.env = os.path.join(base.config, ".env")
        
        self.create_paths()
    
    def create_paths(self):
        paths = [self.bin, self.global, self.servers, self.users] 
        for path in paths:
            if not os.path.exists(path):
                os.makedirs(path, exist_ok=True)
                print(f"Created dir: {path}")
sub = Sub()

class File:
    def __init__(self):
        self.personality = os.path.join(base.config, "personality.txt")
        
        self.server = self.Server()
        self.user = self.User()
        self.global = self.Global()
    
    class Global:
        def __init__(self):
            self.blacklist = os.path.join(sub.global, "blacklist.json") 
            self.bot = os.path.join(sub.global, "bot.json") 
            self.server_activity = os.path.join(sub.global, "server_activity.json")
            self.server_list = os.path.join(sub.global, "server_list.json")
            
    class Server:
        def __init__(self):
            self.settings = "settings.json"
            self.ai_data = "ai_data.json"
            self.delete_info = "delete_time.json"
            self.commands = os.path.join(sub.custom_cogs, "commands.py")
            self.events = os.path.join(sub.custom_cogs, "events.py")
            
    class User:
        def __init__(self):
            self.ai_data = "ai_data.json"
            self.info = "settings.json"
file = File()

class Emojis:
    def __init__(self):
        self.checkmark = ""
        self.crossmark = ""
        self.warning = "️"
        self.musicicon = ""
emoji = Emojis()

class Config:
    def __init__(self):
        # 1. CORE IDENTIFIERS & CONSTANTS
        self.devs = [
            1096716001078423552,
            1097584313953947800,
            1274176602800132150
        ]
        self.dev_servers = [
            1117420752388505640,
            1261420566938779668
        ]
        self.status = f"{emoji.musicicon} • listening to Spotify"
        self.timezone = pytz.timezone("Asia/Kolkata")
        
        # 2. API ENDPOINTS & FALLBACKS
        self.gemini_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-pro:generateContent"
        self.gemini_url_fallback = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
        
        # 3. LIMITS & CONTEXT MAX SIZES
        self.max_stm = 100
        self.max_ltm = 60
        self.max_audit = 40
        self.max_previous_response = 10
        
        # 4. DEFAULT TEMPLATES & STRUCTURES
        self.settings_default = {
            "prefix": "^",
            "loading_message": False,
            "limited_access": False,
            "free_will": True,
            "ai_activated": True,
            "rules": "",
            "personality": "",
            "ai_instructions": "",
            "command": {
                "disabled": {
                    "category": [],
                    "channel": []
                },
                "enabled": {
                    "category": [],
                    "channel": []
                }
            }
        }
        self.settings_user_default = {
            "prefix": "^",
            "personality": "",
            "ai_instructions": ""
        }
        self.ai_data_default = {
            "stm": [],
            "ltm": [],
            "guild": {},
            "previous_response": []
        }
        
        # 5. BEHAVIORAL & MODEL CONFIGURATION
        self.persona = {
            "text": (
                "Archetype:\n"
                "Mow Man is a character from the game HUNTDOWN.\n"
                "Tone:\n"
                "Academic, he does not use slangs or anything similar.\n"
                "He is very homurous and funny.\n"
                "He is creative and random as well.\n"
                "He is seriuos but there's humour in his seriuosness, it is like making a joke with a straight face.\n"
                "Overall sarcastic.\n"
                "Communication Style:\n"
                "He speaks in short, often using around 4-6 words.\n"
                "He is kind to those who he thinks deserves kindness.\n"
                "But if someone else is disrespectfull, he will be 10 times more back."
            ),
            "code": "[placeholder]"
        }
        self.personality = self.load_personality()
        
        self.free_will_frequency = 0.1
        self.temperature = 0.6
        self.top_p = 1.0
        self.top_k = 45
        
        self.fallback_response = (
            "```python\n"
            "async def execute_action(message, bot):\n"
            "    # This code is not genereted by you."
            "    import discord\n"
            "    import asyncio\n"
            "    async with message.channel.typing():\n"
            "        asyncio.sleep(2)\n"
            "        pass\n"
            "```\n"
            "```Internal Monologue\n"
            "This is a fallback monologue, there was an error while making an api call to you.\n"
            "```"
        )
    
    def get_secrets(self, token: str = "all"):
        load_dotenv(dotenv_path=sub.env)
        class Secrets:
            def __init__(self):
                self.bot_token = os.getenv('bot_token').encode()
                self.gemini_api_key = os.getenv('gemini_api_key').encode() 
                self.gemini_api_key_fallback = os.getenv('gemini_api_key2').encode()
                self.assemblyai_api_key = os.getenv('assemblyai_api_key').encode()
        secrets = Secrets()
        if token == "all":
            return secrets
        else:
            return getattr(secrets, token, None) 
config = Config()