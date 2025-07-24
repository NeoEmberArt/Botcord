import discord
import random
import re
import datetime
from discord.ext import commands
from discord import ui, app_commands

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True
intents.messages = True

MUZZLED_ROLE_NAME = "Muzzled"
webhooks_cache = {}

import json
import os

from datetime import datetime, timedelta

STATS_FILE = "muzzle_stats.json"
bot_start_time = datetime.utcnow()
muzzle_counts_since_awake = {}

def load_stats():
    if not os.path.exists(STATS_FILE):
        with open(STATS_FILE, "w") as f:
            json.dump({"muzzle_counts_today": {}, "muzzle_counts_all_time": {}}, f)
    with open(STATS_FILE, "r") as f:
        return json.load(f)

def save_stats(stats):
    with open(STATS_FILE, "w") as f:
        json.dump(stats, f, indent=2)


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

    # === Log stats ===
    stats = load_stats()
    user_id = str(member.id)

    stats["muzzle_counts_today"][user_id] = stats["muzzle_counts_today"].get(user_id, 0) + 1
    stats["muzzle_counts_all_time"][user_id] = stats["muzzle_counts_all_time"].get(user_id, 0) + 1
    save_stats(stats)

    muzzle_counts_since_awake[user_id] = muzzle_counts_since_awake.get(user_id, 0) + 1

