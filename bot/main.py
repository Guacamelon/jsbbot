from dotenv import load_dotenv
import discord
from discord.ext import commands
import sqlite3
import os
import requests
import json

def sliceTo(string,slicedAt):
    return string[0:string.find(slicedAt)]
def sliceFrom(string,slicedAt):
    return string[string.find(slicedAt)+(len(slicedAt)):len(string)]


# Startup
class Client(commands.Bot):
   async def on_ready(self):
      print(f'{self.user} is now running!')
      await client.change_presence(activity=discord.Game("/beatpoints"))

      try:
         guild = discord.Object(id=1165318900892839946)
         synced = await self.tree.sync(guild=guild)
         print(f'Synced {len(synced)} commands to guild {guild.id}')
      except Exception as e:
         print(f'Error syncing commands: {e}')

# Fancy bot stuff
intents = discord.Intents.default()
intents.message_content = True

load_dotenv("token.env")
TOKEN: str = os.getenv("TOKEN")
client = Client(command_prefix="!", intents=intents)
GUILD_ID = discord.Object(id=1165318900892839946)

database = sqlite3.connect('playerstest.db')
cursor = database.cursor()
database.execute("CREATE TABLE IF NOT EXISTS consoletest(user_id STR, display STR, pronouns STR, bp_total INT, bp_steam INT, bp_nswitch INT, bp_playst INT, bp_xbox INT, bp_stadia INT, shape STR, track STR, artist STR, color STR, vetted INT, avatar STR)")



@client.tree.command(name="nitrofun", description="!nitrofun", guild=GUILD_ID)
async def nitroFun(interaction: discord.Interaction):
   await interaction.response.send_message("Nitro Fun sucks!")

@client.tree.command(name="setbp", description="Set how many beatpoints you've collected", guild=GUILD_ID)
async def bpSet(interaction: discord.Interaction, steam: int=None, nswitch: int=None, playstation: int=None, xbox: int=None):

   interaction_user = str(interaction.user.name)

   cursor.execute(f"SELECT * FROM consoletest WHERE user_id = '{interaction_user}'")
   result = cursor.fetchone()

   if result is None:
      vetted = 0
   else:
      vetted = result[13]

   if (steam or nswitch or playstation or xbox) < 750000 or vetted == 1:
      if result is None:
      # Create new record

         if steam is None:
            steam = 0
         if nswitch is None:
            nswitch = 0
         if playstation is None:
            playstation = 0
         if xbox is None:
            xbox = 0

         query = "INSERT INTO consoletest (user_id, bp_total, bp_steam, bp_nswitch, bp_playst, bp_xbox, bp_stadia, vetted, avatar) VALUES (?, 0, ?, ?, ?, ?, 0, 0, ?)"
         cursor.execute(query, (interaction_user, steam, nswitch, playstation, xbox, interaction.user.avatar.url))
         database.commit()

         print(f"NEW: Set {interaction_user}'s bp!")
         await interaction.response.send_message(f"Your beatpoints were set for the first time!")
      
      else: 
      # Update existing record

         if steam is None:
            steam = result[4]
         if nswitch is None:
            nswitch = result[5]
         if playstation is None:
            playstation = result[6]
         if xbox is None:
            xbox = result[7]

         query = (f"UPDATE consoletest SET bp_steam = ?, bp_nswitch = ?, bp_playst = ?, bp_xbox = ?, avatar = ? WHERE user_id = '{interaction_user}'")
         cursor.execute(query, (steam, nswitch, playstation, xbox, interaction.user.avatar.url))
         database.commit()

         print(f"Set {interaction_user}'s bp!")
         await interaction.response.send_message(f"Your bp count was updated to!", ephemeral=True)

      # Update bp total
      cursor.execute(f"SELECT bp_steam, bp_nswitch, bp_playst, bp_xbox, bp_stadia FROM consoletest WHERE user_id = '{interaction_user}'")
      bp_banks = cursor.fetchone()
      int_bptotal = bp_banks[0] + bp_banks[1] + bp_banks[2] + bp_banks[3] + bp_banks[4]
               
      query = (f"UPDATE consoletest SET bp_total = ? WHERE user_id = '{interaction_user}'")
      cursor.execute(query, (int_bptotal,))
      database.commit()

   else:
      print(f"Hey! {interaction_user} tried to set bp to a high amount. Needs vetting.")
      await interaction.response.send_message(f"Anything above 750,000 bp needs verification!", ephemeral=True)

