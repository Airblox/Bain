import asyncio
import string
import coolname
import discord
import random
import datetime
import humanfriendly
import wikipedia
import aiohttp
import ast
import copy
import names
import json
import os
import randomjob
import baintools
import secrets as secret_files

from datetime import date
from collections import Counter
from discord.ext import commands
from discord.ui import Button, Select, View, Modal, InputText
from wikipedia import PageError, DisambiguationError
from baintools import PlayerInfo, PlayerHeist


print("Bain is connecting to CRIME.NET...")

# Secrets
def get_secrets():
    dicts = {}
    for item in dir(secret_files):
        if not item.startswith("__"):
            dicts[item] = getattr(secret_files, item)[0] if type(getattr(secret_files, item)) == tuple else getattr(secret_files, item)

    return dicts


secrets = get_secrets()
os.chdir(secrets["os_dir"])

bot = commands.Bot(command_prefix=".", intents=discord.Intents.all(), owner_id=secrets["owner_id"],
                   auto_sync_commands=True)
bot.remove_command("help")

steam_api_key = secrets["steam_api_key"]

# Error handling
"""@bot.event
async def on_command_error(ctx, error):
    if str(error).endswith("\" is not found"):
        pass
    else:
        await ctx.reply(f"An error occured.\n`{error}`")"""


@bot.event
async def on_ready():
    await bot.change_presence(status=discord.Status.online, activity=discord.Game(name="CRIME.NET | .help"))
    guild_count = 0
    print("Bain is online, and is in the following servers:")
    for guild in bot.guilds:
        print(f"- {guild.name} ({guild.owner}, {guild.id}).")
        guild_count = guild_count + 1

    print(f"(In {guild_count} servers in total.)")


class HelpView(View):
    def __init__(self, ctx):
        super().__init__(timeout=180)
        self.ctx = ctx

    @discord.ui.select(
        max_values=1,
        placeholder="Choose a category...",
        options=[
            discord.SelectOption(label="General", emoji="🎁", description="General commands, for fun!"),
            discord.SelectOption(label="Currency - Page 1", emoji="💵",
                                 description="Get money and earn your payday. Get rich!"),
            discord.SelectOption(label="Currency - Page 2", emoji="💵",
                                 description="Get money and earn your payday. Get rich!"),
            discord.SelectOption(label="Tools", emoji="🛠", description="Useful (and unuseful) tools!"),
            discord.SelectOption(label="Mathematics", emoji="🔢", description="Calculators & equation solvers!"),
            discord.SelectOption(label="Moderation", emoji="📳",
                                 description="Moderation commands! (Moderate members needed)"),
            discord.SelectOption(label="Administration", emoji="🛡️",
                                 description="Administration commands! (Administrator needed)")
        ])
    async def select_callback(self, select: discord.ui.Select, interaction):
        embed = discord.Embed(
            title="Help Section",
            description='View all the available commands here. Separate parameters with commas. Wrap quotations around multi-word parameter (but don\'t put commas afterwards). Our prefix is ".".',
            color=discord.Colour.green()
        )
        embed.set_thumbnail(url="https://i.pinimg.com/originals/15/6a/86/156a86c143634a2e444b673a7b373b46.jpg")
        """
        FIELDS START HERE!
        """
        embed.add_field(
            name="help",
            value="Displays this message (the list of commands).\nParameters: none.",
            inline=False
        )
        embed.add_field(
            name="stillonline",
            value="See if I'm still online!\nParameters: none",
            inline=False
        )
        embed.add_field(
            name="kill",
            value="Someone in your way? We hire the best hitmen and henchmen to help you kill your target!.\nParameters: ``target``",
            inline=False
        )
        embed.add_field(
            name="ask8ball",
            value="Ask 8-ball something that you can't decide!\nParameters: ``question``",
            inline=False
        )
        embed.add_field(
            name="tryitandsee",
            value="What happens? Try it and see!\nParameters: none",
            inline=False
        )
        embed.add_field(
            name="duckee",
            value="Start a Duckee Match!\nParameters: ``competitor``",
            inline=False
        )
        embed.add_field(
            name="nitro",
            value="Generate a Nitro gift link!\nParameters: none.",
            inline=False
        )
        embed.add_field(
            name="clearmatches",
            value="Sets number of matches to 0.\nParameters: none.",
            inline=False
        )
        embed.add_field(
            name="hack",
            value="Infiltrate their computer, government record, or the bank account...\nParameters: ``user``",
            inline=False
        )
        currencyembed = discord.Embed(
            title="Help Section/Currency/1",
            description='View all the available moderation commands here. Separate parameters with commas. Wrap quotations around multi-word parameters (but don\'t put commas afterwards). Our prefix is ".".',
            color=discord.Colour.green()
        )
        currencyembed.set_thumbnail(url="https://i.pinimg.com/originals/15/6a/86/156a86c143634a2e444b673a7b373b46.jpg")
        currencyembed.add_field(
            name="profile",
            value="Check your/other people's profile!\nParameters: ``target_user_(optional)``",
            inline=False
        )
        currencyembed.add_field(
            name="balance/bal",
            value="Check your/other people's balance!\nParameters: ``target_user_(optional)``",
            inline=False
        )
        currencyembed.add_field(
            name="withdraw/draw",
            value="Get money out of your bank account!\nParameters: ``amount``",
            inline=False
        )
        currencyembed.add_field(
            name="deposit/dep",
            value="Put money into your back account!\nParameters: ``amount``",
            inline=False
        )
        currencyembed.add_field(
            name="bet",
            value="Test your luck! Bet some cash with Bain! \nParameters: `amount_(default=100)`",
            inline=False
        )

        currencyembed.add_field(
            name="shop/buy",
            value="Spend your money on weapons and armour!\nFill in the parameter if you want to buy an item. Don't if you're just viewing items.\nParameters: ``item_(optional)``",
            inline=False
        )
        currencyembed.add_field(
            name="sell",
            value="Sell your guns and armour!\nParameters: ``item``, ``amount_(optional,_default=1)``",
            inline=False
        )
        currencyembed.add_field(
            name="inventory/inv",
            value="Check out your inventory, about what (and how many) guns you have!\nParameters: ``user_(optional,_default=yourself)``",
            inline=False
        )
        currencyembed2 = discord.Embed(
            title="Help Section/Currency/2",
            description='View all the available moderation commands here. Separate parameters with commas. Wrap quotations around multi-word parameters (but don\'t put commas afterwards). Our prefix is ".".',
            color=discord.Colour.green()
        )
        currencyembed2.add_field(
            name="work",
            value="Do a heist job and earn money!\nParameters: none",
            inline=False
        )
        currencyembed2.add_field(
            name="fight",
            value="Fight someone with the guns you choose! (You must own them)\nParameters: ``user``",
            inline=False
        )
        currencyembed2.set_thumbnail(url="https://i.pinimg.com/originals/15/6a/86/156a86c143634a2e444b673a7b373b46.jpg")
        currencyembed2.add_field(
            name="hunt",
            value="Go hunting!\nParameters: none",
            inline=False
        )
        currencyembed2.add_field(
            name="snipe",
            value="Go sniping or hunting down people you despise!\nParameters: ``target_(optional)``",
            inline=False
        )
        currencyembed2.add_field(
            name="fish",
            value="Go fishing and reel some delicious fishy seafood back home!\nParameters: none",
            inline=False
        )
        currencyembed2.add_field(
            name="scout",
            value="Search around the world... for money.\nParameters: none",
            inline=False
        )
        currencyembed2.add_field(
            name="rob",
            value="Plan a robbery, and steal money from your friends and enemies!\nParameters: `user`",
            inline=False
        )
        toolembed = discord.Embed(
            title="Help Section/Tools",
            description='View all the available moderation commands here. Separate parameters with commas. Wrap quotations around multi-word parameters (but don\'t put commas afterwards). Our prefix is ".".',
            color=discord.Colour.green()
        )
        toolembed.set_thumbnail(url="https://i.pinimg.com/originals/15/6a/86/156a86c143634a2e444b673a7b373b46.jpg")
        toolembed.add_field(
            name="rng",
            value="Generate a random number!\nParameters: ``lower_limit``, ``upper_limit``",
            inline=False
        )
        toolembed.add_field(
            name="ping",
            value="Pong! Find the latency between the bot and you.\nParameters: none",
            inline=False
        )
        toolembed.add_field(
            name="search",
            value="Search an article on Wikipedia.\nParameters: ``page_name``",
            inline=False
        )
        toolembed.add_field(
            name="define",
            value="Look up a word on the Free Dictionary API!\nParameters: ``word``",
            inline=False
        )
        toolembed.add_field(
            name="poll",
            value="Start a poll!\nParameters: ``poll_name_(or_question_name)``, ``options``"
        )
        toolembed.add_field(
            name="invite",
            value="Invite me, or invite people to this server!\nNote: you must have the permission to create invites.\nParameters: none",
            inline=False
        )
        toolembed.add_field(
            name="revokeinvite",
            value="Revoke an invite.\nNote: you must have the permission to create invites.\nParameters: ``invite_key/invite_link``",
            inline=False
        )
        mathembed = discord.Embed(
            title="Help Section/Mathematics",
            description='View all the available mathematics commands here. Separate parameters with commas. Wrap quotations around multi-word parameters (but don\'t put commas afterwards). Our prefix is ".".',
            color=discord.Color.green()
        )
        mathembed.add_field(
            name="calculate",
            value="Calculate **advanced** equations.\nParameters: `equation`, `solve_for`, `other_parameters_(infinite)`\n**Use `.calculate help` for more information.**",
            inline=False
        )
        modembed = discord.Embed(
            title="Help Section/Moderation",
            description='View all the available moderation commands here. Separate parameters with commas. Wrap quotations around multi-word parameters (but don\'t put commas afterwards). Our prefix is ".".',
            color=discord.Colour.green()
        )
        modembed.set_thumbnail(url="https://i.pinimg.com/originals/15/6a/86/156a86c143634a2e444b673a7b373b46.jpg")
        modembed.add_field(
            name="clear/purge",
            value="Clears a number of messages.\nParameters: ``number``\nExamples: ``.clear 5``, ``.purge 6``",
            inline=False
        )
        modembed.add_field(
            name="timeout",
            value="Timeouts a user.\nParameters: ``user``, ``duration``, ``optional-reason``\nExample: ``.timeout @Airblox 1m Spamming.``",
            inline=False
        )
        modembed.add_field(
            name="untimeout",
            value="Removes a timeout from a user.\nParameters: ``user``, ``optional-reason``\nExample: ``.untimeout @Airblox You're forgiven.``",
            inline=False
        )
        modembed.add_field(
            name="assignrole",
            value="Assigns a role to a user.\n[NOTE: You can only assign roles that are lower than what you have.]\nParameters: ``role``, ``user``\nExample: ``.assignrole Gifted @Airblox``",
            inline=False
        )
        modembed.add_field(
            name="demoterole",
            value="Fires a member from a role.\nParameters: ``role``, ``user``\nExample: ``.demoterole Gifted @Airblox``",
            inline=False
        )
        modembed.add_field(
            name="kick",
            value="Kicks a member from the server (they will still be able to rejoin with a new invite).\nParameters: ``user``, ``reason_(optional)``",
            inline=False
        )
        modembed.add_field(
            name="ban",
            value="Bans a member from the server (they can't rejoin).\nParameters: ``user``, ``delete_messages?_(yes/no/true/false)``, ``reason_(optional)``",
            inline=False
        )
        modembed.add_field(
            name="unban",
            value="Unbans a member from the server.\nParameters: ``user``, ``reason_(optional)``",
            inline=False
        )
        modembed.add_field(
            name="prune",
            value="Prunes members from the server who have been inactive.\nParameters: `duration_(in_days,_default=7)`, `reason_(optional)`, `roles_(optional)`\nExamples: `.prune`, `.prune 7 \"inactive\"`",
            inline=False
        )
        adminembed = discord.Embed(
            title="Help Section/Administration",
            description='View all the available moderation commands here. Separate parameters with commas. Wrap quotations around multi-word parameters (but don\'t put commas afterwards). Our prefix is ".".',
            color=discord.Colour.green()
        )
        adminembed.set_thumbnail(url="https://i.pinimg.com/originals/15/6a/86/156a86c143634a2e444b673a7b373b46.jpg")
        adminembed.add_field(
            name="addrole",
            value="Creates a new role.\nParameters: ``role_name``",
            inline=False
        )
        adminembed.add_field(
            name="delrole",
            value="Deletes a role.\nParameters: ``role_name``",
            inline=False
        )

        if interaction.user != self.ctx.author:
            await interaction.response.send_message("This menu isn't for you!", ephemeral=True)
        else:
            if select.values[0] == "General":
                await interaction.response.edit_message(content=None, embed=embed)
            elif select.values[0] == "Currency - Page 1":
                await interaction.response.edit_message(content=None, embed=currencyembed)
            elif select.values[0] == "Currency - Page 2":
                await interaction.response.edit_message(content=None, embed=currencyembed2)
            elif select.values[0] == "Tools":
                await interaction.response.edit_message(content=None, embed=toolembed)
            elif select.values[0] == "Mathematics":
                await interaction.response.edit_message(content=None, embed=mathembed)
            elif select.values[0] == "Moderation":
                await interaction.response.edit_message(content=None, embed=modembed)
            elif select.values[0] == "Administration":
                await interaction.response.edit_message(content=None, embed=adminembed)


