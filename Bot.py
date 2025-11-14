# Bot.py
import os
import sys
import asyncio
import discord
import traceback
import getpass
from discord.ext import commands
from cryptography.fernet import Fernet

from config import config, base, file
from components import Logging, VigenereCipher
from components.utils import blacklist, server, json_file

class Bot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True
        intents.presences = True
        intents.message_content = True
        
        super().__init__(
            command_prefix = self.get_prefix,
            intents=intents
        )
        self.command_mentions = {}
        self.blacklist_cache = json_file.load(file.blacklist)
    
    async def setup_hook(self):
        for filename in os.listdir('./components/cogs/events'):
            if filename.endswith('.py') and not filename.startswith('__init__'):
                try:
                    await self.load_extension(f'components.cogs.events.{filename[:-3]}')
                    print(f"Loaded Cog: {filename}")
                except Exception as e:
                    print(f"Failed to load cog: /events/{filename} | {type(e).__name__} - {e}")
        for filename in os.listdir('./components/cogs/commands'):
            if filename.endswith('.py') and not filename.startswith('__init__'):
                try:
                    await self.load_extension(f'components.cogs.commands.{filename[:-3]}')
                    print(f"Loaded Cog: {filename}")
                except Exception as e:
                    print(f"Failed to load cog: /commands/{filename} | {type(e).__name__} - {e}")
        
        synced = await self.tree.sync()
        print(f"Commands Synced: {len(synced)}")
        
        for cmd in synced:
            self.command_mentions[cmd.name] = f"<{cmd.name}:{cmd.id}>"
            if isinstance(cmd, discord.app_commands.Group):
                for sub_cmd in cmd.commands:
                    qualified_name = f"{cmd.name} {sub_cmd.name}"
                    self.command_mentions[qualified_name] = f"</{qualified_name}:{cmd.id}>"
        print("Commmand mentions populated")
    
    async def get_prefix(self, bot, message):
        prefixes = ["^", "m!"]
        if message.guild:
            settings = server.settings.load(message.guild.id)
            prefix = settings.get("prefix")
            if prefix and prefix not in prefixes:
                prefixes.append(prefix)
        return prefixes

if __name__ == "__main__":
    logging = Logging(
        timezone=config.timezone,
        logs_dir=base.logs,
        log_format = "%B_%d-%Y.log",
        cleanup_on_startup = True
    )
    logging.setup()
    bot = Bot()
    
    
    try:
        key = os.environ.get('BOT_KEY')
        if not key:
            key = getpass.getpass("Enter Key: ")
        cipher = Fernet(key.encode())
        
        bot.run(
            cipher.decrypt(
                config.get_secrets('bot_token')
            ).decode()
        )
    except (KeyboardInterrupt, SystemExit):
        print("Shutting Down...")
    except Exception:
        traceback.print_exc()
    finally:
        logging.shutdown()

__version__ = '1.0.0'