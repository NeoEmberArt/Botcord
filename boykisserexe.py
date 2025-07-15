import discord
import random
import re
import os
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()  # Loads variables from .env if running locally

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True
intents.messages = True

MUZZLED_ROLE_NAME = "Muzzled"
webhooks_cache = {}

MUFFLED_MESSAGES_NORMAL = [
    "*Muffled sounds*", "*paws at muzzle helplessly*", "*sits down and huffs softly*",
    "*makes soft squeaky noises*", "*pouts silently*", "*softly squeaking through the muzzle*",
    "*submissive floppy bean energy*", "*Whimpering under a muzzle*", "*Cute sounds*",
    "*cutely vibrating in place*", "*I blink slowly and accept my fate*", "*happy muffled giggling*",
    "*Small adorable noises*", "*Trying to say I'm cute but I can't*", "*Just plain cute noises coming out*",
    "MMMMRFRRFRFF", "*muffled mumbles*", "*just sits here blushing*", "*wags tail because I'm into it*",
    "*grumpy cutie sounds*", "*just being a good boy*", "*Is muzzed like a kinky bean~*",
    "Im adorable... Wait, im supposed to be muzzled.. i mean MERRRFFFFFMMM!!!!",
    "I'm adorable!!", "im the cutest  ;3", "*nods in agreement*"
]

MUFFLED_MESSAGES_LOUD = [
    "*Muffled screams*", "*starts vibrating aggressively*", "*furiously muffled yells*",
    "*throws a tantrum in place*", "*grrrRrrrRRrrRRrrr*", "*growling and yipping under muzzle*",
    "*wags tail without a sound*", "*Angry muffled screaming*", "*FULL POWER GROWLS*",
    "*struggles violently in adorable rage*", "*slams tiny fists in frustration*", "*bounces violently in place*",
    "*throws things but it's cute*", "*STOMP STOMP STOMP*", "*YELPS IN GAY*", "*REEEEEEE*",
    "*squirming around!~*", "*Angry I can't bite  >:C*", "*Gay Screaming*", "*Gay panic*",
    "*vigorously flails tail, an angry bean*", "*GRRRRRRR!!!*", "*GRR GRRRR!!!!!!!*", "*GROWLS*"
]

class MuzzleBot(commands.Bot):
    async def setup_hook(self):
        await self.tree.sync()
        print("Slash commands synced.")

bot = MuzzleBot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Bot is online as {bot.user}")

@bot.tree.command(name="muzzle", description="Give someone the Muzzled role")
@discord.app_commands.describe(member="User to muzzle")
async def muzzle(interaction: discord.Interaction, member: discord.Member):
    if not interaction.user.guild_permissions.manage_roles:
        await interaction.response.send_message("You don't have permission to do this.", ephemeral=True)
        return

    role = discord.utils.get(interaction.guild.roles, name=MUZZLED_ROLE_NAME)
    if not role:
        role = await interaction.guild.create_role(name=MUZZLED_ROLE_NAME)

    await member.add_roles(role)
    await interaction.response.send_message(f"{member.mention} has been muzzled.", ephemeral=False)

@bot.tree.command(name="unmuzzle", description="Remove the Muzzled role from someone")
@discord.app_commands.describe(member="User to unmuzzle")
async def unmuzzle(interaction: discord.Interaction, member: discord.Member):
    if not interaction.user.guild_permissions.manage_roles:
        await interaction.response.send_message("You don't have permission to do this.", ephemeral=True)
        return

    role = discord.utils.get(interaction.guild.roles, name=MUZZLED_ROLE_NAME)
    if role and role in member.roles:
        await member.remove_roles(role)
        await interaction.response.send_message(f"{member.mention} has been unmuzzled.", ephemeral=False)
    else:
        await interaction.response.send_message(f"{member.display_name} is not muzzled.", ephemeral=True)

def is_loud_message(content: str) -> bool:
    letters = [c for c in content if c.isalpha()]
    if not letters:
        return False
    uppercase_count = sum(1 for c in letters if c.isupper())
    return (uppercase_count / len(letters)) >= 0.5

