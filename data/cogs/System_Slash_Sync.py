# import discord library
import discord
# Imports commands
from discord.ext import commands
from discord import app_commands
from data.functions.owner import is_owner


class Admin_Slash_Sync(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.load_command()

    def load_command(self):
        tree = self.client.tree

        @app_commands.command()
        @is_owner()
        async def sync(interaction: discord.Interaction):
            try:
                await tree.sync()
                await interaction.response.send_message("Slash command sync complete ✅")
            except Exception as e:
                await interaction.response.send_message(e)

    @commands.command()
    @is_owner()
    async def sync(self, ctx):
        try:
            await self.client.tree.sync()
            await ctx.send("Slash command sync complete ✅")
        except Exception as e:
            await ctx.send(e)


# ends the extension
def setup(client):
    client.add_cog(Admin_Slash_Sync(client))