@bot.command()
async def help(ctx):
    view = HelpView(ctx)

    await ctx.send(content="From the select below, select a category!", view=view)


# Moderation
@bot.command(name="assign")
@commands.has_permissions(moderate_members=True)
async def assign_role(ctx, role: discord.Role, user: discord.Member = None):
    await user.add_roles(role)
    await ctx.send(f"Assigned {user.mention} the role of {role}. (Moderator: {ctx.author.mention}.)")


@bot.command(name="demote")
@commands.has_permissions(moderate_members=True)
async def demote_role(ctx, role: discord.Role, user: discord.Member = None):
    await user.remove_roles(role)
    await ctx.send(f"Moderator {ctx.author.mention} has fired {user.mention} from the role of {role}.")


@bot.command()
@commands.has_permissions(moderate_members=True)
async def clear(ctx, arg):
    msg = await ctx.send(f"Purging/clearing {arg} messages...")
    await msg.delete()
    await ctx.channel.purge(limit=(int(arg) + 1))
    successmsg = await ctx.send(f"Successfully purged/cleared {arg} message(s).")
    await successmsg.delete(delay=5)


@bot.command()
@commands.has_permissions(moderate_members=True)
async def purge(ctx, arg):
    await ctx.invoke(clear, arg)


@bot.command()
@commands.has_permissions(moderate_members=True)
async def timeout(ctx, user: discord.Member = None, time=None, *, reason=None):
    time = humanfriendly.parse_timespan(time)
    await user.timeout(until=discord.utils.utcnow() + datetime.timedelta(seconds=time),
                       reason=f"{ctx.author} - {reason}")
    await ctx.send(
        f"{user} has been timed out for {time} seconds by {ctx.author.mention} | \"{reason}\" -{ctx.author}.")


@bot.command()
@commands.has_permissions(moderate_members=True)
async def untimeout(ctx, user: discord.Member = None, *, reason=None):
    await user.timeout(until=None, reason=reason)
    await ctx.send(f"Timeout has been removed from {user.mention} by {ctx.author.mention}. [Reason: {reason}]")


@bot.command()
@commands.has_permissions(moderate_members=True)
async def kick(ctx, user: discord.Member = None, *kick_reason):
    reason = " ".join(kick_reason)
    if user == None:
        await ctx.reply("Specify a user.")
    else:
        await user.kick(reason=reason)
        await ctx.reply(f"Successfully kicked {user.mention}. Reason: ``{ctx.author} - {reason}``")


@bot.command()
@commands.has_permissions(moderate_members=True)
async def ban(ctx, user: discord.Member = None, deletemessages="false", reason=None):
    if user == None:
        await ctx.reply("Specify a user.")
    else:
        if deletemessages == "yes," or deletemessages == "true,":
            await user.ban(delete_message_days=604800, reason=reason)
            await ctx.reply(
                f"Successfully banned {user.mention}, and deleted their messages in the past week. Reason: ``{ctx.author} - {reason}``")
        elif deletemessages == "no," or deletemessages == "false,":
            await user.ban(delete_message_days=0, reason=reason)
            await ctx.reply(
                f"Successfully banned {user.mention} (messages were not cleared). Reason: ``{ctx.author} - {reason}``")


@bot.command()
@commands.has_permissions(moderate_members=True)
async def unban(ctx, user: discord.User = None, reason=None):
    if user is None:
        await ctx.reply("Specify a user.")
    else:
        await ctx.guild.unban(user=user, reason=reason)
        await ctx.reply(f"Successfully unbanned {user.mention} from the server. Reason: ``{ctx.author} - {reason}``")


@bot.command()
@commands.has_permissions(moderate_members=True)
async def prune(ctx, duration=7, reason="None.", *roles):
    guild = ctx.guild

    pruning = await guild.prune_members(days=duration, roles=roles, reason=f"{ctx.author} - reason")
    await ctx.reply(
        f"Pruned {pruning} members who were inactive on this server for more than {duration} days. | Reason: {reason}")


# Server administration
@bot.command()
@commands.has_permissions(administrator=True)
async def addrole(ctx, *role_name):
    rolename = " ".join(role_name)
    addrole_embed = discord.Embed(
        title="New Role",
        description="Select permissions from the select below. When you're ready, press the confirm button.",
        color=discord.Colour.purple()
    )

    addrole_perms_select = Select(
        options=[
            discord.SelectOption(label="View Channels", description="Allows members to view channels by default.",
                                 value="view_channel"),
            discord.SelectOption(label="Manage Channels",
                                 description="Allows members to create, edit or delete channels.",
                                 value="manage_channels"),
            discord.SelectOption(label="Manage Roles", description="Allows members to create/edit/delete new roles.",
                                 value="manage_roles"),
            discord.SelectOption(label="Manage Emojis & Stickers",
                                 description="Allows members to add/remove custom emojis/stickers.",
                                 value="manage_emojis_and_stickers"),
            discord.SelectOption(label="View Audit Log", description="Allows members to view changes in this server.",
                                 value="view_audit_log"),
            discord.SelectOption(label="Manage Webhooks", description="Allows members to create/edit/delete webhooks.",
                                 value="manage_webhooks"),
            discord.SelectOption(label="Manage Server",
                                 description="Allows members to change the server's information.",
                                 value="manage_guild"),
            discord.SelectOption(label="Create Invite",
                                 description="Allows members to invite new people to this server.",
                                 value="create_instant_invite"),
            discord.SelectOption(label="Change Nickname", description="Allows members to change their nickname.",
                                 value="change_nickname"),
            discord.SelectOption(label="Manage Nicknames",
                                 description="Allows members to change the nicknames of others.",
                                 value="manage_nicknames"),
            discord.SelectOption(label="Kick Members", description="Allows members to remove others from this server.",
                                 value="kick_members"),
            discord.SelectOption(label="Ban Members",
                                 description="Allows members to permanently ban others from this server.",
                                 value="ban_members"),
            discord.SelectOption(label="Moderate Member",
                                 description="Allows members to moderate others (e.g. timeout).",
                                 value="moderate_member"),
            discord.SelectOption(label="Send Messages", description="Allows members to text.", value="send_messages"),
            discord.SelectOption(label="Send Messages in Threads", description="Allows members to text in threads.",
                                 value="send_messages_in_threads"),
            discord.SelectOption(label="Create Public Threads", description="Allows members to create public threads.",
                                 value="create_public_threads"),
            discord.SelectOption(label="Create Private Threads",
                                 description="Allows members to create invite-only threads.",
                                 value="create_private_threads"),
            discord.SelectOption(label="Embed Links", description="Allows members to share embedded content.",
                                 value="embed_links"),
            discord.SelectOption(label="Attach Files",
                                 description="Allows members to attach media and files in channels.",
                                 value="attach_files"),
            discord.SelectOption(label="Add Reactions",
                                 description="Allows members to add emoji reactions to messages.",
                                 value="add_reactions"),
            discord.SelectOption(label="Mention @everyone, @here and All Roles",
                                 description="Allows members to use these pings.", value="mention_everyone"),
            discord.SelectOption(label="Manage Messages", description="Allows memberes to delete and pin messages.",
                                 value="manage_messages"),
            discord.SelectOption(label="Manage Threads", description="Allows members to moderate threads.",
                                 value="manage_threads"),
            discord.SelectOption(label="Read Message History",
                                 description="Allows members to read previously-sent messages.",
                                 value="read_message_history"),
            discord.SelectOption(label="Use Application Commands", description="Allows members to use bot commands.",
                                 value="use_slash_commands")
        ],
        row=0,
        placeholder="Select permissions...",
        min_values=0,
        max_values=25
    )
    addrole_perms_adv_select = Select(
        options=[
            discord.SelectOption(label="Administrator",
                                 description="Members will have all permissions and bypass everything.",
                                 value="administrator"),
            discord.SelectOption(label="Send Text-to-speech Messages",
                                 description="Allows members to use /tts messages.", value="send_tts_messages"),
            discord.SelectOption(label="[NITRO] Use External Emojis",
                                 description="Allows members to use emojis from other servers.",
                                 value="use_external_emojis"),
            discord.SelectOption(label="[NITRO] Use External Stickers",
                                 description="Allows members to use stickers from other servers.",
                                 value="use_external_stickers"),
            discord.SelectOption(label="[VOICE] Connect", description="Allows members to connect to voice channels.",
                                 value="connect"),
            discord.SelectOption(label="[VOICE] Speak", description="Allows members to talk in voice channels.",
                                 value="speak"),
            discord.SelectOption(label="[VOICE] Video", description="Allows members to share their video.",
                                 value="stream"),
            discord.SelectOption(label="[VOICE] Use Activities", description="Allows members to use activities.",
                                 value="start_embedded_activities"),
            discord.SelectOption(label="[VOICE] Use Voice Activity",
                                 description="Allows members to speak by just talking.", value="use_voice_activation"),
            discord.SelectOption(label="[VOICE] Priority Speaker",
                                 description="Allows members to be more easily heard.", value="priority_speaker"),
            discord.SelectOption(label="[VOICE] Mute Members", description="Allows members to mute others.",
                                 value="mute_members"),
            discord.SelectOption(label="[VOICE] Deafen Members", description="Allows members to deafen others.",
                                 value="deafen_members"),
            discord.SelectOption(label="[VOICE] Move Members",
                                 description="Allows members to move others to another voice channel.",
                                 value="move_members"),
            discord.SelectOption(label="[EVENTS] Manage Events",
                                 description="Allows members to create/edit/cancel events.", value="manage_events")],
        row=1,
        placeholder="Advanced permissions...",
        min_values=0,
        max_values=14
    )

    async def addrole_select_callback(interaction):
        if interaction.user != ctx.author:
            await interaction.response.send_message("This select menu isn't for you!", ephemeral=True)

    async def addrole_select_adv_callback(interaction):
        if interaction.user != ctx.author:
            await interaction.response.send_message("This select menu isn't for you!", ephemeral=True)

    addrole_perms_select.callback = addrole_select_callback
    addrole_perms_adv_select.callback = addrole_select_adv_callback

    addrole_confirm_button = Button(label="Confirm", style=discord.ButtonStyle.primary, row=3)
    addrole_cancel_button = Button(label="Cancel", style=discord.ButtonStyle.danger, row=3)

    async def addrole_confirm_button_callback(interaction):

        if interaction.user != ctx.message.author:
            await interaction.response.send_message("This button isn't for you!", ephemeral=True)
        else:
            addrole_dict = {i: True for i in addrole_perms_select.values + addrole_perms_adv_select.values}
            if len(addrole_dict) == 0:
                await ctx.guild.create_role(name=rolename)
                rolecreation_success_embed_empty = discord.Embed(
                    title="Role Creation - Success",
                    color=discord.Colour.green(),
                    description=f"Role Name: {rolename}\nAuthor: {ctx.message.author.mention}"
                )
                rolecreation_success_embed_empty.add_field(
                    name="Permissions",
                    value="None."
                )
                await interaction.response.edit_message(content=None, view=None, embed=rolecreation_success_embed_empty)
            else:
                newrole = await ctx.guild.create_role(name=rolename)
                newrole_editperms = discord.Permissions()
                newrole_editperms.update(**addrole_dict)
                await newrole.edit(permissions=newrole_editperms)

                addrole_permsstring = ["\n".join([str(item) for item in addrole_perms_select.values])]
                addrole_permsstring_adv = ["\n".join([str(item2) for item2 in addrole_perms_adv_select.values])]
                addrole_permsstringlist = addrole_permsstring + addrole_permsstring_adv
                addrole_permsstr = "\n".join([str(item4) for item4 in addrole_permsstringlist])

                addrole_success_embed = discord.Embed(
                    title="Role Creation - Success",
                    description=f"Role Name: {rolename}\nAuthor: {ctx.author.mention}",
                    color=discord.Colour.green()
                )
                addrole_success_embed.add_field(
                    name="Permissions",
                    value=f"{addrole_permsstr}"
                )

                await interaction.response.edit_message(content=None, embed=addrole_success_embed, view=None)

    async def addrole_cancel_button_callback(interaction):
        if interaction.user == ctx.author:
            await interaction.response.edit_message(content=f"Role creation cancelled.", embed=None, view=None)
        else:
            pass

    addrole_confirm_button.callback = addrole_confirm_button_callback
    addrole_cancel_button.callback = addrole_cancel_button_callback

    addrole_view = View()
    addrole_view.disable_on_timeout = True
    addrole_view.add_item(addrole_perms_select)
    addrole_view.add_item(addrole_perms_adv_select)
    addrole_view.add_item(addrole_confirm_button)
    addrole_view.add_item(addrole_cancel_button)

    await ctx.send(embed=addrole_embed, view=addrole_view)


