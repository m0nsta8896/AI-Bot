# components/cogs/general_events.py
import os
import datetime
import discord
import shutil
from discord.ext import commands, events, tasks
from datetime import timedelta

from config import sub, file, config
from components.utils import blacklist, json_file, server

class GeneralEvents(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    def cog_unload(self):
        self.cleanup_old_data.cancel()
        self.check_temporary_blacklists.cancel()

    # --- Background Tasks ---

    @tasks.loop(hours=24)
    async def cleanup_old_data(self):
        print(f"Running daily cleanup task for old server data...")
        if os.path.exists(sub.servers):
            guild_ids = {str(guild.id) for guild in self.bot.guilds}
            server_folders = os.listdir(sub.servers)
            
            for guild_id in server_folders:
                if guild_id not in guild_ids:
                    print(f"Detected leftover data for guild {guild_id}. Moving to bin.")
                    server.data.delete(guild_id)
        
        current_time = datetime.datetime.now(config.timezone)
        if os.path.exists(sub.bin):
            for guild_id_folder in os.listdir(sub.bin):
                folder_path = os.path.join(sub.bin, guild_id_folder)
                timestamp_file = os.path.join(folder_path, file.server.delete_info)
                
                if os.path.exists(timestamp_file):
                    try:
                        info = json_file.load(timestamp_file)
                        moved_at_str = info.get("moved_at")
                        if moved_at_str:
                            moved_at_time = datetime.datetime.fromisoformat(moved_at_str)
                            if current_time - moved_at_time > timedelta(days=7):
                                shutil.rmtree(folder_path)
                                print(f"Permanently deleted data for guild {guild_id_folder} from bin.")
                    except Exception as e:
                        print(f"Error processing bin folder {guild_id_folder}: {e}")
                else:
                    shutil.rmtree(folder_path)

    @cleanup_old_data.before_loop
    async def before_cleanup(self):
        await self.bot.wait_until_ready()

    @tasks.loop(minutes=5)
    async def check_temporary_blacklists(self):
        now = datetime.datetime.now(config.timezone)
        
        user_blacklist = self.bot.user_blacklist_cache.copy()
        user_updated = False
        for user_id, data in user_blacklist.items():
            expires_at_str = data.get("expires_at")
            if expires_at_str:
                expires_at = datetime.datetime.fromisoformat(expires_at_str)
                if now >= expires_at:
                    del self.bot.user_blacklist_cache[user_id]
                    user_updated = True
                    print(f"CHECK_TEMPORARY_BLACKLISTS: Removed expired blacklist for user ID {user_id}")
        if user_updated:
            blacklist.save("user", self.bot.user_blacklist_cache)
        
        server_blacklist = self.bot.server_blacklist_cache.copy()
        server_updated = False
        for server_id, data in server_blacklist.items():
            expires_at_str = data.get("expires_at")
            if expires_at_str:
                expires_at = datetime.datetime.fromisoformat(expires_at_str)
                if now >= expires_at:
                    del self.bot.server_blacklist_cache[server_id]
                    server_updated = True
                    print(f"CHECK_TEMPORARY_BLACKLISTS: Removed expired blacklist for server ID {server_id}")
        if server_updated:
            blacklist.save("server", self.bot.server_blacklist_cache)

    # --- Core Event Listeners ---

    @commands.Cog.listener()
    async def on_ready(self):
        print("Bot is ready. Loading...")
        await self.bot.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.listening,
                name=config.status
            ),
            status=discord.Status.dnd
        )
        await server.list.save(self.bot.guilds, self.bot)
        for guild in self.bot.guilds:
            await server.info.save(guild)
        self.cleanup_old_data.start()
        self.check_temporary_blacklists.start()

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        server.list.save(self.bot.guilds, self.bot)
        
        data_restored = server.data.restore(guild.id)
        await server.info.save(guild)
        
        if data_restored:
            message = (
                f"Here we go again. Your lucky i didn't delete your server data\n"
                f"-# [Terms of Service]( <https://mowman.pages.dev/terms ) • [Privacy Policy]( <https://mowman.pages.dev/privacy )"
            )
        else:
            message = (
                f"ding dong.\nuse `^help ai`, or your server's organic matter might achieve peak frustration with me.\n"
                f"-# [Terms of Service]( <https://mowman.pages.dev/terms ) • [Privacy Policy]( <https://mowman.pages.dev/privacy )"
            )
        
        if guild.system_channel and isinstance(guild.system_channel, discord.TextChannel) and guild.system_channel.permissions_for(guild.me).send_messages:
            try:
                await guild.system_channel.send(message)
                return
            except discord.Forbidden:
                pass
        for channel in sorted(guild.text_channels, key=lambda c: c.position):
            if channel.permissions_for(guild.me).send_messages:
                if channel.is_default_channel() or channel.type == discord.ChannelType.news or channel.id == channel.guild.rules_channel.id:
                    continue
                try:
                    await channel.send(message)
                    return
                except discord.Forbidden:
                    continue

    @commands.Cog.listener()
    async def on_guild_remove(self, guild: discord.Guild):
        server.list.save(self.bot.guilds, self.bot)
        server.data.delete(str(guild.id))

async def setup(bot: commands.Bot):
    await bot.add_cog(GeneralEvents(bot))