@client.tree.command(name="beatpoints", description="Show how many beatpoints total you've collected! [Type username plain for other users]", guild=GUILD_ID)
async def bpShow(interaction: discord.Interaction, user: str=None):

   interaction_user = str(interaction.user.name)
   if user is None:
      user = interaction_user
   cursor.execute(f"SELECT bp_total, bp_steam, bp_nswitch, bp_playst, bp_xbox, bp_stadia, vetted, avatar FROM consoletest WHERE user_id = '{user}'")
   data = cursor.fetchone()

   bp_total = data[0]
   bp_steam = data[1]
   bp_nswitch = data[2]
   bp_playst = data[3]
   bp_xbox = data[4]
   bp_stadia = data[5]
   vetted = data[6]
   avatar_url = data[7]

   if bp_total >= 1000000:
      embedcolor = '#E29BCC'
   elif bp_total >= 500000:
      embedcolor = '#FF327F'
   elif bp_total >= 250000:
      embedcolor = '#FE0062'
   elif bp_total >= 100000:
      embedcolor = '#46277A'
   elif bp_total >= 50000:
      embedcolor = '#4775FF'
   elif bp_total >= 25000:
      embedcolor = '#18BFFE'
   elif bp_total >= 10000:
      embedcolor = '#15C2D4'
   elif bp_total < 10000: 
      embedcolor = '#004C51'

   embed = discord.Embed(title=(f"{bp_total:,}"), description="total amount of bp collected", color=discord.Colour.from_str(embedcolor))
   embed.set_author(name=user, icon_url=avatar_url)
   if bp_steam > 0:
      embed.add_field(name="Steam", value=(f"{bp_steam:,}"), inline=True)
   if bp_nswitch > 0:
      embed.add_field(name="Nintendo Switch", value=(f"{bp_nswitch:,}"), inline=True)
   if bp_playst > 0:
      embed.add_field(name="Playstation", value=(f"{bp_playst:,}"), inline=True)
   if bp_xbox > 0:
      embed.add_field(name="Xbox", value=(f"{bp_xbox:,}"), inline=True)
   if bp_stadia > 0:
      embed.add_field(name="Stadia", value=(f"{bp_stadia:,}"), inline=True)
   if vetted == 1:
      embed.set_footer(text="Vetted!")

   await interaction.response.send_message(embed=embed)

@client.tree.command(name="ribbon", description="Show your ribbon with your profile! [Type username plain for other users]", guild=GUILD_ID)
async def ribbonShow(interaction: discord.Interaction, user: str=None):

   interaction_user = interaction.user.name
   if user is None:
      user = interaction_user
   cursor.execute(f"SELECT * FROM consoletest WHERE user_id = '{user}'")
   data = cursor.fetchone()

   print(interaction.user.name)

   str_user = client.get_user(user)

   username = data[0]
   display = data[1]
   pronouns = data[2]
   bp_total = data[3]
   shape = data[4]
   track = data[5]
   artist = data[6]
   usercolor = data[7]
   vetted = data[8]
   avatar_url = data[9]

   if bp_total >= 1000000:
      embedcolor = '#E29BCC'
   elif bp_total >= 500000:
      embedcolor = '#FF327F'
   elif bp_total >= 250000:
      embedcolor = '#FE0062'
   elif bp_total >= 100000:
      embedcolor = '#46277A'
   elif bp_total >= 50000:
      embedcolor = '#4775FF'
   elif bp_total >= 25000:
      embedcolor = '#18BFFE'
   elif bp_total >= 10000:
      embedcolor = '#15C2D4'
   elif bp_total < 10000: 
      embedcolor = '#004C51'

   embed = discord.Embed(title=display, description=pronouns, color=discord.Colour.from_str(embedcolor))
   embed.set_author(name=username, icon_url=avatar_url)
   embed.set_thumbnail(url="https://soggy.cat/static/ssoggycat/main/images/soggycat.webp")
   embed.add_field(name=bp_total, value="total amount of bp collected")
   

   await interaction.response.send_message(embed=embed)
   
@client.tree.command(name="level", description="Get information about a JS&B level!", guild=GUILD_ID)
async def level(interaction: discord.Interaction, level: str=None):
   
   print("Type the name of a page on the JS&B Wiki")
   levelName = level

   requestData = json.loads(requests.get(f"https://justshapesandbeats.fandom.com/api.php?action=query&prop=revisions&rvprop=content&titles={levelName}&rvsection=0&format=json").text)

   levelInfo = (requestData['query']['pages'])[next(iter(requestData['query']['pages']))]['revisions'][0]['*']
   # levelInfo = levelInfo[0:)]
   # print(levelInfo)

   # punch this string over and over again until we can turn it into a proper dict

   levelInfo = sliceFrom(levelInfo,"Level|")
   levelInfo = sliceTo(levelInfo,"}}'''")
   levelInfo = levelInfo.replace("\n","")
   levelInfo = levelInfo.replace("|","\",\"")
   levelInfo = levelInfo.replace(" = ","\":\"")
   levelInfo = '{"' + levelInfo + '"}'
   levelInfo = levelInfo.replace("_"," ")
   levelInfo=levelInfo

   levelInfoDict = json.loads(levelInfo)

   print(levelInfoDict)

   embed = discord.Embed(title=(f"{levelName}"), description="", color=discord.Colour.from_str("#f92073")) 

   #ADD EMBED FIELDS
   #{'image1': 'HYPE3.png', 'composer': 'Tokyo Machine', 'level_type': '{{ExtraText}}', 'checkpoints': '3', 'duration': '1:30 (3:02)', 'level_number': '34', 'unlocked_by': 'Obtain 1000 Beatpoints'}
   
   levelInfoDict.pop("image1")
   for key,val in levelInfoDict.items():
      embed.add_field(name=key.capitalize(), value=val)

   await interaction.response.send_message(embed = embed)



client.run(TOKEN)