@bot.command(name="deleterole")
@commands.has_permissions(administrator=True)
async def delrole(ctx, *args):
    arg = " ".join(args)
    role = discord.utils.get(ctx.message.guild.roles, name=arg)

    delrole_embed = discord.Embed(
        title="Role Deletion",
        description=f"{ctx.author.mention}, are you sure you want to delete the role {arg}? It cannot be undone!",
        color=discord.Colour.red()
    )
    delrole_confirm = Button(label="Confirm", style=discord.ButtonStyle.danger)
    delrole_cancel = Button(label="Cancel", style=discord.ButtonStyle.blurple)

    delrole_view = View()
    delrole_view.disable_on_timeout = True
    delrole_view.add_item(delrole_confirm)
    delrole_view.add_item(delrole_cancel)

    async def delrole_confirm_callback(interaction):
        if interaction.user == ctx.author:
            try:
                await role.delete()
            except AttributeError:
                await interaction.response.edit_message(content="Role doesn't exist.", embed=None, view=None)
            else:
                delrole_embed = discord.Embed(
                    title="Role Deletion",
                    description=f"Role has been deleted. (Author: {ctx.author.mention})",
                    color=discord.Colour.lighter_grey()
                )
                await interaction.response.edit_message(content=None, embed=delrole_embed, view=None)
        else:
            await interaction.response.send_message(content="This button is not for you!", ephemeral=True)

    async def delrole_cancel_callback(interaction):
        if interaction.user == ctx.author:
            await interaction.response.edit_message(content="Role deletion canceled.", embed=None, view=None)
        else:
            await interaction.response.send_message(content="This button is not for you!", ephemeral=True)

    delrole_confirm.callback = delrole_confirm_callback
    delrole_cancel.callback = delrole_cancel_callback

    await ctx.send(content=None, embed=delrole_embed, view=delrole_view)


@bot.command(name="invite")
@commands.has_permissions(create_instant_invite=True)
async def invite(ctx):
    original = await ctx.reply("Creating invite...")
    invite_link_invite = await ctx.channel.create_invite()
    invite_link = str(invite_link_invite)
    show_button = Button(label="Show URL", style=discord.ButtonStyle.blurple)

    async def show_button_callback(interaction):
        if interaction.user == ctx.author:
            await interaction.response.send_message(f"{invite_link}", ephemeral=True)
        else:
            await interaction.response.send_message("This button is not for you!", ephemeral=True)

    show_button.callback = show_button_callback
    revoke_invite = Button(label="Revoke Invite", style=discord.ButtonStyle.danger)

    async def revoke_invite_callback(interaction):
        if interaction.user == ctx.author:
            await invite_link_invite.delete()
            await interaction.response.edit_message(
                content="*Invite revoked. If you still see the same URL and it's valid, ignore it; it won't work.*",
                view=None)
        else:
            await interaction.response.send_message("This button is not for you!", ephemeral=True)

    revoke_invite.callback = revoke_invite_callback
    invite_view = View()
    invite_view.disable_on_timeout = True
    invite_view.add_item(show_button)
    invite_view.add_item(revoke_invite)
    await original.edit("Click the button to show the link!", view=invite_view)


@bot.command(name="revokeinv")
@commands.has_permissions(ban_members=True)
async def revokeinvite(ctx, arg, reason="None."):
    arg1 = arg.replace("https://discord.gg/", "")
    delete_invite = await bot.fetch_invite(url=f"https://discord.gg/{arg1}", with_counts=False, with_expiration=False)
    await delete_invite.delete(reason=reason)
    await ctx.reply(f"Invite \"{arg1}\" has been revoked.")


# Tools
@bot.command()
async def ping(ctx):
    pingembed = discord.Embed(
        title="Pong!",
        description=f"Latency: {round(bot.latency * 1000)} ms.",
        color=discord.Colour.green()
    )
    await ctx.reply(embed=pingembed)

@bot.command(name="wiki")
async def wikipedia(ctx, *args):
    search_keyword = " ".join(args)
    search_wait = await ctx.reply(f"*Searching \"{search_keyword}\" on Wikipedia...*")
    try:
        search_embed = discord.Embed(
            title=f"Wikipedia Search - \"{search_keyword}\"",
            description=wikisummary(search_keyword)[0],
            color=discord.Colour.lighter_grey())
        search_url_link = wikisummary(search_keyword)[1]
        search_url_button = Button(label=f"Read more about {wikisummary(search_keyword)[2]} on Wikipedia",
                                   url=f"{search_url_link}")
        search_view = View()
        search_view.disable_on_timeout = True
        search_view.add_item(search_url_button)
        await search_wait.edit(content=None, embed=search_embed, view=search_view)
    except PageError:
        await search_wait.edit(content=f"No results for \"{search_keyword}\".")
    except DisambiguationError as disamb_e:
        await search_wait.edit(f"**Disambiguation:** {disamb_e}")

@bot.command()
async def define(ctx, *args):
    arg = " ".join(args)
    async with ctx.typing():
        result2 = await dictsearch(arg)
        result = ast.literal_eval(result2)

        try:
            word = result[0]["word"]
        except Exception:
            word = arg
        try:
            phonetic = result[0]["phonetic"]
        except Exception:
            phonetic = "None found."
        try:
            link = result[0]["sourceUrls"][0]
        except Exception:
            link = None

        try:
            meaning = {}
            for i in range(len(result[0]["meanings"])):
                meaning.update({str(result[0]["meanings"][i]["partOfSpeech"]): [j['definition'] for j in
                                                                                result[0]["meanings"][i][
                                                                                    "definitions"]]})
        except Exception:
            meaning.update({"Meanings": "None found."})

        embed = discord.Embed(title=f"{word}", description=f"Phonetic: {phonetic}", color=discord.Color.blurple())
        embed.set_footer(text="Provided through the Free Dictionary API.")

        nl = "\n- "

        for i in meaning:
            if i != "Meanings":
                embed.add_field(name=f"{i.capitalize()}", value=f"- {nl.join(meaning[i])}", inline=False)
            else:
                embed.add_field(name="Meanings", value="None found.")

        if link is not None:
            button = Button(label="Read more...", url=link, style=discord.ButtonStyle.url)
        elif link is None:
            button = Button(label="No source URLs found.", style=discord.ButtonStyle.secondary)

            async def buttoncall(interaction):
                await interaction.response.defer()

            button.callback = buttoncall
        view = View()
        view.disable_on_timeout = True
        view.add_item(button)

        await ctx.reply(content=None, embed=embed, view=view)

@bot.command()
async def poll(ctx, name, *args):
    name = name.replace(",", "")
    args_list = []
    current_arg = ""
    for z in args:
        if z.endswith(","):
            current_arg = current_arg + " " + z[:-1]
            args_list.append(current_arg)
            current_arg = ""
        else:
            current_arg = current_arg + " " + z
    args_list.append(current_arg)
    castedvotes = {}
    poll_provided = []
    args_loop = 1
    poll_embed = discord.Embed(title=f"POLL: \"{name}\"",
                               description=f"@here, {ctx.author.mention} is starting a poll!\n\nSelect your option and vote! You  may change your choice anytime until the time's up.",
                               color=discord.Colour.green())
    for i in args_list:
        poll_provided.append(discord.SelectOption(label=i))
        args_loop += 1

    poll_vote = Button(label="Vote!", style=discord.ButtonStyle.blurple, row=1)
    poll_end = Button(label="End poll", style=discord.ButtonStyle.secondary, row=1)
    poll_options = Select(
        options=poll_provided,
        row=0
    )

    async def poll_select_callback(interaction):
        await interaction.response.defer()

    async def poll_vote_callback(interaction):
        castedvotes[f"{interaction.user.id}"] = poll_options.values[0]
        await interaction.response.send_message("Vote updated!", ephemeral=True)

    async def poll_end_callback(interaction):
        if interaction.user == ctx.author:
            option_list = list(args_list)
            count_list = castedvotes.values()
            counted_dict = Counter(count_list)
            prepared_poll = ""
            try:
                winning = str(max(counted_dict))
            except ValueError:
                winning = "None."
                prepared_poll = "No votes."
            tie = len(set(counted_dict.values()))

            if tie == 1:
                if len(counted_dict) > 1:
                    winning = "Tie!"

            j_count = 0
            counted_dict_copy = copy.copy(counted_dict)

            for j in counted_dict_copy.keys():
                counted_dict[str(j)] = counted_dict[option_list[j_count]]
                del counted_dict[str(j)]
                j_count += 1

            if prepared_poll != "No votes.":
                prepared_poll = str(counted_dict_copy).replace('Counter(', '').replace(')', '').replace('{',
                                                                                                        '').replace('}',
                                                                                                                    '').replace(
                    '\'', '')

            poll_embed = discord.Embed(
                title=f"POLL: \"{name}\" - Results",
                description=f"**Winning Vote: {winning}\n**{prepared_poll}",
                color=discord.Colour.green()
            )
            await interaction.response.edit_message(content=None, view=None, embed=poll_embed)
        elif interaction.user != ctx.author:
            await interaction.response.send_message("This poll isn't created by you!", ephemeral=True)

    poll_options.callback = poll_select_callback
    poll_vote.callback = poll_vote_callback
    poll_end.callback = poll_end_callback

    poll_view = View(timeout=None)
    poll_view.add_item(poll_vote)
    poll_view.add_item(poll_options)
    poll_view.add_item(poll_end)

    await ctx.reply(content=None, embed=poll_embed, view=poll_view)

@bot.command(name="8ball")
async def _8ball(ctx, *args):
    if len(args) != 0:
        possibleanswers = ["It is certain.",  # positive
                           "It is decidely so.",
                           "Without a doubt.",
                           "Yes definitely.",
                           "You may rely on it.",
                           "As I see it, yes.",
                           "Most likely.",
                           "Outlook good.",
                           "Yes.",
                           "Signs point to yes.",
                           "Reply hazy, try again.",  # vague
                           "Ask again later.",
                           "Better not tell you now.",
                           "Cannot predict now.",
                           "Concentrate and ask again.",
                           "Don't count on it.",  # negative
                           "My reply is no.",
                           "My sources say no.",
                           "Outlook not so good.",
                           "Very doubtful."]

        await ctx.reply(random.choice(possibleanswers))
    else:
        raise Exception("arg is a required argument that is missing.")

@bot.command(name="random")
async def _random(ctx, *numbers):
    numbers = [int(i.replace(" ", "")) for i in " ".join(numbers).split(",")]
    embed = discord.Embed(title="CRIME.NET/Random Number Generator", colour=discord.Colour.blurple())
    embed.add_field(name="Result", value="{:,}".format(random.randint(*numbers)), inline=False)
    embed.set_footer(text=f"Lower limit: {'{:,}'.format(numbers[0])}; Upper limit: {'{:,}'.format(numbers[1])}\nProcessing ID: {baintools.generate_transaction_id(10)}")
    await ctx.reply(content=None, embed=embed)

# Trolling
@bot.command()
async def nitro(ctx):
    nitroembed = discord.Embed(
        description=f"**{ctx.author.mention} generated a Nitro link!**",
        color=discord.Colour.nitro_pink()
    )
    nitroembed.set_image(
        url="https://media.discordapp.net/attachments/886639021772648469/903535585992523796/unknown.png")

    claimbutton = discord.ui.Button(label="Claim", style=discord.ButtonStyle.green)

    async def nitro_callback(interaction):
        nitroembed = discord.Embed(
            description=f"**{interaction.user.mention} claimed the Nitro!**",
            color=discord.Colour.red()
        )
        nitroembed.set_image(
            url="https://media.discordapp.net/attachments/886639021772648469/903535585992523796/unknown.png")

        claimbutton = discord.ui.Button(label="Claimed", style=discord.ButtonStyle.danger, disabled=True)

        newnitroview = View()
        newnitroview.disable_on_timeout = True
        newnitroview.add_item(claimbutton)
        await interaction.response.edit_message(content=None, embed=nitroembed, view=newnitroview)
        await interaction.followup.send(content="https://imgur.com/NQinKJB", ephemeral=True)

    claimbutton.callback = nitro_callback

    view = View()
    view.disable_on_timeout = True
    view.add_item(claimbutton)

    await ctx.send(embed=nitroembed, view=view)


@bot.command(name="tryitandsee")
async def _tryitandsee(ctx, user: discord.Member = None):
    if user is None:
        user = ctx.author
    try:
        await ctx.message.reference.cached_message.reply(content=f"From {ctx.author},\nhttps://tryitands.ee")
    except Exception:
        await ctx.reply(content=f"{user.mention}, from {ctx.author},\nhttps://tryitands.ee")
    finally:
        await ctx.message.delete()


@bot.command()
async def kill(ctx, arg: discord.Member):
    if arg == "me":
        await ctx.send(f"You've committed suicide. Welcome to The Bad Place.")
    elif arg == "Bain" or arg == "bain" or arg == secrets["bain_id"]:
        await ctx.send(
            f"You're the dentist. How dare you. I'll get Locke to rescue me, and you'll wait for my revenge!")
    else:
        quotenumber = random.randint(1, 12)
        if quotenumber == 1:
            quotenumber = "a pair of electrical brass knuckles. Get a tazed of your own medicine!"
        elif quotenumber == 3:
            quotenumber = "a silent OVE9000 saw. Man it would be better if they used the saw to open deposit boxes instead. What a waste of ammo."
        elif quotenumber == 4:
            quotenumber = "two STRYk 18c pistols. Oof!"
        elif quotenumber == 6:
            quotenumber = "an AMCAR rifle, an AK rifle, a CAR-4 rifle, an UAR, an AK .762, a JP36, a... God forbid... a forking GALANT? I mean seriously, you don't need to get so many guns to kill this guy."
        elif quotenumber == 7:
            quotenumber = "Razormind music. Credits to Simon Viklund. But for now, give them hell... (*police assault starts*)"
        elif quotenumber == 8:
            quotenumber = f"an FN Five-seveN pistol, loaded with a magazine filled with 19 AP rounds, as well as one extra cartridge in the chamber. {arg} was wearing Kevlar, but it had no use."
        elif quotenumber == 9:
            quotenumber = f"oh my- what the hEll, ice? {ctx.author.mention} killed him with intracellular ice. *Shivers...*"
        elif quotenumber == 10:
            quotenumber = f"oh wait, {ctx.author.mention} couldn't kill him. John Wick killed him with the Contractor .308 Sniper Rifle instead. A revolver-holding cop saw {ctx.author.mention} drawing out his weapon so he arrested him. *Presses F to pay respects...*"
        elif quotenumber == 11:
            quotenumber = f"a pair of boxing gloves, lol. Completely overkill."
        elif quotenumber == 12:
            quotenumber = f"a cup of lemon tea. {arg} was allergic to lemon tea (yes, what the heck, man)!"

        if quotenumber == 2 or quotenumber == 5:
            await ctx.send(
                f"{ctx.message.author.mention} tried to kill {arg}, but got arrested by the FBI for concealed "
                f"carry. You're probably gonna be the next Hoxton, who'll need to be broken out by "
                f"blasting C4 in the wall, going through a parking lot, and going to the FBI Headquarters "
                f"and go under a full-style SWAT, FBI, and DHS assault just to find out who ratted you "
                f"out!")
        else:
            await ctx.send(f"<:glock_17:966176633398644757> {ctx.message.author.mention} killed {arg} with {quotenumber}")


