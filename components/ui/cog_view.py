import discord
from discord.ui import View, Select, Button, button
from discord.ext import commands
from discord import Interaction, SelectOption, ButtonStyle
from pathlib import Path

class CogSelect(Select):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        super().__init__(placeholder="Select a cog to manage...", min_values=1, max_values=1)
        self.populate_options()
    
    def get_all_cogs(self):
        cogs_path = Path("components/cogs")
        all_cogs = []
        for cog_file in cogs_path.rglob("*.py"):
            if cog_file.stem == "__init__":
                continue
            scope = cog_file.parent.name
            name = cog_file.stem
            extension_path = f"components.cogs.{scope}.{name}"
            all_cogs.append(extension_path)
        return all_cogs
    
    def populate_options(self):
        all_cogs = get_all_cogs()
        loaded_cogs = self.bot.extensions.keys()
        options = []
        for cog_path in sorted(all_cogs):
            try:
                scope, name = cog_path.split('.')[-2:]
                label = f"[{scope}] {name}"
            except ValueError:
                label = cog_path
            if cog_path in loaded_cogs:
                options.append(
                    SelectOption(label=label, value=cog_path, emoji="✅", description="Currently loaded.")
                )
            else:
                options.append(
                    SelectOption(label=label, value=cog_path, emoji="❌", description="Currently unloaded.")
                )
        self.options = options

    async def callback(self, interaction: Interaction):
        await interaction.response.defer()

class CogManagerView(View):
    def __init__(self, bot: commands.Bot):
        super().__init__(timeout=None)
        self.bot = bot
        self.select_menu = CogSelect(bot)
        self.add_item(self.select_menu)
    
    async def handle_cog_action(self, interaction: Interaction, action: str):
        if not self.select_menu.values:
            await interaction.response.send_message("Please select a cog from the dropdown first.", ephemeral=True)
            return
        extension_name = self.select_menu.values[0]
        if action == "unload" and "cog_manager" in extension_name:
            await interaction.response.send_message("❌ **Error:** This cog manager cannot be unloaded.", ephemeral=True)
            return
        try:
            if action == "load":
                await self.bot.load_extension(extension_name)
                message = f"✅ **Success:** Loaded `{extension_name}`."
            elif action == "unload":
                await self.bot.unload_extension(extension_name)
                message = f"✅ **Success:** Unloaded `{extension_name}`."
            elif action == "reload":
                await self.bot.reload_extension(extension_name)
                message = f"✅ **Success:** Reloaded `{extension_name}`."
            else:
                return
            self.select_menu.populate_options()
            await interaction.message.edit(view=self)
            await interaction.response.send_message(message, ephemeral=True)
        except commands.ExtensionAlreadyLoaded:
            await interaction.response.send_message(f"❌ **Error:** Cog `{extension_name}` is already loaded.", ephemeral=True)
        except commands.ExtensionNotLoaded:
            await interaction.response.send_message(f"❌ **Error:** Cog `{extension_name}` is not loaded.", ephemeral=True)
        except commands.ExtensionNotFound:
            await interaction.response.send_message(f"❌ **Error:** Cog `{extension_name}` could not be found.", ephemeral=True)
        except commands.ExtensionFailed as e:
            await interaction.response.send_message(f"❌ **Error:** Cog `{extension_name}` failed to load:\n```py\n{e.original}\n```", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ **An unknown error occurred:**\n```py\n{e}\n```", ephemeral=True)
    
    @button(label="Load", style=ButtonStyle.green, row=1)
    async def load_button(self, interaction: Interaction, button: Button):
        await self.handle_cog_action(interaction, "load")
    
    @button(label="Unload", style=ButtonStyle.red, row=1)
    async def unload_button(self, interaction: Interaction, button: Button):
        await self.handle_cog_action(interaction, "unload")
    
    @button(label="Reload", style=ButtonStyle.primary, row=1)
    async def reload_button(self, interaction: Interaction, button: Button):
        await self.handle_cog_action(interaction, "reload")