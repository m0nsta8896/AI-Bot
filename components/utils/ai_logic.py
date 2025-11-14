# components/utils/ai_logic.py
import discord
import os
from typing import List, Dict, Union, Any
import datetime

_attachment_meta_cache: Dict[int, (datetime.datetime, List[Any])] = {}
CACHE_TTL = datetime.timedelta(minutes=30)

async def _fetch_attachments(guild: discord.Guild, limit: int) -> List[Dict[str, Union[str, bytes]]]:
    now = datetime.datetime.now(datetime.timezone.utc)
    all_attachments_info = None
    if guild.id in _attachment_meta_cache:
        cached_time, cached_data = _attachment_meta_cache[guild.id]
        if (now - cached_time) < CACHE_TTL:
            all_attachments_info = cached_data
    if all_attachments_info is None:
        all_attachments_info = []
        for channel in guild.text_channels:
            try:
                async for message in channel.history(limit=20): 
                    if message.attachments:
                        for attachment in message.attachments:
                            all_attachments_info.append((message.created_at, message.id, attachment))
            except discord.Forbidden:
                print(f"Warning: No permission to read history in {channel.name}. Skipping.")
            except discord.HTTPException as e:
                print(f"Warning: HTTPException while scanning {channel.name}: {e}. Skipping.")
        _attachment_meta_cache[guild.id] = (now, all_attachments_info)
    all_attachments_info.sort(key=lambda x: x[0], reverse=True)
    recent_attachments_to_fetch = all_attachments_info[:limit]
    output_files = []
    for created_at, msg_id, attachment in recent_attachments_to_fetch:
        try:
            _original_filename, extension = os.path.splitext(attachment.filename)
            new_filename = f"msg_id-{msg_id}{extension}"
            file_bytes = await attachment.read()
            output_files.append({
                'filename': new_filename,
                'data': file_bytes
            })
        except (discord.HTTPException, discord.NotFound) as e:
            print(f"Error: Failed to download {attachment.filename} (msg {msg_id}): {e}")
    return output_files