@bot.command()
async def hack(ctx, user: discord.Member):
    hack_lobby = discord.Embed(
        title="Welcome to CRIME.NET",
        description="Welcome to crime.net. My name is Bain, and I'll be guiding you throughout your hack. I'm a "
                    "professional hacker who has served the PAYDAY gang for over 15 years. Choose a type of hack, "
                    "and we'll continue. ",
        color=discord.Colour.blurple()
    )
    hack_bank = Button(label="Bank Account hack", style=discord.ButtonStyle.blurple)
    hack_id = Button(label="Identity hack", style=discord.ButtonStyle.blurple)
    hack_pc = Button(label="Computer hack", style=discord.ButtonStyle.blurple)

    async def hack_bank_callback(interaction):
        if interaction.user == ctx.author and user.mention != secrets["owner_id"] and user.mention != secrets["bain_id"]:
            bank_embed = discord.Embed(
                title="Bank Hack",
                description=f"Bain: ``Starting hack...``",
                color=discord.Colour.blurple()
            )
            await interaction.response.edit_message(content=None, embed=bank_embed, view=None)
            await asyncio.sleep(1)
            bank_embed = discord.Embed(
                title="Bank Hack",
                description=f"Bain: ``Accessing bank account information...``",
                color=discord.Colour.blurple()
            )
            await interaction.edit_original_message(content=None, attachments=[], embed=bank_embed, view=None)
            await asyncio.sleep(2.5)
            bank_embed = discord.Embed(
                title="Bank Hack",
                description=f"Bain: ``Found credentials. Finding balance and phone number...``",
                color=discord.Colour.blurple()
            )
            password = f"``{''.join(random.choices(string.ascii_uppercase + string.digits, k=12))}``"
            bank_embed.add_field(name="Account information",
                                 value=f"Username: {str(user).replace('#', '')}\nPassword: {password}")
            await interaction.edit_original_message(content=None, attachments=[], embed=bank_embed, view=None)
            await asyncio.sleep(2)
            balance = "{:,}".format(random.randint(-1000, 100000))
            phone = f"+1 {random.randint(0, 999):03} {random.randint(0, 999):03} {random.randint(0, 9999):04}"
            bank_embed = discord.Embed(
                title="Bank Hack",
                description=f"Bain: ``Found information. Now blackmailing {user}...``",
                color=discord.Colour.blurple()
            )
            bank_embed.add_field(name="Account information",
                                 value=f"Username: {str(user).replace('#', '')}\nPassword: {password}\nBalance: ${balance}\nPhone number: {phone}")
            await interaction.edit_original_message(content=None, attachments=[], embed=bank_embed, view=None)
            await asyncio.sleep(2)
            bank_embed = discord.Embed(
                title="Bank Hack",
                description=f"Bain: (Talking to {user}) ``Hello, this is First World Bank. Seems like your account has been compromised. Please log into your account immediately and change your password.``\n(Talking to {ctx.author.mention}) ``Injecting Trojan horse...``",
                color=discord.Colour.blurple()
            )
            bank_embed.add_field(name="Account information",
                                 value=f"Username: {str(user).replace('#', '')}\nPassword: {password}\nBalance: ${balance}\nPhone number: {phone}")
            await interaction.edit_original_message(content=None, attachments=[], embed=bank_embed, view=None)
            await asyncio.sleep(7.5)
            bank_embed = discord.Embed(
                title="Bank Hack",
                description=f"{user}: ``That is bad! I don't know how to do that... guide me please.``\n(Talking to {ctx.author.mention}) ``I'm doing some mischief from here, hang on...``",
                color=discord.Colour.blurple()
            )
            bank_embed.add_field(name="Account information",
                                 value=f"Username: {str(user).replace('#', '')}\nPassword: {password}\nBalance: ${balance}\nPhone number: {phone}")
            await interaction.edit_original_message(content=None, attachments=[], embed=bank_embed, view=None)
            await asyncio.sleep(5)
            bank_embed = discord.Embed(
                title="Bank Hack",
                description=f"Bain: (Talking to {user}) ``Alright. Log into your account and go to the settings page, then enter the PIN.``\n(Talking to {ctx.author.mention}) ``Waiting for the PIN... After that we can disable 2FA.``",
                color=discord.Colour.blurple()
            )
            bank_embed.add_field(name="Account information",
                                 value=f"Username: {str(user).replace('#', '')}\nPassword: {password}\nBalance: ${balance}\nPhone number: {phone}\nAccount Settings PIN: ``Searching...``")
            await interaction.edit_original_message(content=None, attachments=[], embed=bank_embed, view=None)
            await asyncio.sleep(6)
            bank_embed = discord.Embed(
                title="Bank Hack",
                description=f"{user}: ``Done. Now?``\n(Talking to {ctx.author.mention}) ``Got the PIN! Hang on, I'm disabling 2FA...``",
                color=discord.Colour.blurple()
            )
            acc_pin = f"``{random.randint(0, 9999):04}``"
            bank_embed.add_field(name="Account information",
                                 value=f"Username: {str(user).replace('#', '')}\nPassword: {password}\nBalance: ${balance}\nPhone number: {phone}\nAccount Settings PIN: {acc_pin}")
            await interaction.edit_original_message(content=None, attachments=[], embed=bank_embed, view=None)
            await asyncio.sleep(6)
            bank_embed = discord.Embed(
                title="Bank Hack",
                description=f"Bain: (Talking to {user}) ``Alright. Now we'll do the work for you. Have a nice day. [Hangs up]``\n(Talking to {ctx.author.mention}) ``Got it! 2FA bypassed.``",
                color=discord.Colour.blurple()
            )
            bank_embed.add_field(name="Account information",
                                 value=f"Username: {str(user).replace('#', '')}\nPassword: {password}\nBalance: ${balance}\nPhone number: {phone}\nAccount Settings PIN: {acc_pin}")
            await interaction.edit_original_message(content=None, attachments=[], embed=bank_embed, view=None)
            await asyncio.sleep(6.5)
            bank_embed = discord.Embed(
                title="Bank Hack",
                description=f"Bain: ``Fetching information...``",
                color=discord.Colour.blurple()
            )
            bank_embed.add_field(name="Account information",
                                 value=f"Username: {str(user).replace('#', '')}\nPassword: {password}\nBalance: ${balance}\nPhone number: {phone}\nAccount Settings PIN: {acc_pin}")
            await interaction.edit_original_message(content=None, attachments=[], embed=bank_embed, view=None)
            await asyncio.sleep(3)
            bank_embed = discord.Embed(
                title="Bank Hack",
                description=f"Bain: ``Wow. H-how interesting... Now let's get some cash from this person...``",
                color=discord.Colour.blurple()
            )
            age = random.randint(12, 40)
            birthdate = str(int(date.today().year) - age) + "/" + str(random.randint(1, 12)) + "/" + str(
                int(random.randint(1, 30)))
            gender = random.choice(
                ['Male', 'Female', 'Male', 'Female', 'Male', 'Female', 'Male', 'Female', 'Male', 'Female', 'Male',
                 'Female', 'Queering'])
            name = names.get_full_name(gender=gender)
            job = randomjob.print_job_title()
            bank_embed.add_field(name="Account information",
                                 value=f"Username: {str(user).replace('#', '')}\nPassword: {password}\nBalance: ${balance}\nPhone number: {phone}\nAccount Settings PIN: {acc_pin}",
                                 inline=False)
            bank_embed.add_field(name="Personal Information",
                                 value=f"Real Name: {name}\nGender: {gender}\nJob: {job}\nAge: {str(age)}\nBirth: {birthdate}",
                                 inline=False)
            await interaction.edit_original_message(content=None, attachments=[], embed=bank_embed, view=None)
            await asyncio.sleep(4)
            bank_embed = discord.Embed(
                title="Bank Hack",
                description=f"Bain: ``Withdrawing money...``",
                color=discord.Colour.blurple()
            )
            bank_embed.add_field(name="Account information",
                                 value=f"Username: {str(user).replace('#', '')}\nPassword: {password}\nBalance: ${str(balance)}\nPhone number: {phone}\nAccount Settings PIN: {acc_pin}",
                                 inline=False)
            bank_embed.add_field(name="Personal Information",
                                 value=f"Real Name: {name}\nGender: {gender}\nJob: {job}\nAge: {str(age)}\nBirth: {birthdate}",
                                 inline=False)
            await interaction.edit_original_message(content=None, attachments=[], embed=bank_embed, view=None)
            await asyncio.sleep(2.5)
            bank_embed = discord.Embed(
                title="Bank Hack",
                description=f"Bain: ``Done. The hack is complete.``",
                color=discord.Colour.blurple()
            )
            bank_embed.add_field(name="Account information",
                                 value=f"Username: {str(user).replace('#', '')}\nPassword: {password}\nBalance: $0\nPhone number: {phone}\nAccount Settings PIN: {acc_pin}",
                                 inline=False)
            bank_embed.add_field(name="Personal Information",
                                 value=f"Real Name: {name}\nGender: {gender}\nJob: {job}\nAge: {str(age)}\nBirth: {birthdate}",
                                 inline=False)
            bank_acc_id = f"{random.randint(100000, 999999):04}"
            bank_embed.set_footer(text=f"Money has been transferred to {ctx.author} (ID: {bank_acc_id}).")
            await interaction.edit_original_message(content=None, attachments=[], embed=bank_embed, view=None)
        elif interaction.user == ctx.author and user.mention == secrets["owner_id"]:
            await interaction.response.edit_message(content="``Couldn't hack him. Perhaps try someone else?``",
                                                    embed=None, view=None)
        elif interaction.user == ctx.author and user.mention == secrets["bain_id"]:
            await interaction.response.edit_message(content="``Couldn't hack him. Perhaps try someone else?``",
                                                    embed=None, view=None)
        elif interaction.user != ctx.author:
            await interaction.response.send_message("This hack isn't for you!", ephemeral=True)

    async def hack_id_callback(interaction):
        if interaction.user == ctx.author and user.mention != secrets["owner_id"] and user.mention != secrets["bain_id"]:
            id_embed = discord.Embed(title="Identity Hack",
                                     description=f"Bain: ``Starting hack...``",
                                     color=discord.Color.blurple())
            await interaction.response.edit_message(content=None, embed=id_embed, view=None)
            await asyncio.sleep(1)
            id_embed = discord.Embed(title="Identity Hack",
                                     description=f"Bain: ``Infiltrating government records...``",
                                     color=discord.Color.blurple())
            await interaction.edit_original_message(content=None, embed=id_embed, view=None)
            await asyncio.sleep(1)
            gender = random.choice(
                ['Male', 'Female', 'Male', 'Female', 'Male', 'Female', 'Male', 'Female', 'Male', 'Female', 'Male',
                 'Female', 'Queering'])
            name = names.get_full_name(gender=gender)
            age = random.randint(12, 40)
            birthdate = str(int(date.today().year) - age) + "/" + str(random.randint(1, 12)) + "/" + str(
                int(random.randint(1, 30)))
            id_embed = discord.Embed(title="Identity Hack",
                                     description=f"Bain: ``Found his file! Attempting to edit...``",
                                     color=discord.Color.blurple())
            id_embed.add_field(name="Profile",
                               value=f"Name: {name}\nGender: {gender}\nBirth: {birthdate}\nAge: {str(age)}")
            await interaction.edit_original_message(content=None, embed=id_embed, view=None)
            await asyncio.sleep(3)
            id_embed = discord.Embed(title="Identity Hack",
                                     description=f"Bain: ``Ugh. Firewalls are tripped... DANG IT! They are sending "
                                                 f"agents to check out what's happening... I'm fixing it, "
                                                 f"hang on...``",
                                     color=discord.Color.red())
            id_embed.add_field(name="Profile",
                               value=f"Name: {name}\nGender: {gender}\nBirth: {birthdate}\nAge: {str(age)}")
            await interaction.edit_original_message(content=None, embed=id_embed, view=None)
            await asyncio.sleep(6.5)
            id_embed = discord.Embed(title="Identity Hack",
                                     description=f"Agents: ``Hello. Is there anything wrong with {user}'s file?``",
                                     color=discord.Color.red())
            id_embed.add_field(name="Profile",
                               value=f"Name: {name}\nGender: {gender}\nBirth: {birthdate}\nAge: {str(age)}")
            await interaction.edit_original_message(content=None, embed=id_embed, view=None)
            await asyncio.sleep(4)
            id_embed = discord.Embed(title="Identity Hack",
                                     description=f"Bain: [talking to agents] ``Yeah. They just changed their name, so I'm updating their file.``",
                                     color=discord.Color.red())
            id_embed.add_field(name="Profile",
                               value=f"Name: {name}\nGender: {gender}\nBirth: {birthdate}\nAge: {str(age)}")
            await interaction.edit_original_message(content=None, embed=id_embed, view=None)
            await asyncio.sleep(3)
            id_embed = discord.Embed(title="Identity Hack",
                                     description=f"Agents: ``Alright then, sorry for calling. Have a good day. [Hangs up]``",
                                     color=discord.Color.red())
            id_embed.add_field(name="Profile",
                               value=f"Name: {name}\nGender: {gender}\nBirth: {birthdate}\nAge: {str(age)}")
            await interaction.edit_original_message(content=None, embed=id_embed, view=None)
            await asyncio.sleep(3)
            id_embed = discord.Embed(title="Identity Hack",
                                     description=f"Bain: ``Phew. Carrying on with the hack, let me initiate the timelock...``",
                                     color=discord.Color.blurple())
            id_embed.add_field(name="Profile",
                               value=f"Name: {name}\nGender: {gender}\nBirth: {birthdate}\nAge: {str(age)}")
            await interaction.edit_original_message(content=None, embed=id_embed, view=None)
            await asyncio.sleep(3)
            timelock = 14
            for x in range(15):
                id_embed = discord.Embed(title="Identity Hack",
                                         description=f"Bain: ``Waiting for the timelock to end... Then we can edit it.``",
                                         color=discord.Color.green())
                id_embed.add_field(name="Timelocks active", value=f"Profile Edit: ``{str(timelock)}/15``", inline=False)
                id_embed.add_field(name="Profile",
                                   value=f"Name: {name}\nGender: {gender}\nBirth: {birthdate}\nAge: {str(age)}")
                await interaction.edit_original_message(content=None, embed=id_embed, view=None)
                await asyncio.sleep(1)
                timelock -= 1
            id_embed = discord.Embed(title="Identity Hack",
                                     description=f"Bain: ``Timelock done! Let me see... Give me a few seconds.``",
                                     color=discord.Color.blurple())
            id_embed.add_field(name="Timelocks active", value=f"Profile Edit: ``Finished``", inline=False)
            id_embed.add_field(name="Profile",
                               value=f"Name: {name}\nGender: {gender}\nBirth: {birthdate}\nAge: {str(age)}")
            await interaction.edit_original_message(content=None, embed=id_embed, view=None)
            await asyncio.sleep(1)
            id_embed = discord.Embed(title="Identity Hack",
                                     description=f"Bain: ``Timelock done! Let me see... Give me a few seconds.``",
                                     color=discord.Color.blurple())
            id_embed.add_field(name="Profile",
                               value=f"Name: {name}\nGender: {gender}\nBirth: {birthdate}\nAge: {str(age)}")
            await interaction.edit_original_message(content=None, embed=id_embed, view=None)
            await asyncio.sleep(2)
            newname = []
            newname_list = coolname.generate(pattern=2)
            for y in newname_list:
                newname.append(y.capitalize())

            newname = str(" ".join(newname))
            id_embed = discord.Embed(title="Identity Hack",
                                     description=f"Bain: ``Alright, let's change his name. Haha! {newname}... How silly...``",
                                     color=discord.Color.blurple())
            id_embed.add_field(name="Profile",
                               value=f"Name: {newname}\nGender: {gender}\nBirth: {birthdate}\nAge: {str(age)}")
            await interaction.edit_original_message(content=None, embed=id_embed, view=None)
            await asyncio.sleep(2.5)
            newage = random.choice([random.randint(0, 5), random.randint(90, 115)])
            birthdate = str(int(date.today().year) - int(newage)) + "/" + str(random.randint(1, 12)) + "/" + str(
                int(random.randint(1, 30)))
            id_embed = discord.Embed(title="Identity Hack",
                                     description=f"Bain: ``Now for the age. Let's make it {newage}!``",
                                     color=discord.Color.blurple())
            id_embed.add_field(name="Profile",
                               value=f"Name: {newname}\nGender: {gender}\nBirth: {birthdate}\nAge: {str(newage)}")
            await interaction.edit_original_message(content=None, embed=id_embed, view=None)
            await asyncio.sleep(2.5)
            if gender == "Male":
                gender = "Female"
            elif gender == "Female":
                gender = "Male"
            elif gender == "Queering":
                gender = random.choice(
                    ["Agender", "Bigender", "Genderfluid", "Transgender: Male", "Transgender: Female", "Omnigender",
                     "Polygender", "Two Spirit"])
            id_embed = discord.Embed(title="Identity Hack",
                                     description=f"Bain: ``Changed the gender to {gender}...``",
                                     color=discord.Color.blurple())
            id_embed.add_field(name="Profile",
                               value=f"Name: {newname}\nGender: {gender}\nBirth: {birthdate}\nAge: {str(newage)}")
            await interaction.edit_original_message(content=None, embed=id_embed, view=None)
            await asyncio.sleep(2.5)
            id_embed = discord.Embed(title="Identity Hack",
                                     description=f"Bain: ``Hack is done! He'll be having troubles confirming his identity next time...``",
                                     color=discord.Color.blurple())
            id_embed.add_field(name="Profile",
                               value=f"Name: {newname}\nGender: {gender}\nBirth: {birthdate}\nAge: {str(newage)}")
            await interaction.edit_original_message(content=None, embed=id_embed, view=None)
        elif interaction.user == ctx.author and user.mention == secrets["owner_id"]:
            await interaction.response.edit_message(content="``Couldn't hack him. Perhaps try someone else?``",
                                                    embed=None, view=None)
        elif interaction.user == ctx.author and user.mention == secrets["bain_id"]:
            await interaction.response.edit_message(content="``Couldn't hack him. Perhaps try someone else?``",
                                                    embed=None, view=None)
        elif interaction.user != ctx.author:
            await interaction.response.send_message("This hack isn't for you!", ephemeral=True)

    async def hack_pc_callback(interaction):
        if interaction.user == ctx.author and user.mention != secrets["owner_id"] and user.mention != secrets["bain_id"]:
            pc_embed = discord.Embed(
                title="Computer Hack",
                description=f"Bain: ``Starting hack...``",
                color=discord.Colour.blurple()
            )
            await interaction.response.edit_message(content=None, embed=pc_embed, view=None)
            await asyncio.sleep(1)
            pc_embed = discord.Embed(
                title="Computer Hack",
                description=f"Bain: ``Sending pishing email...``",
                color=discord.Colour.blurple()
            )
            await interaction.edit_original_message(content=None, embed=pc_embed, view=None)
            await asyncio.sleep(2)
            pc_embed = discord.Embed(
                title="Computer Hack",
                description=f"Bain: ``Done. While we wait for their response, let's set up our hacking flash drive.``",
                color=discord.Colour.blurple()
            )
            pc_embed.add_field(name="Pishing email",
                               value=f"To: {user}\nFrom: Microsoft Support\n\nDear {user},\nWe are very pleased to tell you that you have won our Xbox One giveaway. Please claim your reward by responding to this email. Thank you.\n\nYours sincerely,\n``Rosa``\nMicrosoft Support")
            await interaction.edit_original_message(content=None, embed=pc_embed, view=None)
            await asyncio.sleep(5)

            correct_button = random.randint(0, 4)
            flash_hack_view = View()
            flash_hack_view.disable_on_timeout = True
            for i in range(5):
                if correct_button == i:
                    newbutton = Button(label="😀")
                    flash_hack_view.add_item(newbutton)

                    async def correct_button_callback(interaction2):
                        if interaction2.user == ctx.author:
                            pc_embed = discord.Embed(
                                title="Computer Hack",
                                description=f"Bain: ``Nice. Flash drive setup is done! Now let's wait for their response...``",
                                color=discord.Colour.blurple()
                            )
                            pc_embed.add_field(name="Pishing email",
                                               value=f"To: {user}\nFrom: Microsoft Support\n\nDear {user},\nWe are very pleased to tell you that you have won our Xbox One giveaway. Please claim your reward by responding to this email. Thank you.\n\nYours sincerely,\n``Rosa``\nMicrosoft Support")
                            await interaction2.response.edit_message(content=None, embed=pc_embed, view=None)
                            await asyncio.sleep(2)
                            ip_add = f"192.{random.randint(100, 200)}.{random.randint(1, 9)}.{random.randint(1, 9)}"
                            pc_embed = discord.Embed(
                                title="Computer Hack",
                                description=f"Bain: ``They've responded! I've got their IP address.``",
                                color=discord.Colour.blurple()
                            )
                            pc_embed.add_field(name="Pishing email",
                                               value=f"To: Microsoft Support\nFrom: {user}\n\nDear Microsoft Support,\nSounds like a scam bro. You're not the legit Microsoft Support.\n\nYours not sincerely,\n``{user}``",
                                               inline=False)
                            pc_embed.add_field(name="Information", value=f"IP Address: {ip_add}")
                            await interaction2.edit_original_message(content=None, embed=pc_embed, view=None)
                            await asyncio.sleep(2)
                            pc_embed = discord.Embed(
                                title="Computer Hack",
                                description=f"Bain: ``Installing spyware remotely...``",
                                color=discord.Colour.blurple()
                            )
                            pc_embed.add_field(name="Information", value=f"IP Address: {ip_add}")
                            await interaction2.edit_original_message(content=None, embed=pc_embed, view=None)
                            await asyncio.sleep(2)
                            pc_embed = discord.Embed(
                                title="Computer Hack",
                                description=f"Bain: ``Getting his secret information...``",
                                color=discord.Colour.blurple()
                            )
                            pc_embed.add_field(name="Information",
                                               value=f"IP Address: ``{ip_add}``\nMost contacted: {names.get_full_name()}")
                            await interaction2.edit_original_message(content=None, embed=pc_embed, view=None)
                            await asyncio.sleep(1)
                            random_name = names.get_full_name()
                            common_mes = random.choice(
                                ['send nudes', 'help me cheat in exam', 'u suc', 'reeeeeeeeeeEE', '<3 i love you'])
                            pc_embed = discord.Embed(
                                title="Computer Hack",
                                description=f"Bain: ``Getting his secret information...``",
                                color=discord.Colour.blurple()
                            )
                            pc_embed.add_field(name="Information",
                                               value=f"IP Address: ``{ip_add}``\nMost contacted: {random_name}\nMost common message: ``{common_mes}``")
                            await interaction2.edit_original_message(content=None, embed=pc_embed, view=None)
                            await asyncio.sleep(1)
                            common_web = random.choice(
                                ["p***hub.com", "discord.com", "roblox.com", "freerobux.com", "buyandsellmeth.com"])
                            pc_embed = discord.Embed(
                                title="Computer Hack",
                                description=f"Bain: ``Getting his secret information...``",
                                color=discord.Colour.blurple()
                            )
                            pc_embed.add_field(name="Information",
                                               value=f"IP Address: ``{ip_add}``\nMost contacted: {random_name}\nMost common message: ``{common_mes}``\nMost visited website: ``{common_web}``")
                            await interaction2.edit_original_message(content=None, embed=pc_embed, view=None)
                            await asyncio.sleep(1)
                            pc_embed = discord.Embed(
                                title="Computer Hack",
                                description=f"Bain: ``Getting his secret information...``",
                                color=discord.Colour.blurple()
                            )
                            pc_embed.add_field(name="Information",
                                               value=f"IP Address: ``{ip_add}``\nMost contacted: {random_name}\nMost common message: ``{common_mes}``\nMost visited website: ``{common_web}``")
                            await interaction2.edit_original_message(content=None, embed=pc_embed, view=None)
                            await asyncio.sleep(1)
                            pc_embed = discord.Embed(
                                title="Computer Hack",
                                description=f"Bain: ``Getting his secret information...``",
                                color=discord.Colour.blurple()
                            )
                            screentime = str(random.randint(2, 24))
                            pc_embed.add_field(name="Information",
                                               value=f"IP Address: ``{ip_add}``\nMost contacted: {random_name}\nMost common message: ``{common_mes}``\nMost visited website: ``{common_web}``\nScreen time: {screentime} hours per day")
                            await interaction2.edit_original_message(content=None, embed=pc_embed, view=None)
                            await asyncio.sleep(1)
                            pc_embed = discord.Embed(
                                title="Computer Hack",
                                description=f"Bain: ``Hack is done!``",
                                color=discord.Colour.blurple()
                            )
                            screentime = random.randint(2, 24)
                            pc_embed.add_field(name="Information",
                                               value=f"IP Address: ``{ip_add}``\nMost contacted: {random_name}\nMost common message: ``{common_mes}``\nMost visited website: ``{common_web}``\nScreen time: {screentime} hours per day")
                            await interaction2.edit_original_message(content=None, embed=pc_embed, view=None)
                            await asyncio.sleep(1)



                        elif interaction2.user != ctx.author:
                            await interaction2.response.send_message("This button isn't for you!", ephemeral=True)

                    newbutton.callback = correct_button_callback
                else:
                    newbutton = Button(label="😄")
                    flash_hack_view.add_item(newbutton)

                    async def wrong_button_callback(interaction2):
                        if interaction2.user == ctx.author:
                            await interaction.edit_original_message(
                                content="**You have messed up the hack! Nooooo! I'll get a better flash drive next time.**",
                                view=None)
                        elif interaction2.user != ctx.author:
                            await interaction2.response.send_message(content="This button isn't for you!",
                                                                     ephemeral=True)

                    newbutton.callback = wrong_button_callback

            pc_embed = discord.Embed(
                title="Computer Hack",
                description=f"Bain: ``Click the odd-one-out button to set up the flash drive! You NEED to be careful! You cannot click the wrong button!``",
                color=discord.Colour.blurple()
            )
            pc_embed.add_field(name="Pishing email",
                               value=f"To: {user}\nFrom: Microsoft Support\n\nDear {user},\nWe are very pleased to tell you that you have won our Xbox One giveaway. Please claim your reward by responding to this email. Thank you.\n\nYours sincerely,\n``Rosa``\nMicrosoft Support")
            await interaction.edit_original_message(content=None, embed=pc_embed, view=flash_hack_view)
            await asyncio.sleep(5)






        elif interaction.user == ctx.author and user.mention == secrets["owner_id"]:
            await interaction.response.edit_message(content="``Couldn't hack him. Perhaps try someone else?``",
                                                    embed=None, view=None)
        elif interaction.user == ctx.author and user.mention == secrets["bain_id"]:
            await interaction.response.edit_message(content="``Couldn't hack him. Perhaps try someone else?``",
                                                    embed=None, view=None)
        elif interaction.user != ctx.author:
            await interaction.response.send_message("This hack isn't for you!", ephemeral=True)

    hack_bank.callback = hack_bank_callback
    hack_id.callback = hack_id_callback
    hack_pc.callback = hack_pc_callback

    hack_view = View()
    hack_view.disable_on_timeout = True
    hack_view.add_item(hack_bank)
    hack_view.add_item(hack_id)
    hack_view.add_item(hack_pc)

    await ctx.reply(content=None, embed=hack_lobby, view=hack_view)

