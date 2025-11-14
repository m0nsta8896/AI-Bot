# components/utils/server_manager.py
import os
import shutil
import datetime
import discord
import asyncio

from config import sub, file
from .file_manager import json_file
from .converter import convert3


class Server:
    def __init__(self):
        self.data = Data()
        self.settings = Settings()
        self.info = Info()
        self.list = List()
server = Server()

class Data:
    def delete(self, guild_id):
        guild_id = str(guild_id)
        source_path = os.path.join(sub.servers, guild_id)
        dest_path = os.path.join(sub.bin, guild_id)
        if os.path.exists(source_path):
            try:
                if os.path.exists(dest_path):
                    shutil.rmtree(dest_path)
                shutil.move(source_path, dest_path)
                deletion_info = {
                    "moved_at": datetime.datetime.now(TIMEZONE).isoformat(),
                    "guild_id": guild_id
                }
                timestamp_file = os.path.join(dest_path, file.server.delete_info)
                json_file.save(timestamp_file, deletion_info)
            except Exception as e:
                print(f"SERVER.DATA.DELETE: Error moving server data for guild '{guild_id}' to bin: {e}")
    
    def restore(self, guild_id):
        guild_id = str(guild_id)
        binned_path = os.path.join(sub.bin, guild_id)
        final_active_path = os.path.join(sub.servers, guild_id)
        restore_destination = sub.servers
        if os.path.exists(binned_path):
            try:
                if os.path.exists(final_active_path):
                    shutil.rmtree(final_active_path)
                shutil.move(binned_path, restore_destination)
                timestamp_file = os.path.join(final_active_path, "deletion_info.json") 
                if os.path.exists(timestamp_file):
                    os.remove(timestamp_file)
                return True
            except Exception as e:
                print(f"SERVER.DATA.RESTORE: An error occurred while restoring data of '{guild_id}': {e}")
                return False
        return False

class Settings:
    def load(self, guild_id):
        guild_file = os.path.join(sub.servers, str(guild_id), file.server.settings)
        data = {}
        if os.path.exists(guild_file):
            data = json_file.load(guild_file)
        else:
            print(f"SERVER.SETTINGS.LOAD: Guild '{guild_id}' not found. Returning empty dictionary.")
            data = {}
        return data
    
    def save(self, guild_id, data):
        guild_file = os.path.join(sub.servers, str(guild_id), file.server.settings)
        if os.path.exists(guild_file):
            json_file.save(guild_file, data)
        else:
            print(f"SERVER.SETTINGS.SAVE: Guild '{guild_id}' not found. Skipping operation.")

class Info:
    def load(self, guild_id):
        guild_file = os.path.join(sub.servers, str(guild_id), file.server.info)
        data = {}
        if os.path.exists(guild_file):
            data = json_file.load(guild_file)
        else:
            print(f"SERVER.INFO.LOAD: Guild '{guild_id}' not found. Returning empty dictionary.")
        return data
    
    async def save(self, guild: discord.Guild):
        try:
        except Exception as e:
            print(f"SERVER.INFO.SAVE: An error occured while saving guild_info for '{guild.id}': {e}")

class List:
    async def save(self, servers, bot):
        data = await convert3.to_json(servers)
        json_file.save(file.server.list, data)