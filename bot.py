import discord
from discord.ext import commands
import logging
from logging.handlers import RotatingFileHandler
import traceback
import settings
import sys
from cogs.discord_utils.Context import Context
from cogs.discord_utils.Embeds import makeEmbeds

log = logging.getLogger('clodbot')
log.setLevel(logging.DEBUG)


class ClodBot(commands.Bot):
    def __init__(self, initialExt):
        intents = discord.Intents(
            guilds=True,
            members=True,
            bans=True,
            emojis=True,
            voice_states=True,
            messages=True,
            reactions=True,
            message_content=True)

        super().__init__(
            command_prefix="--",
            description="Sulfate and Paraben free.",
            intents=intents,
        )
        self.error_channel = self.get_channel(settings.ERROR_CHANNEL)
        self.dev_guild = settings.DEV_GUILD
        self.initialExt = initialExt

    async def setup_hook(self) -> None:
        for extension in self.initialExt:
            await self.load_extension(extension)
        # guild = discord.Object(self.dev_guild)
        # self.tree.copy_global_to(guild=guild)
        # await self.tree.sync(guild=guild)
        log.info("Setup Hook Complete!")

    async def close(self):
        log.info("Closing connection to Discord.")
        await super().close()

    async def get_context(self, message, *, cls=Context) -> Context:
        return await super().get_context(message, cls=cls)

    async def on_command_error(self, ctx: Context, error: commands.CommandError) -> None:
        log.error(str(error))
        if isinstance(error, commands.NoPrivateMessage):
            await ctx.send('This command cannot be used in private messages.')
        elif isinstance(error, commands.DisabledCommand):
            await ctx.send('This command is disabled and cannot be used.')
        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f"Dude, chill. {str(error)}")
        elif isinstance(error, commands.NotOwner):
            await ctx.send("This command can only be used by my owner.")
        elif isinstance(error, commands.CommandInvokeError):
            original = error.original
            if not isinstance(original, discord.HTTPException):
                print(f'In {ctx.command.qualified_name}:', file=sys.stderr)
                traceback.print_tb(original.__traceback__)
                print(f'{original.__class__.__name__}: {original}', file=sys.stderr)
                tb = traceback.format_tb(original.__traceback__)
                for message in makeEmbeds(tb):  # embeds that will fit the long traceback messages.
                    await self.error_channel.send(embed=message)
        elif isinstance(error, commands.ArgumentParsingError):
            await ctx.send(str(error))


def main():
    logger = logging.getLogger('discord')
    logger.setLevel(logging.INFO)
    logging.getLogger('discord.http').setLevel(logging.INFO)

    logFileHandler = RotatingFileHandler(
        filename='app.log',
        encoding='utf-8',
        maxBytes=7 * 1024 * 1024,  # 7 MiB so that I can send it in chat.
        backupCount=5,  # Rotate through 5 files
    )
    streamHandler = logging.StreamHandler()
    dt_fmt = '%Y-%m-%d %H:%M:%S'
    formatter = logging.Formatter('[{asctime}] [{levelname:<8}] {name}: {message}', dt_fmt, style='{')

    logFileHandler.setFormatter(formatter)
    streamHandler.setFormatter(formatter)

    logger.addHandler(logFileHandler)
    logger.addHandler(streamHandler)
    log.addHandler(logFileHandler)
    log.addHandler(streamHandler)

    ext = ['cogs.admin']
    bot = ClodBot(ext)
    log.info("Starting Bot")
    bot.run(token=settings.DISCORD_TOKEN, log_handler=None)


if __name__ == '__main__':
    main()