@bot.command()
async def rickroll(ctx, user: discord.Member = None):
    if user is None:
        user = ctx.author
    embed = discord.Embed(title=":)", description=f"You have been rolled by {ctx.author.mention}. You cannot delete this message... Teehee!", colour=discord.Color.blurple())
    embed.set_image(url="https://media.tenor.com/_4YgA77ExHEAAAAd/rick-roll.gif")

    await ctx.reply(content=f"{user.mention}:" if user != ctx.author else None, embed=embed)
    await ctx.message.delete()

# Voice
@bot.command()
@commands.has_permissions(moderate_members=True)
async def join(ctx):
    try:
        channel = ctx.author.voice.channel
        await channel.connect()
        await ctx.reply(f"Joined `#{channel.name}`.")
    except Exception as e:
        if str(e) == "'NoneType' object has no attribute 'channel'":
            await ctx.reply("You are not connected to a voice channel.")
        elif str(e) == "Already connected to a voice channel.":
            await ctx.reply(
                "**An error occurred. This is because:**\n- you are not in the same voice channel as I am; or\n- I am already connected to your voice channel.")
        else:
            await ctx.reply(f"An error occured.\nError: `{e}`")


@bot.command()
@commands.has_permissions(moderate_members=True)
async def leave(ctx):
    try:
        await ctx.guild.voice_client.disconnect()
    except Exception:
        await ctx.reply("Error. Most likely that I had not been in a voice channel in the first place.")


