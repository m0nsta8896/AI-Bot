from .server_manager import server

class Commnd:
    def is_enabled(ctx):
        settings = server.settings.load(ctx.guild.id)
        if settings:
            enabled_channels = settings['command']['enabled']['channel']
            enabled_categories = settings['command']['enabled']['category']
            
            is_enabled = False
            if ctx.channel.id in enabled_channels:
                is_enabled = True
            if ctx.channel.category.id in enabled_categories:
                is_enabled = True
            
            return is_enabled
        return False