@bot.event
async def on_message(message):
    if message.author.bot or not message.guild:
        return

    role = discord.utils.get(message.guild.roles, name=MUZZLED_ROLE_NAME)
    lowered = message.content.lower()

    if any(trigger in lowered for trigger in [
        "who is the gayest", "who's the gayest", "whos the gayest",
        "who is the cutest", "who's the cutest", "whos the cutest",
        "who's a good girl", "who is a good girl", "whos a good girl",
        "who's a good boy", "who is a good boy", "whos a good boy"
    ]):
        category = None
        if "gayest" in lowered:
            category = "gayest"
        elif "cutest" in lowered:
            category = "cutest"
        elif "good girl" in lowered:
            category = "good girl"
        elif "good boy" in lowered:
            category = "good boy"

        members = [m.display_name for m in message.guild.members if role and role in m.roles]

        if members:
            chosen = random.choice(members)
            templates = {
                "gayest": [
                    f"Oh I know this, it's {chosen}~",
                    f"I think it's {chosen}, with the way they wear that muzzle ;3",
                    f"The muzzled ones, totally. Ya know... {chosen}",
                    f"Clearly {chosen}, no competition",
                    f"{chosen}. Obv.",
                    f"Have you seen {chosen} lately? Case closed.",
                    f"Hmm... probably {chosen}~",
                    f"*Looks around suspiciously*... it's {chosen}",
                ],
                "cutest": [
                    f"{chosen} wins. No question.",
                    f"The cutest? Gotta be {chosen}~",
                    f"{chosen} just *radiates* adorable energy",
                    f"{chosen} makes my tail wag tbh",
                    f"*blushes* it's totally {chosen}",
                    f"{chosen} is a walking squeak toy of cuteness",
                    f"I bet {chosen} can't even help being that cute",
                ],
                "good girl": [
                    f"{chosen} is such a good girl~",
                    f"I've seen good girls... and then there's {chosen} 😳",
                    f"*headpats {chosen} lovingly*",
                    f"Awwww, {chosen} for sure~",
                    f"{chosen} has major good girl energy",
                    f"{chosen} gets all the treats for being good",
                ],
                "good boy": [
                    f"{chosen} is the goodest boy~",
                    f"Good boy? That’s gotta be {chosen}",
                    f"*pats {chosen}'s head and gives cookie*",
                    f"Such a good boyyy~ {chosen} deserves it",
                    f"{chosen} has the best tail wags, 10/10 good boy",
                    f"Definitely {chosen}, no question!",
                ],
            }
            reply = random.choice(templates[category])
        else:
            reply = "you are! :3"

        await message.channel.send(reply)
        return

    if role and role in message.author.roles:
        await message.delete()
        content = message.content.lower()

        if any(phrase in content for phrase in ["no", "shut up", "sybau", "shut the fuck up", "fuck you", "nuhuh"]):
            reply = random.choice([
                "keep talking", "so true", "yeah ^^ tell me more", "yup",
                "*nods in agreement*", "*mhmm mhmm ^^*"
            ])
        elif re.search(r"\b(yes+)\b", content):
            reply = random.choice(["nuhuhhhh", "nope~", "*muffled disagreement*"])
        elif re.search(r"\b(no+|nuh+|nuhuh+)\b", content):
            reply = random.choice(["*Nods*", "yes!!", "*enthusiastic muffled nod*"])
        else:
            reply = random.choice(
                MUFFLED_MESSAGES_LOUD if is_loud_message(message.content) else MUFFLED_MESSAGES_NORMAL
            )

        name = message.author.display_name
        pfp = message.author.avatar.url if message.author.avatar else message.author.default_avatar.url

        webhook = webhooks_cache.get(message.channel.id)
        if webhook is None:
            webhook = await message.channel.create_webhook(name="MuffledSender")
            webhooks_cache[message.channel.id] = webhook

        await webhook.send(reply, username=name, avatar_url=pfp)
    else:
        await bot.process_commands(message)

# Start the bot using env variable
bot.run(os.environ.get("DISCORD_TOKEN"))