@bot.command()
@commands.has_permissions(moderate_members=True)
async def disconnect(ctx, user: discord.Member, reason=None):
    try:
        if ctx.author.top_role > user.top_role:
            await user.move_to(channel=None, reason=reason)
            await ctx.reply(f"Disconnected {user}.")
        else:
            await ctx.reply("You can only disconnect users lower than your highest role.")
    except Exception:
        await ctx.reply("An error occured.")


@bot.command()
@commands.has_permissions(moderate_members=True)
async def pause(ctx):
    voice = discord.VoiceClient(channel=ctx.author.voice.channel, client=bot)
    try:
        voice.pause()
        await ctx.reply("Audio already paused/no audio is playing.")
    except Exception as e:
        await ctx.reply(f"Error: `{e}`")


@bot.command()
@commands.has_permissions(moderate_members=True)
async def resume(ctx):
    voice = discord.VoiceClient(channel=ctx.author.voice.channel, client=bot)
    try:
        if voice.is_paused():
            voice.resume()
        else:
            await ctx.reply("Already resumed/no audio is playing.")
    except Exception as e:
        await ctx.reply(f"Error: `{e}`")


@bot.command()
@commands.has_permissions(moderate_members=True)
async def stop(ctx):
    voice = discord.VoiceClient(channel=ctx.author.voice.channel, client=bot)
    voice.stop()


@bot.command()
async def play(ctx, song):
    await ctx.reply("Gimme a few seconds...")
    try:
        channel = ctx.author.voice.channel
        await channel.connect()
    except Exception as e:
        if str(e) == "'NoneType' object has no attribute 'channel'":
            await ctx.reply("You are not connected to a voice channel.")
    else:
        # Create playlist
        spotdlsong = f"spotdl {song}"
        spotdlpath = f"C:\\Users\\anson\\Documents\\DATA\\Personal\\Python\\Bain_Discord\\Music\\{ctx.author.guild.id}"

        if not os.path.exists(spotdlpath):
            os.makedirs(spotdlpath)

        spotdlout = "'1%-{artist}-{album}-{title}.{ext}'"
        os.system(f"{spotdlsong} --output {spotdlpath}")

        voiceChannel = discord.utils.get(ctx.guild.voice_channels)
        voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
        voiceChannel.play(discord.FFmpegPCMAudio(
            "Olivia Rodrigo, Joshua Bassett, Disney - Even WhenThe Best Part - From 'High School Musical -  The Musical -  The Series (Season 2).mp3"),
            after=lambda e: print("done", e))


# Owner-only.
@bot.command()
@commands.is_owner()
async def _status(ctx):
    await ctx.reply(f"Online! Running.")

@bot.command()
@commands.is_owner()
async def _end(ctx):
    print(f"Program killed in {ctx.guild.name}.")
    await ctx.send(f"Program killed by {ctx.author.mention}! I'm going offline now. See you guys at the safehouse.")
    exit()

@bot.command(name="_generate_inv")
@commands.is_owner()
async def _gen_inv(ctx, id: int):
    if id is None:
        id = ctx.guild.id
    await ctx.message.delete()
    guild = bot.get_guild(id)
    user = ctx.author

    name = guild.name
    avatar = guild.icon
    owner = guild.owner
    member_count = guild.approximate_member_count
    online_count = guild.approximate_presence_count
    channel = await guild.text_channels[0].create_invite(max_age=0, max_uses=1, temporary=False, unique=False)

    embed = discord.Embed(title=f"Invite Link for {name}")
    embed.set_thumbnail(url=str(avatar))
    embed.add_field(name="Owner", value=f"{owner} (ID: {owner.id})", inline=False)
    embed.add_field(name="No. of members", value=f"{member_count}", inline=False)
    embed.add_field(name="No. of **online** members", value=f"```diff\n{online_count}\n```", inline=False)

    dm = await user.create_dm()
    await dm.send(content=f"{str(channel.url)}", embed=embed)

@bot.command(name="_commands")
@commands.is_owner()
async def _commands(ctx):
    pages = baintools.split_page([i.name for i in bot.commands], 5)
    for i in pages:
        await ctx.reply(i)

    await ctx.reply("end")

# Player system/Currency MAIN
@bot.command()
async def shop(ctx):
    await player_create(ctx, ctx.author.id)
    with open("item_database.json") as file:
        data = json.load(file)

    items = {}
    for item, info in data.items():
        if info["valid"]:
            information = await get_item(item)
            try:
                items[information["category"]].append({"name": information["name"], "desc": information["description"], "category": string.capwords(information["type"])+", "+string.capwords(information["slot"]), "emoji": information["emoji"], "cost": information["data"]["cost"]})
            except KeyError:
                items[information["category"]] = [{"name": information["name"], "desc": information["description"], "category": string.capwords(information["type"])+", "+string.capwords(information["slot"]), "emoji": information["emoji"], "cost": information["data"]["cost"]}]

    select_options = []
    embeds = {}

    for category, item_list in items.items():
        cat_info = await get_category_desc(category)
        select_options.append(discord.SelectOption(label=cat_info["name"], description=cat_info["description"], emoji=cat_info["emoji"]))
        embeds.update({cat_info['name']: []})
        page_count = 0
        split_pages = baintools.split_page(item_list, 5)
        for items_in_page in split_pages:
            # Returns the list of pages. Do stuff every page.
            description = ""
            for item in items_in_page:
                # For every item in the page. Do stuff every item.
                description += f"{item['emoji']} **{item['name']}** ({item['category']})\n*{item['desc']}*\n${'{:,}'.format(item['cost'])}\n\n"
            embed = discord.Embed(title=f"CRIME.NET/Blackmarket/{cat_info['name']}", description=f"_Use `{bot.command_prefix}item` for more information about an item._\n\n"+description, colour=discord.Colour.blurple()).set_footer(text=f"Page {page_count+1}/{len(split_pages)}")
            embeds[cat_info['name']].append(embed)
            page_count += 1

    class Storage:
        def __init__(self):
            self.page = 1
            self.opened = False

    storage = Storage()

    button_prev = Button(label="⏪ Prev.", style=discord.ButtonStyle.blurple)
    button_next = Button(label="⏩ Next", style=discord.ButtonStyle.blurple)
    button_jump = Button(label="Jump...", style=discord.ButtonStyle.gray)

    modal = Modal(title="Blackmarket: Jump to...")
    modal_field = InputText(label="Page Number", style=discord.InputTextStyle.short)
    modal.add_item(modal_field)

    async def modal_callback(interaction):
        if interaction.user == ctx.author:
            try:
                await interaction.response.edit_message(embed=embeds[select.values[0]][int(modal.children[0].value)-1])
            except (TypeError, IndexError, ValueError) as error_msg:
                await interaction.response.send_message(content=f"Input something valid.\n`{error_msg}`", ephemeral=True)

    modal.callback = modal_callback

    async def button_jump_callback(interaction: discord.Interaction):
        if interaction.user == ctx.author:
            await interaction.response.send_modal(modal)

    async def button_prev_callback(interaction):
        if interaction.user == ctx.author:
            if storage.page == 1:
                await interaction.response.defer()
                await interaction.followup.send(content="It's already the first page!", ephemeral=True, wait=True)
            else:
                storage.page -= 1
                new_embed = embeds[select.values[0]][storage.page-1]
                await interaction.response.edit_message(embed=new_embed)

    async def button_next_callback(interaction):
        if interaction.user == ctx.author:
            length_of_cat = len(embeds[select.values[0]])
            if storage.page == length_of_cat:
                await interaction.response.defer()
                await interaction.followup.send(content="It's already the last page!", ephemeral=True, wait=True)
            else:
                storage.page += 1
                new_embed = embeds[select.values[0]][storage.page - 1]
                await interaction.response.edit_message(embed=new_embed)

    select = Select(placeholder="Select a category...", options=select_options)

    async def select_callback(interaction: discord.Interaction):
        if interaction.user == ctx.author:
            if not storage.opened:
                view.add_item(button_prev)
                view.add_item(button_next)
                view.add_item(button_jump)
                storage.opened = True
            await interaction.response.edit_message(embed=embeds[select.values[0]][0], view=view)

    select.callback = select_callback
    button_prev.callback = button_prev_callback
    button_next.callback = button_next_callback
    button_jump.callback = button_jump_callback

    view = View()
    view.disable_on_timeout = True
    view.add_item(select)
    await ctx.reply(embed=discord.Embed(title="CRIME.NET/Blackmarket/Home_Page", description="Select a category below to get started!\n"+f"_Use `{bot.command_prefix}item` for more information about an item._", colour=discord.Color.blurple()), view=view)

