from nextcord import Interaction, SlashOption
from nextcord.ext import commands
import json, nextcord, os

bot = commands.Bot(command_prefix="$")
stats = json.load(open("stats.json"))

# Define hydrates in array and costs in dict
class Redeems:
    async def hydrate(self, uid, showname):
        if not showname:
            await bot.get_channel(968222515493220472).send(f"@everyone an anonymous user has redeemed hydrate! Sippies time!!!")
        else:
            await bot.get_channel(968222515493220472).send(f"@everyone <@{uid}> has redeemed hydrate! Sippies time!!!")

redeems_dict = {
    "hydrate": {
        "desc": "Force the members to hydrate!",
        "cost": 100,
        "func": Redeems().hydrate
    }
}

def getPoints(uid):
    global stats
    if uid not in list(stats.keys()):
        stats[uid] = 0
        json.dump(stats, open("stats.json", "w"), indent=4)
        return 0
    else:
        if str(stats[uid]).endswith('.5'):
            return int(stats[uid]-.5)
        return int(stats[uid])

def changePoints(ctype, uid, amount):
    global stats
    if uid not in list(stats.keys()):
        stats[uid] = 0
    if ctype == "add":
        stats[uid] += amount
    else:
        stats[uid] -= amount
    json.dump(stats, open("stats.json", "w"), indent=4)

async def doRedeem(uid, redeem, showname):
    if getPoints(uid) >= redeems_dict[redeem]['cost']:
        changePoints("sub", uid, redeems_dict[redeem]['cost'])
        await redeems_dict[redeem]['func'](uid, showname)
        return True
    else:
        return False

@bot.event
async def on_message(message):
    if message.author.id in [968143251360079983, 302050872383242240, 704802632660943089, 375805687529209857, 948664174114902037, 204255221017214977]:
        return
    else:
        changePoints("add", str(message.author.id), 0.5)

@bot.slash_command(description="Get a list of possible channel point redemptions")
async def redeems(interaction: Interaction):
    embed=nextcord.Embed(title=f"**Redeems For {interaction.guild.name}**", color=0x84a5f0)
    for redeem in list(redeems_dict.keys()):
        embed.add_field(name=f"{redeem}", value=f"Description: {redeems_dict[redeem]['desc']}\nCost: {redeems_dict[redeem]['cost']} points", inline=False)
    embed.set_footer(text="Bot created by Willow")
    await interaction.response.send_message(embed=embed)

@bot.slash_command(description="Get your current points!")
async def getpoints(interaction: Interaction):
    embed=nextcord.Embed(color=0x84a5f0)
    embed.add_field(name=f"{interaction.user.display_name}'s points", value=getPoints(str(interaction.user.id)), inline=False)
    ranking = sorted(stats, key=stats.get, reverse=True).index(str(interaction.user.id))+1
    embed.set_footer(text=f"Server Rank: {ranking}/{len(list(stats.keys()))+1} | Bot created by Willow")
    await interaction.response.send_message(embed=embed)

@bot.slash_command(description="Redeem a reward with your points!")
async def redeem(
    interaction: Interaction,
    redeem: str = SlashOption(description="What you are redeeming (use /redeems for a full list)", required=True),
    showname: str = SlashOption(description="Show your name on the group member ping? (Y/N)", required=False)
):
    if showname.lower() == "n":
      showname = False
    else:
      showname = True
    redeem = redeem.lower()
    if redeem in list(redeems_dict.keys()):
        if not await doRedeem(str(interaction.user.id), redeem, showname=showname):
            needed = redeems_dict[redeem]['cost'] - getPoints(str(interaction.user.id))
            await interaction.response.send_message(f"You don't have enough points!\n(Need {needed} more points)", ephemeral=True)
        else:
            await interaction.response.send_message(f"You have redeemed {redeem}! All group members have been pinged!", ephemeral=True)
    else:
        await interaction.response.send_message(f"{redeem} is not a valid redeem. For a full list, please use /redeems", ephemeral=True)

bot.run(os.environ['token'])