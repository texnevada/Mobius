import discord
import asyncio
import configparser
from discord.ext import commands
from discord.ext.commands import has_permissions
from data.functions.MySQL_Connector import MyDB
from data.functions.logging import get_log

config = configparser.ConfigParser()
config.read("./config.ini")
logger = get_log(__name__)


# TODO: Replace @MODUS with config
# TODO: Replace Support link with config

pre = config["APP"]


class admin_commands(commands.Cog):
    def __init__(self, client: commands.Bot) -> None:
        self.client = client
        super().__init__()

    # Reads the users input if it has prefix or not
    @commands.command(name="clear", aliases=["purge"])
    # Will only execute command if user has the role
    @commands.guild_only()
    @has_permissions(manage_messages=True)
    # sees user wants to use the command clear.
    async def clear(self, ctx, amount: int):
        try:
            if amount <= 10000:
                logger.info(f"A admin has started a purge of messages in \"{ctx.guild.name}\" clearing {amount} of messages")
                async with ctx.channel.typing():
                    if amount >= 1000:
                        await ctx.send("This might take a while to clear & start. Please be patient.")
                        await asyncio.sleep(5)
                    await ctx.channel.purge(limit=amount+1)
                    bot_message = await ctx.channel.send("Messages cleared!")
                    await asyncio.sleep(2)
                    await bot_message.delete()
                logger.info(f"Purged messages in \"{ctx.guild.name}\" ")
            else:
                await ctx.send("You can only delete 100k messages at once.")
        except Exception as e:
            logger.info(f"{ctx.guild.id} - {e}")
            await ctx.send('I require the permission `manage messages` to delete messages for you.')

    @commands.command(name="moveto", aliases=["silentmoveto"])
    # Will only execute command if user has the role
    @commands.guild_only()
    @has_permissions(manage_messages=True)
    # sees user wants to use the command clear.
    async def moveto(self, ctx, To_Channel: discord.TextChannel, amount: int, *, reason=None):
        logger.info(f"Moveto command was issues in \"{ctx.guild.name}\"")
        msg_limit = 150
        missing_perms = "I require the permission `manage webhooks` & " \
                        "`manage messages` to be able to move messages for you"

        # In case of trying to move to the same channel
        if To_Channel == ctx.channel:
            await ctx.response.send_message("It seems you're trying to move the messages to the original channel")
            return False
        elif not To_Channel.permissions_for(ctx.author.guild.me).manage_webhooks:
            await ctx.send(f'I Require the permission "Manage Webhooks" on the {To_Channel} '
                           f'channel itself to be able to move messages for you.')
            return False

        if ctx.author.guild.me.guild_permissions.manage_webhooks:
            if ctx.author.guild.me.guild_permissions.manage_messages:
                if amount <= msg_limit:
                    async with ctx.channel.typing():
                        webhook = await To_Channel.create_webhook(name="Temporary Moveto Webhook",
                                                                  reason=f"For moving messages from {ctx.channel} to {To_Channel}")
                        try:
                            # Fetching messages
                            # +1 is specified as we also want to include our own message.
                            # We only want to delete the amount messages above our command message.
                            messages = [message async for message in ctx.channel.history(limit=amount+1)]
                            # We reverse the messages to post them back later in the destination channel.
                            messages.reverse()

                            # Fetching all users
                            users = []
                            for message in messages:
                                if message.id == ctx.message.id:
                                    list_position = messages.index(message)
                                    messages.pop(list_position)
                                else:
                                    if message.author.id not in users:
                                        users.append(message.author.id)

                            for message in messages:
                                message_content = message.content
                                if len(message.attachments) != 0:
                                    message_content += '\n'.join([attachment.url for attachment in message.attachments])
                                if message_content == "":
                                    if len(message.embeds) == 0:
                                        await webhook.send(username=f"{message.author.display_name}",
                                                           avatar_url=message.author.display_avatar.url)
                                    else:
                                        await webhook.send(username=f"{message.author.display_name}",
                                                           avatar_url=message.author.display_avatar.url,
                                                           embeds=message.embeds)
                                else:
                                    if len(message.embeds) == 0:
                                        await webhook.send(username=f"{message.author.display_name}",
                                                           content=message_content,
                                                           avatar_url=message.author.display_avatar.url)
                                    else:
                                        await webhook.send(username=f"{message.author.display_name}",
                                                           content=message_content,
                                                           avatar_url=message.author.display_avatar.url,
                                                           embeds=message.embeds)
                                # In case of an attachment wait 1 seconds to make sure it is loaded before deleting
                                # Because discord will delete the unused url so if we delete the original before giving
                                # the new msg a second to register it will sometimes not work and post a not working url
                                await asyncio.sleep(1)
                                await message.delete()

                            logger.info(f"moved messages in \"{ctx.guild.name}\"")
                            if ctx.invoked_with == "silentmoveto":
                                bot_message = await ctx.send("Done")
                                await asyncio.sleep(2)
                                try:
                                    await ctx.message.delete()
                                except Exception as e:
                                    print(e)
                                    logger.debug(f"Failed to delete moveto command. Reason: {e}")
                                try:
                                    await bot_message.delete()
                                except Exception as e:
                                    logger.debug(f"Failed to delete moveto bot message. Reason: {e}")
                            else:
                                if len(users) > 0:
                                    msg = ''
                                    for user_id in users:
                                        msg += f'<@{user_id}>, '
                                    await webhook.send(username='MODUS',
                                                       content=f'{msg} Your messages were moved to this channel for reason:'
                                                               f' \"{reason}\"',
                                                       avatar_url=config["APP"]["Bot_Logo"])
                                bot_message = await ctx.send("Done")
                                await asyncio.sleep(2)
                                try:
                                    await ctx.message.delete()
                                except Exception as e:
                                    print(e)
                                    logger.debug(f"Failed to delete moveto command. Reason: {e}")
                                try:
                                    await bot_message.delete()
                                except Exception as e:
                                    logger.debug(f"Failed to delete moveto bot message. Reason: {e}")
                            await webhook.delete(reason=f"Finished moving messages from {ctx.channel} to {To_Channel}")
                        except Exception as e:
                            logger.info(e)
                            await webhook.delete(reason=f"Error when trying to move messages from {ctx.channel} to {To_Channel}")

                else:
                    await ctx.send(f"You can only move a maximum {msg_limit} messages")
            else:
                await ctx.send(missing_perms)
        else:
            await ctx.send(missing_perms)


async def setup(client: commands.Bot):
    await client.add_cog(admin_commands(client))
