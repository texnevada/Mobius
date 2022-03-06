# import discord library
import discord
# Imports commands
from discord.ext import commands
from discord import app_commands
import requests
# Allows the code to retrieve data online
from datetime import datetime
import configparser


class User_F76_NukeCodes(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.load_command()
        tree = self.client.tree

    def load_command(self):
        @app_commands.command()
        async def codes(interaction: discord.Interaction):
            print("A user requested nuke codes")
            config = configparser.ConfigParser()
            config.read("./config.ini")

            data = config["NukaCrypt"]["API_key"]
            r = requests.get(url=f'https://nukacrypt.com/api/codes?{data}')
            response = r.json()
            code_response = f'Nuke codes reset every <t:{response["since_epoch"]+604800}:F> \n' \
                            f'**Alpha**: {response["ALPHA"]}\n' \
                            f'**Bravo**: {response["BRAVO"]}\n' \
                            f'**Charlie**: {response["CHARLIE"]}'

            embed = discord.Embed(color=0xe7e9d3, title="Fallout 76 Nuclear Codes")

            embed.set_footer(text="Special thanks to https://nukacrypt.com/ for providing codes for all these years!")
            # embed.set_image(url="")
            config = configparser.ConfigParser()
            config.read("./config.ini")
            embed.set_thumbnail(url=config["EDB.TOOLS"]["F76_NukeCodes"])

            embed.add_field(name="This week's nuclear codes",
                            value=code_response)

            await interaction.response.send_message(embed=embed)

        self.client.tree.add_command(codes)  # , guild=discord.Object(id=guild.id))


# ends the extension
def setup(client):
    client.add_cog(User_F76_NukeCodes(client))
