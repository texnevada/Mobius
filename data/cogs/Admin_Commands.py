"""
Extension name: admin commands
Author: Tex Nevada
Created: 18.03.19 - Europe
"""
# import discord py library
import discord
# Imports commands
from discord.ext import commands
# import permissions
from discord.ext.commands import has_permissions
import asyncio
from data.functions.MySQL_Connector import MyDB
import configparser
config = configparser.ConfigParser()
config.read("./config.ini")

# TODO: Replace @MODUS with config
# TODO: Replace Support link with config


class Admin_Commands(commands.Cog):
    def __init__(self, client):
        self.client = client

    # Reads the users input if it has prefix or not
    @commands.command(name="clear", aliases=["purge"])
    # Will only execute command if user has the role
    @commands.guild_only()
    @has_permissions(manage_messages=True)
    # sees user wants to use the command clear.
    async def clear(self, ctx, amount: int):
        try:
            if amount <= 10000:
                print(f"A admin has started a purge of messages in \"{ctx.guild.name}\" clearing {amount} of messages")
                async with ctx.channel.typing():
                    if amount >= 1000:
                        await ctx.send("This might take a while to clear & start. Please be patient.")
                        await asyncio.sleep(5)
                    await ctx.channel.purge(limit=amount+1)
                    bot_message = await ctx.channel.send("Messages cleared!")
                    await asyncio.sleep(2)
                    await bot_message.delete()
                print(f"Purged messages in \"{ctx.guild.name}\" ")
            else:
                await ctx.send("You can only delete 100k messages at once.")
        except Exception as e:
            print(e)
            await ctx.send('I require the permission `manage messages` to delete messages for you.')

    @commands.command(name="moveto", aliases=["mimic", "echo", "silentmoveto", "перемести", "перемесТихо"])
    # Will only execute command if user has the role
    @commands.guild_only()
    @has_permissions(manage_messages=True)
    # sees user wants to use the command clear.
    async def moveto(self, ctx, toChannel: discord.TextChannel, amount: int, *, reason=None):
        missing_perms = "I require the permission `manage webhooks` & " \
                        "`manage messages` to be able to move messages for you"

        # In case of trying to move to the same channel
        if toChannel == ctx.channel:
            await ctx.send("It seems you're trying to move the messages to the original channel")
            return False
        elif not toChannel.permissions_for(ctx.author.guild.me).manage_webhooks:
            await ctx.send(f'I Require the permission "Manage Webhooks" on the {toChannel} '
                           f'channel itself to be able to move messages for you.')
            return False

        if ctx.author.guild.me.guild_permissions.manage_webhooks:
            if ctx.author.guild.me.guild_permissions.manage_messages:
                if amount <= 30:
                    async with ctx.channel.typing():
                        users = []
                        messages = []
                        image_formats = ["jpg", "png", "gif", "jpeg"]
                        webhook = await toChannel.create_webhook(name="Temporary Moveto Webhook")
                        async for message in ctx.channel.history(limit=amount+1):
                            # Look for messages or attachments
                            if message.id != ctx.message.id and (message.content != '' or message.attachments[0].url):
                                messages.append(message)
                                if message.author.id not in users:
                                    users.append(message.author.id)

                        messages.reverse()
                        for message in messages:
                            # In the case of a normal message without attachments
                            if message.content != '' and not message.attachments:
                                await webhook.send(username=message.author.name,
                                                   content=message.content,
                                                   avatar_url=message.author.avatar_url)
                            # In case of attachments
                            elif message.attachments:
                                is_image = False
                                for image_format in image_formats:
                                    if message.attachments[0].url.endswith(image_format):
                                        is_image = True
                                # If attached file is not an image post only the content
                                if not is_image:
                                    if message.content == '':
                                        pass
                                    else:
                                        await webhook.send(username=message.author.name,
                                                           content=message.content,
                                                           avatar_url=message.author.avatar_url)
                                else:
                                    await webhook.send(username=message.author.name,
                                                       content=message.content + "\n" + message.attachments[0].url,
                                                       avatar_url=message.author.avatar_url)
                                # In case of an attachment wait 1 seconds to make sure it is loaded before deleting
                                # Because discord will delete the unused url so if we delete the original before giving
                                # the new msg a second to register it will sometimes not work and post a not working url
                                await asyncio.sleep(1)

                            await message.delete()

                        print(f"moved messages in \"{ctx.guild.name}\" ")
                        if ctx.invoked_with == "silentmoveto":
                            await webhook.delete()
                            bot_message = await ctx.send("Done")
                            await asyncio.sleep(2)
                            await bot_message.delete()
                        else:
                            if len(users) > 0:
                                msg =''
                                for each in users:
                                    msg += '<@{}>, '.format(each)
                                await webhook.send(username='MODUS',
                                                   content=f'{msg} Your messages were moved to this channel for reason: \"{reason}\"',
                                                   avatar_url="https://cdn.edb.tools/MODUS_Project/images/Enclave/MODUS_smiling.jpg")
                            await webhook.delete()
                else:
                    await ctx.send("You can only move a maximum 30 messages")
            else:
                await ctx.send(missing_perms)
        else:
            await ctx.send(missing_perms)

    @commands.command()
    @commands.guild_only()
    @has_permissions(administrator=True)
    async def prefix(self, ctx, arg=None):
        print(f"A admin changed the prefix of their server in {ctx.guild.name}")
        try:
            c = MyDB("essential")
            c.execute("SELECT * FROM GuildTable WHERE GuildID = %s", (ctx.guild.id,))
            response = c.fetchone()
            oldprefix = []
            isprefixold = False
            if response["Prefix"] and arg is not None:
                oldprefix.append(response["Prefix"])
                isprefixold = True

            if arg is None:
                c.execute("UPDATE GuildTable SET Prefix = %s WHERE GuildID = %s", (config["APP"]["Prefix"], ctx.guild.id,))
            else:
                c.execute("UPDATE GuildTable SET Prefix = %s WHERE GuildID = %s", (arg, ctx.guild.id,))
            c.commit()
            c.close()

            embed = discord.Embed(color=0xe7e9d3, title="The Enclave Database")
            embed.set_thumbnail(url="https://cdn.edb.tools/MODUS_Project/images/Enclave/Enclave.png")
            prefix = "Your server prefix has changed!"
            if arg is None:
                embed.add_field(name=prefix,
                                value="MODUS prefix has now been reverted back to default\n**Default:** >")

            elif isprefixold is True:
                embed.add_field(name=prefix,
                                value=f"Your prefix is now changed\n"
                                      f"**Old:** {oldprefix[0]}\n"
                                      f"**New:** {arg}\n"
                                      f"You can also use @MODUS for commands even if you forget your prefix")

            elif isprefixold is False:
                embed.add_field(name=prefix, value=f"Your prefix is now changed\n"
                                                   f"**New:** {arg}")

            await ctx.send(embed=embed)

        except Exception as e:
            print(e)
            await ctx.send("Something went wrong here. Contact support over at https://discord.gg/hMfgSaN")


def setup(client):
    client.add_cog(Admin_Commands(client))
