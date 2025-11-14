# components/utils/converter.py
import datetime
import json
import asyncio
from io import StringIO
import discord
try:
    DISCORD_MODELS = (
        discord.Member, discord.Role, discord.Emoji, discord.Guild,
        discord.TextChannel, discord.VoiceChannel, discord.CategoryChannel,
        discord.User, discord.Message, discord.Asset, discord.Client,
        discord.ClientUser
    )
    DISCORD_TYPES = (discord.Colour, discord.Permissions)
except ImportError:
    DISCORD_MODELS = ()
    DISCORD_TYPES = ()

class Convert:
    def __init__(self, filter_attrs: str = None, max_depth: int = 5):
        self.filter_attrs = filter_attrs
        self.max_depth = max_depth
    
    async def to_json(self, obj, filter_attrs=None, max_depth=None):
        class _Sentinel:
            def __repr__(self):
                return "<Circular Reference>"
        _CIRCULAR = _Sentinel()
        
        current_max_depth = max_depth if max_depth is not None else self.max_depth
        current_filter_attrs = filter_attrs if filter_attrs is not None else self.filter_attrs
        
        def _sync_serialize_object(obj, seen_stack, filter_attrs, depth, max_depth):
            if filter_attrs is None:
                filter_attrs = []
            
            # --- Base Type Checks ---
            if obj is None or isinstance(obj, (int, float, bool)):
                return obj
            if isinstance(obj, str):
                return obj
            if isinstance(obj, datetime.datetime):
                return obj.isoformat()
            if DISCORD_TYPES and isinstance(obj, DISCORD_TYPES):
                return str(obj)
            
            # --- Depth Check ---
            if depth >= max_depth:
                try:
                    return str(obj)
                except Exception:
                    return f"[Max depth {max_depth} reached]"
            
            # --- Circular Reference Check ---
            obj_id = id(obj)
            if obj_id in seen_stack:
                return _CIRCULAR
            seen_stack.add(obj_id) 
            
            # --- Collection Serialization ---
            if isinstance(obj, dict):
                new_dict = {}
                for k, v in obj.items():
                    serialized_value = _sync_serialize_object(
                        v, seen_stack, filter_attrs, depth + 1, max_depth
                    )
                    if serialized_value is not _CIRCULAR:
                        new_dict[str(k)] = serialized_value
                seen_stack.remove(obj_id)
                return new_dict
            is_discord_model = bool(DISCORD_MODELS and isinstance(obj, DISCORD_MODELS))
            if not is_discord_model:
                try:
                    iterable = list(obj)
                    new_list = []
                    for item in iterable:
                        serialized_item = _sync_serialize_object(
                            item, seen_stack, filter_attrs, depth + 1, max_depth
                        )
                        if serialized_item is not _CIRCULAR:
                            new_list.append(serialized_item)
                    seen_stack.remove(obj_id)
                    return new_list
                except TypeError:
                    pass
            
            # --- Object Serialization ---
            result = {}
            try:
                attributes = dir(obj)
            except Exception:
                attributes = []
            for attr_name in attributes:
                if attr_name.startswith('_'):
                    continue
                if attr_name in filter_attrs:
                    continue
                if depth > 1 and attr_name in ('members', 'roles', 'channels'): 
                    result[attr_name] = "<Skipped: Attribute present at surface level>" 
                    continue
                try:
                    value = getattr(obj, attr_name)
                except Exception as e:
                    result[attr_name] = f"[Error accessing attribute: {e}]"
                    continue
                if callable(value):
                    continue
                serialized_value = _sync_serialize_object(
                    value, seen_stack, filter_attrs, depth + 1, max_depth
                )
                if serialized_value is not _CIRCULAR:
                    result[attr_name] = serialized_value
            seen_stack.remove(obj_id)
            return result
        
        return await asyncio.to_thread(
            _sync_serialize_object, obj, set(), current_filter_attrs, 0, current_max_depth
        )

# object for messages
convert1 = Convert(
    filter_attrs = [
        'guild', 'channel', 'mutual_guilds',
        'call', 'jump_url', 'colour',
        'accent_colour', 'DEFAULT_VALUE', 'VALID_FLAGS',
        'BASE', 'key', 'role_subscription',
        'clean_content', 'value', 'raw_role_mentions',
        'failed_to_mention_some_roles_in_thread',
        'role_mentions', 'raw_mentions',
        'message_snapshots', 'nonce', 'system_content',
        'purchase_notification', 'tts', 'application',
        'application_id', 'accent_color',
        'avatar_decoration_sku_id', 'top_role',
        'client_status', 'default_avatar', 'category',
        'discriminator', 'dm_settings_upsell_acknowledged',
        'identity_enabled', 'roles', 'channel_mentions',
        'mention_everyone', 'pinned_at', 'pinned',
        'desktop_status', 'pending', 'web_status', 'channels'
    ],
    max_depth = 5
)

# object for servers
convert2 = Convert(
    filter_attrs = [
        'me', 'BASE', 'key', 'DEFAULT_VALUE',
        'VALID_FLAGS', 'jump_url', 'categories',
        'voice_channels', 'text_channels'
    ],
    max_depth = 5
)

# object for lists of servers
convert3 = Convert(
    filter_attrs = [
        'me', 'BASE', 'key', 'DEFAULT_VALUE',
        'VALID_FLAGS', 'jump_url', 'categories',
        'voice_channels', 'text_channels'
    ],
    max_depth = 3
)

# object for users
convert4 = Convert(
    filter_attrs = [
        'BASE', 'key', 'DEFAULT_VALUE', 'VALID_FLAGS',
        'guild', 'mutual_guilds', 'status', 'web_status',
        'mobile_status', 'desktop_status', 'client_status',
        'colour'
    ],
    max_depth = 5
)

# object for bot
convert5 = Convert(
    filter_attrs = [
        'cached_messages', 'cogs', 'extra_events',
        'users', 'user', 'token', 'soundboard_sounds',
        'help_command', 'command_mentions', 'commands',
        'stickers'
    ],
    max_depth = 3
)