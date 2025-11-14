# components/utils/misc.py
import discord
import datetime
import asyncio
from discord.ext import commands

from config import config

def is_dev():
    async def predicate(ctx: commands.Context) -> bool:
        return ctx.author.id in config.devs
    return commands.check(predicate)