@bot.command()
async def buy(ctx, *args):
    arguments = " ".join(args).split(",")
    item = arguments[0]
    try:
        amount = int(arguments[1])
    except IndexError:
        amount = 1
    await player_create(ctx, ctx.author.id)
    data = await player_database()
    key = baintools.item_autocorrect(item, True)

    with open("item_database.json") as file:
        items = json.load(file)
    try:
        items[key]["data"]["cost"]
    except KeyError:
        await throw_crimenet_error(ctx, 404, "Invalid item.")
        return

    cost = items[key]["data"]["cost"]

    if data[str(ctx.author.id)]["cash"] >= cost:
        if amount > 1:
            embed = discord.Embed(title="Blackmarket",
                                  description=f"Are you sure you want to buy {'{:,}'.format(amount)}x {items[key]['name']}?",
                                  colour=discord.Colour.blurple()).set_thumbnail(url=items[key]["image_link"])
            button_confirm = Button(label="Confirm", style=discord.ButtonStyle.blurple)
            button_cancel = Button(label="Cancel", style=discord.ButtonStyle.red)

            async def button_confirm_callback(interaction: discord.Interaction):
                if interaction.user == ctx.author:
                    await interaction.response.defer()
                    data[str(ctx.author.id)]["cash"] -= cost
                    data[str(ctx.author.id)][key] += amount
                    await player_save(data)
                    new_embed = discord.Embed(title="Blackmarket/Transaction_Successful", description=f"Your purchase of {'{:,}'.format(amount)}x {items[key]['name']} has succeeded.\n\n**Total Cost**\n${'{:,}'.format(items[key]['data']['cost']*amount)}", colour=discord.Color.blurple()).set_thumbnail(url=items[key]["image_link"]).set_footer(text=f"Transction ID: {baintools.generate_transaction_id(20)}")
                    await interaction.followup.edit_message(message_id=interaction.message.id, embed=new_embed, view=None)

            async def button_cancel_callback(interaction: discord.Interaction):
                if interaction.user == ctx.author:
                    await interaction.response.edit_message(content=None, embed=discord.Embed(title="Blackmarket/Transaction_Cancelled", description="Transaction has been cancelled.", colour=discord.Color.red()), view=None)

            button_confirm.callback = button_confirm_callback
            button_cancel.callback = button_cancel_callback
            view = View()
            view.disable_on_timeout = True
            view.add_item(button_confirm)
            view.add_item(button_cancel)

            await ctx.reply(content=None, embed=embed, view=view)
        elif amount == 1:
            data[str(ctx.author.id)]["cash"] -= cost
            data[str(ctx.author.id)][key] += amount
            await player_save(data)
            new_embed = discord.Embed(title="Blackmarket/Transaction_Successful", description=f"Your purchase of {'{:,}'.format(amount)}x {items[key]['name']} has succeeded.\n\n**Total Cost**\n${'{:,}'.format(items[key]['data']['cost'])}", colour=discord.Colour.blurple()).set_thumbnail(url=items[key]["image_link"]).set_footer(text=f"Transction ID: {baintools.generate_transaction_id(20)}")
            await ctx.reply(embed=new_embed, view=None)
        else:
            await throw_crimenet_error(ctx, 400, "Invalid amount.")
    else:
        await throw_crimenet_error(ctx, 400, "Insufficient cash.")

@bot.command()
async def sell(ctx, *args):
    arguments = " ".join(args).split(",")
    item = arguments[0]
    try:
        amount = int(arguments[1])
    except IndexError:
        amount = 1

    await player_create(ctx, ctx.author.id)
    data = await player_database()
    key = baintools.item_autocorrect(item, True)

    with open("item_database.json") as file:
        items = json.load(file)
    try:
        items[key]["data"]["cost"]
    except KeyError:
        await throw_crimenet_error(ctx, 404, "Invalid item.")
        return

    sell_data = items[key]
    player = data[str(ctx.author.id)]

    # Run checks for last items
    primary_amt = 0
    secondary_amt = 0

    for _item, _amount in player.items():
        item_data = await get_item(_item)
        if item_data["valid"]:
            if item_data["slot"] == "primary":
                if _amount >= 1:
                    primary_amt += 1
            elif item_data["slot"] == "secondary":
                if _amount >= 1:
                    secondary_amt += 1

    if primary_amt - 1 == 0:
        if sell_data["slot"] == "primary":
            await throw_crimenet_error(ctx, 400, "You cannot sell your last primary weapon!")
            return
    if secondary_amt - 1 == 0:
        if sell_data["slot"] == "secondary":
            await throw_crimenet_error(ctx, 400, "You cannot sell your last secondary weapon!")
            return

    if amount == 1:
        data[str(ctx.author.id)][key] -= 1
        data[str(ctx.author.id)]["cash"] += (sell_data["data"]["cost"] * 0.25).__floor__()
        await player_save(data)
        embed = discord.Embed(title="Blackmarket/Transaction_Successful", description=f"Your transaction of selling **{'{:,}'.format(amount)}x {sell_data['name']}** has succeeded.\n\nYou have been paid **${'{:,}'.format((sell_data['data']['cost'] * 0.25 * amount).__floor__())}**.", colour = discord.Colour.blurple())
        await ctx.reply(content=None, embed=embed)
    elif amount > 1:
        button_confirm = Button(label="Confirm", style=discord.ButtonStyle.blurple)
        button_cancel = Button(label="Cancel", style=discord.ButtonStyle.red)

        async def button_confirm_callback(interaction: discord.Interaction):
            data[str(ctx.author.id)][key] -= amount
            data[str(ctx.author.id)]["cash"] += (sell_data["data"]["cost"] * 0.25 * amount).__floor__()
            await player_save(data)
            new_embed = discord.Embed(title="Blackmarket/Transaction_Successful", description=f"Your transaction of selling **{'{:,}'.format(amount)}x {sell_data['name']}** has succeeded.\n\nYou have been paid **${'{:,}'.format((sell_data['data']['cost'] * 0.25 * amount).__floor__())}**.", colour = discord.Colour.blurple())
            await interaction.response.edit_message(embed=new_embed, view=None)

        async def button_cancel_callback(interaction: discord.Interaction):
            await interaction.response.edit_message(embed=discord.Embed(title="Blackmarket/Transaction_Cancelled", description="Your transaction has been cancelled.", colour=discord.Colour.red()), view=None)

        button_confirm.callback = button_confirm_callback
        button_cancel.callback = button_cancel_callback
        view = View()
        view.disable_on_timeout = True
        view.add_item(button_confirm)
        view.add_item(button_cancel)
        confirmation_embed = discord.Embed(title="Blackmarket/Transaction/Pending", description=f"Are you sure you want to sell **{'{:,}'.format(amount)}x {sell_data['name']}**?\n\nYou will be paid **${'{:,}'.format((sell_data['data']['cost'] * 0.25 * amount).__floor__())}**.", colour=discord.Colour.blurple())
        await ctx.reply(embed=confirmation_embed, view=view)
    else:
        await throw_crimenet_error(ctx, 400, "Invalid amount.")

@bot.command()
async def inspect(ctx, *item_name):
    await player_create(ctx, ctx.author.id)

    item = " ".join(item_name) if len(item_name) > 0 else None

    item = baintools.item_autocorrect(item, True) if item is not None else None
    player = (await player_database())[str(ctx.author.id)]
    if item is None:
        await throw_crimenet_error(ctx, 400, "Invalid weapon.")
    else:
        data = await get_item(item)
        description = f"**({'{:,}'.format(player[item])} owned)**\n{data['description']}\n\n**Category:** {(await get_category_desc(data['category']))['name']} - {data['type']}, {string.capwords(data['slot'])}\n"

        special_list_str = f"**{string.capwords(list(data['data'].keys())[0])}:** {list(data['data'].values())[0][0]} ({', '.join(list(data['data'].values())[0][1:])})\n\n"
        cost_str = f"\nCosts **${'{:,}'.format(data['data']['cost'])}**."

        attr_str = ""
        for attr, val in data['data'].items():
            if type(val) != list and attr != "cost":
                attr_str += f"**{string.capwords(attr.replace('_', ' ')).replace('Rate Of Fire', 'Rate of Fire').replace('Reload', 'Reload Time (seconds)')}:** {'**'+'{:,}'.format(val)+'**' if val is not None else '-'}\n"

        description += special_list_str
        description += attr_str
        description += cost_str

        embed = discord.Embed(title=data["name"], description=description, colour=discord.Colour.blurple()).set_thumbnail(url=data["image_link"])
        await ctx.reply(embed=embed)

@bot.command(name="item")
async def inspect_revoke_item(ctx, *item_name):
    await ctx.invoke(inspect, *item_name)

@bot.command()
async def heist(ctx, *_contract_name: str):
    await player_create(ctx, ctx.author.id)
    _contract = " ".join(_contract_name)
    if len(_contract_name) == 0 or _contract not in baintools.heist_list:
        await throw_crimenet_error(ctx, 400, note="Invalid job.")
    data = {}
    diff_select_view = View()
    diff_select_view.disable_on_timeout = True
    difficulty_select = baintools.difficulty_select
    difficulty_od_select = baintools.difficulty_od_select
    button_confirm = baintools.difficulty_finish
    button_cancel = baintools.difficulty_cancel

    async def select_callback(interaction):
        if interaction.user == ctx.author:
            await interaction.response.defer()

    async def confirm_callback(interaction):
        if interaction.user == ctx.author:
            await interaction.message.delete()
            await interaction.response.defer()
            try:
                data["difficulty"] = difficulty_select.values[0]
            except IndexError:
                data["difficulty"] = "normal"
            try:
                data["od"] = True if difficulty_od_select.values[0] == "True" else False
            except IndexError:
                data["od"] = False

            await getattr(PlayerHeist(), baintools.heist_autocorrect(_contract))(ctx=ctx,
                                                                                          difficulty=data["difficulty"],
                                                                                          od=data["od"])

    async def cancel_callback(interaction):
        if interaction.user == ctx.author:
            await interaction.response.edit_message(content=None, view=None,
                                                    embed=discord.Embed(title="CRIME.NET/Contract Broker",
                                                                        description="Cancelled.",
                                                                        colour=discord.Color.blurple()))

    difficulty_select.callback = select_callback
    difficulty_od_select.callback = select_callback
    button_confirm.callback = confirm_callback
    button_cancel.callback = cancel_callback

    diff_select_view.add_item(difficulty_select)
    diff_select_view.add_item(difficulty_od_select)
    diff_select_view.add_item(button_confirm)
    diff_select_view.add_item(button_cancel)

    embed = discord.Embed(title="CRIME.NET/Contract Broker", description="Select a difficulty.",
                          colour=discord.Colour.blurple())

    await ctx.reply(content=None, embed=embed, view=diff_select_view)

# Player system/Profile
@bot.command(name="profile")
async def profile(ctx, user: discord.Member = None):
    if user is None:
        user = ctx.author

    if str(user.id) not in list((await player_database()).keys()) and ctx.author != user:
        await ctx.reply("User is not on `CRIME.NET`.")
        return

    await player_create(ctx, user.id)
    data = (await player_database())[str(user.id)]
    profile_char_dtb = (await get_item(data['char']))
    profile_char = f"**{profile_char_dtb['name'].upper()}**\n**Age:** {profile_char_dtb['age']}\n**Height:** {profile_char_dtb['physical_description']['height'][0]}\n**Build:** {', '.join(profile_char_dtb['physical_description']['build'])}\n**Signature Weapon:** {(await get_item(data['weapon']))['name']} {(await get_item(data['weapon']))['emoji']}"
    profile_reputation = f"**Heisting since:** {':'.join(datetime.datetime.fromtimestamp(data['join']).strftime('%Y-%m-%d %H:%M:%S.%f').split(':')[:2:])}\n**Infamy {data['infamy']}**\n**Reputation Level {baintools.to_roman(data['infamy']) if data['infamy'] > 0 else ''}{'-' if data['infamy'] > 0 else ''}{data['reputation']}**\n{'{:,}'.format(data['exp'])}/{'{:,}'.format(baintools.calculate_experience(data['reputation']))} EXP\n**{'{:,}'.format(data['heist_stat_success'])}** heists succeeded\n**{'{:,}'.format(data['heist_stat_failure'])}** heists failed\n[Success rate: {baintools.calculate_success_rate(data)}]"
    embed = discord.Embed(
        title=user.name,
        description=f"{profile_char}\n\n{profile_reputation}",
        colour=discord.Colour.blurple()
    )
    embed.set_thumbnail(url=profile_char_dtb['image_mask'])

    view = View()
    view.disable_on_timeout = True

    button_bal = Button(label="Balance", style=discord.ButtonStyle.blurple)
    button_inv = Button(label="Inventory", style=discord.ButtonStyle.blurple)

    async def button_bal_callback(interaction: discord.Interaction):
        await interaction.response.defer()
        await balance(ctx, user)

    async def button_inv_callback(interaction: discord.Interaction):
        await interaction.response.defer()
        await inventory(ctx, user)

    button_bal.callback = button_bal_callback
    button_inv.callback = button_inv_callback
    view.add_item(button_bal)
    view.add_item(button_inv)

    await ctx.reply(embed=embed, view=view)

@bot.group(name="customize")
async def _customize(ctx: commands.Context):
    if ctx.invoked_subcommand is None:
        await throw_crimenet_error(ctx, 404)

@_customize.command(name="character")
async def _customize_char(ctx, *char_name):
    await player_create(ctx, ctx.author.id)
    data = await player_database()
    char = "_".join(char_name).lower()
    data[str(ctx.author.id)]["char"] = char
    await player_save(data)
    embed = discord.Embed(title="CRIME.NET/Profile", description=f"`Successfully changed your character to {(await get_item(char))['name']}.`", colour=discord.Colour.blurple()).set_thumbnail(url=(await get_item(char))['image_mask'])
    await ctx.reply(embed=embed)

@_customize.command(name="char")
async def _customize_char_revoke_char(ctx, *args):
    await ctx.invoke(_customize_char, *args)

@_customize.command(name="weapon")
async def _customize_weapon(ctx, *weapon_name):
    await player_create(ctx, ctx.author.id)
    try:
        await get_item("w_" + "_".join(weapon_name).lower().replace(".", ""))
    except KeyError:
        await throw_crimenet_error(ctx, 400, note="Weapon doesn't exist.")
    else:
        data = await player_database()
        if data[str(ctx.author.id)]["w_" + "_".join(weapon_name)] > 0:
            await player_setattr(str(ctx.author.id), "weapon", "w_" + "_".join(weapon_name).lower().replace(".", ""))
            await ctx.reply(embed=discord.Embed(title="CRIME.NET/Profile", description=f"Successfully changed your signature weapon to `{(await get_item('w_' + ' '.join(weapon_name)))['name']}`.", colour=discord.Colour.blurple()).set_thumbnail(url="https://static.wikia.nocookie.net/payday/images/7/73/AMCAR-icon.png/revision/latest/scale-to-width-down/200?cb=20130806182054"))
        else:
            await throw_crimenet_error(ctx, 400, note="You don't own this weapon.")

