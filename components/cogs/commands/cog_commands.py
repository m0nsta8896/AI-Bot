# components/cogs/commands/cog_commands.py
import discord
from discord.ext import commands
from discord import app_commands, Embed, Color
from pathlib import Path

from components.ui import CogManagerView
from components.utils import is_dev
from config import emoji

async def cog_autocomplete(interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
    cogs_path = Path("components/cogs")
    choices = []
    for cog_file in cogs_path.rglob("*.py"):
        if cog_file.stem == "__init__":
            continue
        scope = cog_file.parent.name
        name = cog_file.stem
        extension_path = f"components.cogs.{scope}.{name}"
        label = f"[{scope}] {name}" 
        if current.lower() in label.lower() or current.lower() in extension_path.lower():
            choices.append(app_commands.Choice(name=label, value=extension_path))
    loaded_extensions = interaction.client.extensions.keys()
    for ext in loaded_extensions:
        if current.lower() in ext.lower() and ext not in [c.value for c in choices]:
             choices.append(app_commands.Choice(name=f"[Loaded] {ext}", value=ext))
    return choices[:25]

class CogCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    
    @commands.hybrid_group(
        name='cog', aliases=['c'],
        description='DEV ONLY: Handle cog files.'
    )
    @is_dev()
    async def cog(self, ctx):
        if ctx.invoked_subcommand is None:
            pass
    
    @cog.error
    async def cog_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            await ctx.reply(f"{emoji.crossmark} Only developers can use this command.")
    
    
    @cog.command(
        name='load',
        description='DEV ONLY: Load a cog file.'
    )
    @app_commands.describe(
        extension='The cog to load (e.g., components.cogs.commands.help_commands)'
    )
    @app_commands.autocomplete(extension=cog_autocomplete)
    async def load(self, ctx: commands.Context, *, extension: str):
        try:
            await self.bot.load_extension(extension)
            embed = Embed(
                title="Cog Loaded",
                description=f"{emoji.checkmark} Successfully loaded `{extension}`.",
                color=Color.green()
            )
            await ctx.reply(embed=embed)
        except commands.ExtensionError as e:
            embed = Embed(
                title="Load Error",
                description=f"{emoji.crossmark} Failed to load `{extension}`:\n```py\n{e}\n```",
                color=Color.red()
            )
            await ctx.reply(embed=embed)
    
    
    @cog.command(
        name='unload',
        description='DEV ONLY: Unload a cog file.'
    )
    @app_commands.describe(
        extension='The cog to unload (e.g., components.cogs.commands.help_commands)'
    )
    @app_commands.autocomplete(extension=cog_autocomplete)
    async def unload(self, ctx: commands.Context, *, extension: str):
        if "cog_manager" in extension:
            await ctx.reply(f"{emoji.crossmark} This cog cannot be unloaded.")
            return
            
        try:
            await self.bot.unload_extension(extension)
            embed = Embed(
                title="Cog Unloaded",
                description=f"{emoji.checkmark} Successfully unloaded `{extension}`.",
                color=Color.green()
            )
            await ctx.reply(embed=embed)
        except commands.ExtensionError as e:
            embed = Embed(
                title="Unload Error",
                description=f"{emoji.crossmark} Failed to unload `{extension}`:\n```py\n{e}\n```",
                color=Color.red()
            )
            await ctx.reply(embed=embed)
    
    
    @cog.command(
        name='reload',
        description='DEV ONLY: Reload a cog file.'
    )
    @app_commands.describe(
        extension='The cog to reload (e.g., components.cogs.commands.help_commands)'
    )
    @app_commands.autocomplete(extension=cog_autocomplete)
    async def reload(self, ctx: commands.Context, *, extension: str):
        try:
            await self.bot.reload_extension(extension)
            embed = Embed(
                title="Cog Reloaded",
                description=f"{emoji.checkmark} Successfully reloaded `{extension}`.",
                color=Color.green()
            )
            await ctx.reply(embed=embed)
        except commands.ExtensionError as e:
            embed = Embed(
                title="Reload Error",
                description=f"{emoji.crossmark} Failed to reload `{extension}`:\n```py\n{e}\n```",
                color=Color.red()
            )
            await ctx.reply(embed=embed)
    
    
    @cog.command(
        name='list',
        description='DEV ONLY: Open the interactive cog management panel.'
    )
    async def list(self, ctx: commands.Context):
        await ctx.send(
            "**Cog Management Panel**\nSelect a cog from the dropdown and choose an action.",
            view=CogManagerView(self.bot),
            ephemeral=True
        )

async def setup(bot: commands.Bot):
    await bot.add_cog(CogCommands(bot))