@bot.tree.command(name="stats", description="View muzzle stats and uptime")
async def stats(interaction: discord.Interaction):
    now = datetime.utcnow()
    uptime = now - bot_start_time
    stats = load_stats()

    def format_seconds(td):
        hours, remainder = divmod(int(td.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours}h {minutes}m {seconds}s"

    def top_user(stat_dict):
        if not stat_dict:
            return "None"
        top_id = max(stat_dict, key=stat_dict.get)
        count = stat_dict[top_id]
        user = interaction.guild.get_member(int(top_id))
        return f"{user.display_name if user else 'Unknown'} ({count})"

    embed = discord.Embed(title="📊 Bot Stats", color=discord.Color.blue())
    embed.add_field(name="Uptime", value=format_seconds(uptime), inline=False)
    embed.add_field(name="Most Muzzled Today", value=top_user(stats["muzzle_counts_today"]), inline=False)
    embed.add_field(name="Most Muzzled Since Awake", value=top_user(muzzle_counts_since_awake), inline=False)
    embed.add_field(name="Most Muzzled All Time", value=top_user(stats["muzzle_counts_all_time"]), inline=False)

    await interaction.response.send_message(embed=embed)


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

@bot.tree.command(name="cage", description="Put someone in the cage (mute them)")
@discord.app_commands.describe(member="User to cage")
async def cage(interaction: discord.Interaction, member: discord.Member):
    if not interaction.user.guild_permissions.manage_roles:
        await interaction.response.send_message("You don't have permission to do this.", ephemeral=True)
        return

    caged_role = discord.utils.get(interaction.guild.roles, name="Caged")

    if not caged_role:
        caged_role = await interaction.guild.create_role(name="Caged", reason="Used /cage to mute a user")

        # Deny send messages in all current text channels
        for channel in interaction.guild.text_channels:
            await channel.set_permissions(caged_role, send_messages=False)

    await member.add_roles(caged_role)
    await interaction.response.send_message(f"{member.mention} has been locked in the cage. 🔒", ephemeral=False)

@bot.tree.command(name="uncage", description="Free someone from the cage (unmute them)")
@discord.app_commands.describe(member="User to uncage")
async def uncage(interaction: discord.Interaction, member: discord.Member):
    if not interaction.user.guild_permissions.manage_roles:
        await interaction.response.send_message("You don't have permission to do this.", ephemeral=True)
        return

    caged_role = discord.utils.get(interaction.guild.roles, name="Caged")

    if caged_role and caged_role in member.roles:
        await member.remove_roles(caged_role)
        await interaction.response.send_message(f"{member.mention} has been released from the cage. 🗝️", ephemeral=False)
    else:
        await interaction.response.send_message(f"{member.display_name} is not in the cage.", ephemeral=True)


def is_loud_message(content: str) -> bool:
    letters = [c for c in content if c.isalpha()]
    if not letters:
        return False
    uppercase_count = sum(1 for c in letters if c.isupper())
    return (uppercase_count / len(letters)) >= 0.5

@bot.event
@bot.event
async def on_message(message):
    if message.author.bot or not message.guild:
        return

    role = discord.utils.get(message.guild.roles, name=MUZZLED_ROLE_NAME)
    lowered = message.content.lower()

    # === Fun Phrases ===
        # === Fun Phrases ===
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
            # No one muzzled fallback
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



class VerifyButton16(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Accept Rules", style=discord.ButtonStyle.success, custom_id="accept_rules_button")
    async def accept_rules(self, interaction: discord.Interaction, button: discord.ui.Button):
        role = discord.utils.get(interaction.guild.roles, name="Generate")
        if role:
            await interaction.user.add_roles(role)
            await interaction.response.send_message("You've been verified! Welcome!~", ephemeral=True)
        else:
            await interaction.response.send_message("Role not found, Contact a moderator!.", ephemeral=True)

class DOBModal(ui.Modal, title="18+ Age Verification"):
    dob_input = ui.TextInput(label="Enter your date of birth (MM/DD/YYYY)", placeholder="MM/DD/YYYY")

    def __init__(self, min_age: int = 18, role_name: str = "Degenerate"):
        super().__init__()
        self.min_age = min_age
        self.role_name = role_name

    async def on_submit(self, interaction: discord.Interaction):
        try:
            dob = datetime.strptime(self.dob_input.value.strip(), "%m/%d/%Y")
            age = (datetime.now() - dob).days // 365
        except ValueError:
            await interaction.response.send_message("Invalid date format. Use MM/DD/YYYY.", ephemeral=True)
            return

        role = discord.utils.get(interaction.guild.roles, name=self.role_name)
        if not role:
            role = await interaction.guild.create_role(name=self.role_name)

        if age >= self.min_age:
            await interaction.user.add_roles(role)
            await interaction.response.send_message(f"Verified {self.min_age}+! Welcome to the dark side~", ephemeral=True)
        else:
            await interaction.response.send_message(f"Sorry, you must be at least {self.min_age} years old.", ephemeral=True)

class VerifyButton18(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Verify 18+", style=discord.ButtonStyle.danger, custom_id="verify_18_button_unique")
    async def verify_18_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(DOBModal())



@bot.tree.command(name="addverify", description="Post rules and 18+ verification embeds")
async def addverify(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)

    embed_rules = discord.Embed(
        title="📜 Server Rules",
        description=(
            "Welcome! To access this server, you must be **16 years or older**.\n\n"
            "Please follow all server rules and respect everyone.\n"
            "- No harassment\n"
            "- Keep content appropriate and SFW!\n"
            "# Sound good?"
        ),
        color=discord.Color.green()
    )

    embed_18 = discord.Embed(
        title="🔞 18+ NSFW Access",
        description=(
            "Click the button below and enter your birthdate (MM/DD/YYYY) to verify you are 18 or older.\n\n"
            "**Users under 18 will be denied access or banned**\n"
            "> ⚠️ Your birthdate cannot be seen by others and is not stored!"
        ),
        color=discord.Color.orange()
    )

    await interaction.channel.send(embed=embed_rules, view=VerifyButton16())
    await interaction.channel.send(embed=embed_18, view=VerifyButton18())
    await interaction.followup.send("Rules and verification embeds sent.", ephemeral=True)








class NSFWVerifyModal(ui.Modal, title="NSFW Access Verification"):
    dob_input = ui.TextInput(label="Enter your date of birth (MM/DD/YYYY)", placeholder="MM/DD/YYYY")

    def __init__(self, min_age: int = 18, role_name: str = "Verified"):
        super().__init__()
        self.min_age = min_age
        self.role_name = role_name

    async def on_submit(self, interaction: discord.Interaction):
        try:
            dob = datetime.strptime(self.dob_input.value.strip(), "%m/%d/%Y")
            age = (datetime.now() - dob).days // 365
        except ValueError:
            await interaction.response.send_message("Invalid date format. Use MM/DD/YYYY.", ephemeral=True)
            return

        if age < self.min_age:
            await interaction.response.send_message("Access denied. You must be 18+.", ephemeral=True)
            return

        guild = interaction.guild
        role = discord.utils.get(guild.roles, name=self.role_name)
        if not role:
            role = await guild.create_role(name=self.role_name, reason="NSFW Verification")

        await interaction.user.add_roles(role)
        await interaction.response.send_message(f"You are now verified for NSFW access.", ephemeral=True)

        # Update permissions for all channels
        for channel in guild.channels:
            if isinstance(channel, (discord.TextChannel, discord.VoiceChannel)):
                await channel.set_permissions(guild.default_role, view_channel=False)
                await channel.set_permissions(role, view_channel=True)


class VerifyNSFW(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Verify age", style=discord.ButtonStyle.danger, custom_id="verify_nsfw_button")
    async def verify_nsfw_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(NSFWVerifyModal())



@bot.tree.command(name="setup", description="Set up rules and NSFW 18+ verification")
async def addverify(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("Only administrators can use this command.", ephemeral=True)
        return

    await interaction.response.defer(ephemeral=True)

    guild = interaction.guild

    # Create or get Verified role
    role_name = "Verified"
    verified_role = discord.utils.get(guild.roles, name=role_name)
    if not verified_role:
        verified_role = await guild.create_role(name=role_name, reason="Used for NSFW access control")

    # Create or get #rules channel
    rules_channel = discord.utils.get(guild.text_channels, name="rules")
    if not rules_channel:
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=True, send_messages=False),
            verified_role: discord.PermissionOverwrite(view_channel=True, send_messages=False)
        }
        rules_channel = await guild.create_text_channel(
            name="rules",
            overwrites=overwrites,
            reason="Rules and NSFW Verification"
        )
        await rules_channel.edit(position=0)
    else:
        await rules_channel.set_permissions(guild.default_role, view_channel=True, send_messages=False)
        await rules_channel.set_permissions(verified_role, view_channel=True, send_messages=False)

    # Hide all other channels from @everyone, show to Verified
    for channel in guild.channels:
        if channel == rules_channel:
            continue
        if isinstance(channel, (discord.TextChannel, discord.VoiceChannel, discord.CategoryChannel)):
            try:
                await channel.set_permissions(guild.default_role, view_channel=False)
                await channel.set_permissions(verified_role, view_channel=True)
            except discord.Forbidden:
                print(f"⚠️ Bot lacks permission to edit {channel.name}")
            except Exception as e:
                print(f"⚠️ Unexpected error updating {channel.name}: {e}")

    # Age Verification Embed
    age_embed = discord.Embed(
        title="🔞 Age Verification Required",
        description=(
            "**To access this server, you must be 18 years or older.**\n\n"
            "Click the button below and enter your birthdate in the format `MM/DD/YYYY`.\n\n"
            "⚠️ **Users under 18 will be denied access or removed.**\n"
            "*Your birthdate cannot be seen by others and is not stored.*"
        ),
        color=discord.Color.red()
    )
    age_embed.set_thumbnail(url="https://media.istockphoto.com/id/1350885528/vector/under-18-sign-warning-symbol-over-18-only-censored-eighteen-age-older-forbidden-adult.jpg?s=612x612&w=0&k=20&c=ast2XCxr0wfHm1XBDWL-u2sfsnfkZvUoPjE_h5-YsPE=")

    # Server Rules Embed
    rules_embed = discord.Embed(
        title="📜 Server Rules",
        color=discord.Color.blue()
    )
    rules_embed.add_field(
        name="Respect and Behavior",
        value="• Be kind and respectful to all members.\n• No harassment, hate speech, or bullying.\n• __NO DRAMA__: keep all drama private or in DMs or you will be silenced\n",
        inline=False
    )
    rules_embed.add_field(
        name="Content Guidelines",
        value="• NSFW content only in designated channels.\n• No illegal or harmful content.\n• Avoid spamming or trolling.",
        inline=False
    )
    rules_embed.add_field(
        name="Privacy and Safety",
        value="• Do not share personal information.\n• Follow [Discord's Terms of Service](https://discord.com/terms).",
        inline=False
    )
    rules_embed.set_footer(text="By verifying, you agree to follow all server rules.")
    rules_embed.set_thumbnail(url="https://cdn-icons-png.flaticon.com/512/760/760205.png")

    # Send both embeds to #rules
    await rules_channel.send(embed=age_embed)
    await rules_channel.send(embed=rules_embed, view=VerifyNSFW())  # Add button to this one

    # Final confirmation to admin
    await interaction.followup.send("✅ Setup complete.\n\n# What i did:\n• Created verified role\n• Created rules channel\n• Made all channeles hidden without verified role.", ephemeral=True)





import os

# === Bot Ready ===
@bot.event
async def on_ready():
    bot.add_view(VerifyButton16())
    bot.add_view(VerifyButton18())
    bot.add_view(VerifyNSFW())  # important
    await bot.tree.sync()
    print(f"Logged in as {bot.user} and ready.")



# === Run the Bot ===
TOKEN = os.getenv("ALTOBOT_TOKEN")
if TOKEN:
    bot.run(TOKEN)
else:
    print("DISCORD_TOKEN not set in environment variables.")