@_customize.command(name="wp")
async def _customize_weapon_revoke_wp(ctx, *args):
    await ctx.invoke(_customize_weapon, *args)

@bot.command()
async def inventory(ctx, user: discord.Member = None):
    await player_create(ctx, ctx.author.id)
    if user is None:
        user = ctx.author

    try:
        data = (await player_database())[str(user.id)]
    except KeyError:
        await ctx.reply("User is not on `CRIME.NET`.")
        return
    embed_data = {}

    for attr, val in data.items():
        if (await get_item(attr))["valid"]:
            try:
                if val > 0:
                    embed_data[((await get_item(attr))["category"])].append(str(f"{'{:,}'.format(val)}x "+(await get_item(attr))["name"]))
            except KeyError:
                if val > 0:
                    embed_data[((await get_item(attr))["category"])] = [str(f"{'{:,}'.format(val)}x {(await get_item(attr))['name']}")]

    embeds = []
    select_options = []
    for category, items in embed_data.items():
        category_data = await get_category_desc(category)
        embed = discord.Embed(title=f"CRIME.NET/{user.name.replace(' ', '_')}/Inventory", description=f"**Inventory/{category_data['name']}\n**"+"\n".join(items), colour=discord.Color.blurple())
        embed.set_thumbnail(url=user.avatar)
        option = discord.SelectOption(label=category_data["name"], description=category_data["description"], emoji=category_data["emoji"])
        embeds.append(embed)
        select_options.append(option)

    select = Select(placeholder="Select a category...", options=select_options)

    async def select_callback(interaction):
        if interaction.user == ctx.author:
            designated_embed = None
            for i in embeds:
                if i.description.startswith(f"**Inventory/{select.values[0]}"):
                    designated_embed = embed
            await interaction.response.edit_message(embed=designated_embed)

    select.callback = select_callback
    view = View()
    view.disable_on_timeout = True
    view.add_item(select)

    await ctx.reply(embed=embeds[0], view=view)

@bot.command(name="inv")
async def inventory_invoke_inv(ctx, user: discord.Member = None):
    if user is None:
        user = ctx.author
    await ctx.invoke(inventory, user)

@bot.command()
async def balance(ctx, user: discord.Member = None):
    await player_create(ctx, ctx.author.id)
    if user is None:
        user = ctx.author
    data = (await player_database())[str(user.id)]
    cash = data['cash']
    offshore = data['offshore']
    item_worth = 0
    for attr, val in data.items():
        try:
            if val >= 1:
                item_worth += (await get_item(attr))["data"]["cost"]
        except (KeyError, TypeError):
            pass

    embed = discord.Embed(title=f"CRIME.NET/{user.name.replace(' ', '_')}/Balance", description=f"**Cash:** ${'{:,}'.format(cash)}\n**Offshore Account:** ${'{:,}'.format(offshore)} [Total: ${'{:,}'.format(cash+offshore)}]\n**Item Worth:** ${'{:,}'.format(item_worth*0.25)}\n\n**Net Worth:** ${'{:,}'.format(cash+offshore+(item_worth*0.25))}", colour=discord.Colour.blurple())
    await ctx.reply(content=None, embed=embed)

@bot.command(name="bal")
async def balance_invoke_bal(ctx, user: discord.Member = None):
    await ctx.invoke(balance, user)

# Player system/Casual
@bot.command()
async def bet(ctx, amount: int = 1000):
    await player_create(ctx, ctx.author.id)
    cash_amt = (await player_database())[str(ctx.author.id)]['cash']
    if amount > cash_amt:
        await throw_crimenet_error(ctx, 400, note="You don't enough money.")
        return
    elif amount < 1000:
        await throw_crimenet_error(ctx, 400, note="You need to bet at least $1,000.")
        return
    bain_bet = random.randint(1, 15)
    player_bet = random.randint(1, 15)
    diff = abs(bain_bet - player_bet)
    win = False
    tie = False

    if bain_bet > player_bet:
        win = False
    elif bain_bet < player_bet:
        win = True
    elif bain_bet == player_bet:
        win = False
        tie = True

    if win:
        embed = discord.Embed(title="CRIME.NET/Quick Bet", description="Result: **WIN!**",
                              colour=discord.Colour.green())
        embed.add_field(name="Bain rolled:", value=bain_bet)
        embed.add_field(name=f"You rolled:", value=player_bet)
        embed.add_field(name=f"You won by ${'{:,}'.format(diff * amount)}!",
                        value=f"_`Transaction completed: {baintools.generate_transaction_id(35)}`_", inline=False)
        await player_add_bal(ctx.author.id, "cash", diff * amount)
        await ctx.reply(content=None, embed=embed)
    elif tie:
        embed = discord.Embed(title="CRIME.NET/Quick Bet", description="Result: **TIE!**", colour=discord.Colour.blue())
        embed.add_field(name="Bain rolled:", value=bain_bet)
        embed.add_field(name=f"You rolled:", value=player_bet)
        embed.add_field(name=f"Tie!", value=f"_`Transaction cancelled: {baintools.generate_transaction_id(35)}`_",
                        inline=False)
        await ctx.reply(content=None, embed=embed)
    else:
        embed = discord.Embed(title="CRIME.NET/Quick Bet", description="Result: **LOSE!**", colour=discord.Colour.red())
        embed.add_field(name="Bain rolled:", value=bain_bet)
        embed.add_field(name=f"You rolled:", value=player_bet)
        embed.add_field(name=f"You lost by ${'{:,}'.format(diff * amount)}!",
                        value=f"_`Transaction completed: {baintools.generate_transaction_id(35)}`_", inline=False)
        await player_add_bal(ctx.author.id, "cash", diff * amount * -1)
        await ctx.reply(content=None, embed=embed)

@bot.command()
async def scout(ctx):
    await player_create(ctx, ctx.author.id)
    users = await player_database()
    user = ctx.author
    embed = discord.Embed(title="The Search", description="Where would you like to search?",
                          colour=discord.Colour.blurple())

    b1 = Button(label="Dallas' Office", style=discord.ButtonStyle.blurple)
    b2 = Button(label="Hoxton's Files", style=discord.ButtonStyle.blurple)
    b3 = Button(label="Clover's Surveillance Centre", style=discord.ButtonStyle.blurple)
    b4 = Button(label="Scarface's Room", style=discord.ButtonStyle.blurple)
    b5 = Button(label="Duke's Gallery", style=discord.ButtonStyle.blurple)
    b6 = Button(label="Houston's Workshop", style=discord.ButtonStyle.blurple)
    b7 = Button(label="Sydney's Studio", style=discord.ButtonStyle.blurple)
    b8 = Button(label="Rust's Corner", style=discord.ButtonStyle.blurple)
    b9 = Button(label="Joy's Van", style=discord.ButtonStyle.blurple)
    b10 = Button(label="Bonnie's Gambling Den", style=discord.ButtonStyle.blurple)
    b11 = Button(label="Jiro's Lounge", style=discord.ButtonStyle.blurple)
    b12 = Button(label="Jimmy's Bar", style=discord.ButtonStyle.blurple)
    b13 = Button(label="Chains' Weapon Workshop", style=discord.ButtonStyle.blurple)
    b14 = Button(label="Sangres' Cave", style=discord.ButtonStyle.blurple)
    b15 = Button(label="Ethan and Hila's Video Corner", style=discord.ButtonStyle.blurple)
    b16 = Button(label="The Common Rooms", style=discord.ButtonStyle.blurple)
    b17 = Button(label="Bohdi's Surfboard Workshop", style=discord.ButtonStyle.blurple)
    b18 = Button(label="Jacket's Hangout", style=discord.ButtonStyle.blurple)
    b19 = Button(label="Sokol's Hockey Gym", style=discord.ButtonStyle.blurple)
    b20 = Button(label="Dragan's Gym", style=discord.ButtonStyle.blurple)
    b21 = Button(label="Wolf's Workshop", style=discord.ButtonStyle.blurple)
    b22 = Button(label="John Wick's Shooting Range", style=discord.ButtonStyle.blurple)
    b23 = Button(label="The Vault", style=discord.ButtonStyle.blurple)
    b24 = Button(label="Aldstone's Quarters", style=discord.ButtonStyle.blurple)

    async def call(interaction):
        rng = random.randint(1, 4)
        earnings = random.randint(100, 10000)
        if rng == 2:
            embed_end = discord.Embed(title="The Search", description="You found nothing.",
                                      colour=discord.Color.og_blurple())
            await interaction.response.edit_message(content=None, embed=embed_end, view=None)
        else:
            embed_end = discord.Embed(title="The Search", description=f"You found ${'{:,}'.format(earnings)}!",
                                      colour=discord.Color.green())
            await interaction.response.edit_message(content=None, embed=embed_end,
                                                    view=None)
            users[str(user.id)]["cash"] += earnings
            await player_save(users)

    buttons = [b1, b2, b3, b4, b5, b6, b7, b8, b9, b10, b11, b12, b13, b14, b15, b16, b17, b18, b19, b20, b21, b22, b23,
               b24]

    for i in buttons:
        i.callback = call

    buttons_ran = random.sample(buttons, 4)

    view = View()
    view.disable_on_timeout = True
    for i in range(4):
        view.add_item(buttons_ran[i])

    await ctx.reply(content=None, embed=embed, view=view)


# Fetch player database.
async def player_database():
    with open("mainbank.json") as file:
        data = json.load(file)
        return data


async def player_create(ctx, user_id: int):
    player_objects = PlayerInfo.player_objects
    if user_id is None:
        return False
    else:
        data = await player_database()
        if str(user_id) in list(data.keys()):
            return False
        else:
            ct = datetime.datetime.utcnow() + datetime.timedelta(hours=1)
            button = Button(label="Continue reading...", style=discord.ButtonStyle.blurple)
            clear_button = Button(label="OK", style=discord.ButtonStyle.blurple)

            async def button_callback(interaction):
                if interaction.user == ctx.author:
                    await interaction.response.send_message(
                        """
                        text.
                        """, ephemeral=True
                    )

            async def clear_callback(interaction):
                if interaction.user == ctx.author:
                    await interaction.message.delete()

            button.callback = button_callback
            clear_button.callback = clear_callback
            view = View()
            view.disable_on_timeout = True
            view.add_item(button)
            view.add_item(clear_button)

            await ctx.reply(
                f"**YOU HAVE A NEW MESSAGE**\n**From:** Bain `[bain@///REDACTED///]`\n**To:** {ctx.author.name}\n**Date:** {':'.join((str(datetime.datetime.strptime(str(ct), '%Y-%m-%d %H:%M:%S.%f')).split(':')[:2:]))} (GMT+1)\n**Subject**: Welcome to crime.net\n\nGreetings, {ctx.author.name}, and welcome to Crime.net.\n\n If you are reading this, it means you have cleared for access to the hub of our organization. Congratulations; you have taken your first step into a larger world.\n\nLet's have a look at the basic functions of Crime.net. Don't worry if it seems complex at first, everything is more or less self-explanatory.",
                view=view)
            data[str(user_id)] = {}
            for obj, amt in player_objects.items():
                data[str(user_id)][obj] = amt

            with open("mainbank.json", "w") as file:
                json.dump(data, file)


async def player_setattr(user_id: str, attr_id: str, value):
    data = await player_database()
    data[user_id][attr_id] = value
    await player_save(data)


async def player_change_attr_by(user_id: str, attr_id: str, value):
    data = await player_database()
    data[user_id][attr_id] += value
    await player_save(data)


async def player_add_bal(user_id: str, method: str, amount: int):
    data = await player_database()
    data[str(user_id)][method] += amount
    await player_save(data)


async def player_get_heist_rewards(_heist):
    with open("heist_rewards_database.json") as file:
        if heist is not None:
            return json.load(file)[heist]
        else:
            return json.load(file)


async def player_save(data):
    with open("mainbank.json", "w") as file:
        json.dump(data, file)


async def get_item(item):
    with open("item_database.json") as file:
        data = json.load(file)
        return data[item]


async def get_category_desc(category=None):
    with open("category_desc_database.json") as file:
        if category is not None:
            return json.load(file)[category]
        else:
            return json.load(file)

# .define command
async def dictsearch(arg):
    async with aiohttp.ClientSession() as session:
        word_id = arg.lower()
        url = "https://api.dictionaryapi.dev/api/v2/entries/en/" + word_id.lower()
        async with session.get(url) as res:
            r = await res.text()
            return r

# CRIME.NET custom embed errors
async def throw_crimenet_error(ctx: commands.Context, err_code: int = 404, note: str = None):
    guide = {
        400: "Bad request. Try passing some valid arguments?",
        404: "Not found. Try using a valid command?"
    }
    await ctx.reply(content=None, embed=discord.Embed(title=f"CRIME.NET/Error/{err_code}", description=f"{guide[err_code]}\n{'_(No additional information given.)_' if note is None else f'`{note}`'}", colour=discord.Colour.red()))

# .wiki command
def wikisummary(arg):
    definition = wikipedia.summary(arg, sentences=3, chars=1000)
    url = wikipedia.page(arg, redirect=True).url
    search_keyword = wikipedia.page(arg, redirect=True).title
    return definition, url, search_keyword


bot.run(secrets["discord_bot_token"])
