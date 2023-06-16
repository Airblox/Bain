import asyncio
import string
import subprocess
import sys
import traceback
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
import baintools
import spotdl.__main__
import pr_secrets as real_pr_secrets

from program_dep.random_string import randomjob
from datetime import date
from collections import Counter
from discord.ext import commands
from discord.ui import Button, Select, View
from wikipedia import PageError, DisambiguationError

print(f"INITIALIZE AT {datetime.datetime.now()}\n")
print("CRIME.NET CONNECTION\nSTATUS CODE: 200\n>>> Fetching server information...")


# Replit configuration.
class ProgramSecrets:
    def __init__(self):
        self.on_pycharm = True

    def __getattr__(self, item):
        return os.getenv(item) if not self.on_pycharm else getattr(real_pr_secrets, item)


pr_secrets = ProgramSecrets()
os.chdir(pr_secrets.os_dir)

bot = commands.Bot(command_prefix=".", intents=discord.Intents.all(), owner_id=pr_secrets.owner_id,
                   auto_sync_commands=True)
bot.remove_command("help")


# Events
@bot.event
async def on_ready():
    await bot.change_presence(status=discord.Status.online, activity=discord.Game(name="CRIME.NET | .help"))
    guild_count = 0
    print(f">>> Server info <{datetime.datetime.now()}>")
    for guild in bot.guilds:
        print(f"- {guild.name} ({guild.owner}, {guild.id}).")
        guild_count = guild_count + 1

    print(f"(In {guild_count} servers in total.)\n\nBain is online. Run \"._logout\" to get Bain offline.")


@bot.event
async def on_command_error(ctx: commands.Context, error):
    if hasattr(ctx.command, 'on_error'):
        return

    ignored = (commands.CommandNotFound,)
    error = getattr(error, 'original', error)

    if isinstance(error, ignored):
        return

    if isinstance(error, commands.DisabledCommand):
        await ctx.reply(f'{ctx.command} has been disabled.')

    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.reply(f'Arguments are missing for {ctx.command}.')

    elif isinstance(error, commands.NoPrivateMessage):
        try:
            await ctx.author.send(f'{ctx.command} can not be used in Private Messages.')
        except discord.HTTPException:
            pass

    elif isinstance(error, commands.BadArgument):
        await ctx.reply(f'Bad argument passed for {ctx.command}')

    elif isinstance(error, commands.MissingPermissions):
        await ctx.reply(f'Sorry - you do not have the permissions for using {ctx.command}.')

    elif isinstance(error, discord.errors.Forbidden):
        await ctx.reply(content=f"Sorry - `{error}`")

    elif isinstance(error, commands.NotOwner):
        await ctx.reply("Sorry - you are not the owner of this bot.")

    elif isinstance(error, discord.errors.NotFound):
        pass

    else:
        print(f"Error time: {datetime.datetime.now()}\n"+'Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
        await ctx.reply("`An error occurred!`")
        traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)


@bot.event
async def on_voice_state_update(member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
    if not member.id == pr_secrets.bain_id:
        return
    elif before.channel is None:
        # noinspection PyTypeChecker
        voice: discord.VoiceClient = after.channel.guild.voice_client
        time = 0
        while True:
            await asyncio.sleep(1)
            time += 1
            if voice.is_playing():
                time = 0
            if time == 30:
                await voice.disconnect(force=True)
            if not voice.is_connected():
                break


@bot.command(name="help")
async def _help(ctx: commands.Context, command=None):
    """___category__General___category__
___parameters__None.___parameters__
___description__Displays the help page.___description__
___duplicate__##none##___duplicate__"""
    if command is None:
        command_dict = {}
        for i in list(bot.commands):
            if i.callback.__doc__ is None:
                docstr = "No description available currently."
                category = "unknown"
                parameters = "unknown"
                invoke = None
            else:
                original_docstring = i.callback.__doc__
                duplicate_split_docstring = original_docstring.split("___duplicate__")[0]
                
                category = duplicate_split_docstring.split("___category__")[1]
                parameters = duplicate_split_docstring.split("___parameters__")[1]
                docstr = duplicate_split_docstring.split("___description__")[1]
                invoke = None if original_docstring.split("___duplicate__")[1] == "##none##" else i.callback.__doc__.split("___duplicate__")[1]

            if invoke is None and not i.name.startswith("_"):
                command_dict.update({i.name: {"doc": docstr, "category": category, "parameters": parameters}})

        print(command_dict)

        command_keys = []
        command_info = []
        for name, info in sorted(command_dict.items()):
            command_keys.append(name)
            command_info.append(info)

        categorised = {}

        for __name, __info in zip(command_keys, command_info):
            try:
                categorised[__info["category"]].append(f"**{bot.command_prefix}{__name}**\n*{__info['doc']}*")
            except KeyError:
                categorised[__info["category"]] = [f"**{bot.command_prefix}{__name}**\n*{__info['doc']}*"]

        with open("command_category_description_database.json") as file:
            cat_info = json.load(file)

        for k in list(cat_info.keys()):
            try:
                categorised.update({k: categorised[k]})
            except KeyError:
                pass

        embeds = {}
        options = []
        for page_name, __line in categorised.items():
            # Per category
            cat_embed = discord.Embed(title=f"Help Page/{page_name}",
                                      description="\n\n".join(__line) + "\n\n_Tip: Use .help `command` for more details about a command!_",
                                      colour=discord.Colour.blurple()).set_thumbnail(url="https://static.wikia.nocookie.net/payday/images/1/18/I_Wasn%27t_Even_There%21.jpg/revision/latest?cb=20130812172734")
            try:
                embeds[page_name].append(cat_embed)
            except KeyError:
                embeds[page_name] = [cat_embed]
            options.append(discord.SelectOption(label=page_name, description=cat_info[page_name]["description"],
                                                emoji=cat_info[page_name]["emoji"]))

        class Storage:
            def __init__(self):
                self.opened = False

        storage = Storage()

        select = Select(placeholder="Select a category...", options=options)

        async def select_callback(interaction: discord.Interaction):
            if interaction.user == ctx.author:
                if not storage.opened:
                    storage.opened = True
                await interaction.response.edit_message(embed=embeds[select.values[0]][0], view=view)

        select.callback = select_callback
        view = View()
        view.disable_on_timeout = True
        view.add_item(select)

        await ctx.reply(content=None, embed=discord.Embed(title="Help Page", description="Select a category to begin!",
                                                          colour=discord.Colour.blurple()).set_thumbnail(
            url="https://static.wikia.nocookie.net/payday/images/1/18/I_Wasn%27t_Even_There%21.jpg/revision/latest?cb=20130812172734").set_footer(
            text="Tip: Use .help <command> for more details about a command!"), view=view)

    else:
        target = None
        for i in list(bot.commands):
            if i.name == command.replace(".", ""):
                target = i
                break
        try:
            parameters = target.callback.__doc__.split("___parameters__")[1]
        except AttributeError:
            await throw_crimenet_error(ctx, 400, "Invalid command.")
            return
        docstr = target.callback.__doc__.split("___description__")[1]

        await ctx.reply(content=None, embed=discord.Embed(title=f"{bot.command_prefix}{target.qualified_name}",
                                                          description=f"*{docstr}*",
                                                          colour=discord.Colour.blurple()).add_field(name="Parameters",
                                                                                                     value=parameters).set_thumbnail(
            url="https://static.wikia.nocookie.net/payday/images/8/85/Texas_Treasures%2C_Part_2.jpg/revision/latest?cb=20221020182240"))


# Moderation
@bot.command(name="assign")
@commands.has_permissions(moderate_members=True)
async def assign_role(ctx, role: discord.Role, user: discord.Member = None):
    """___category__Moderation___category__
___parameters__`role` - The role to assign.
`user` - The user to assign to.___parameters__
___description__Assigns a role to a member.___description__
___duplicate__##none##___duplicate__"""
    await user.add_roles(role)
    await ctx.send(f"Assigned {user.mention} the role of {role}. (Moderator: {ctx.author.mention}.)")


@bot.command(name="demote")
@commands.has_permissions(moderate_members=True)
async def demote_role(ctx, role: discord.Role, user: discord.Member = None):
    """___category__Moderation___category__
___parameters__`role` - The role to remove.
`user` - The user to remove the role from.___parameters__
___description__Removes a role from a member.___description__
___duplicate__##none##___duplicate__"""
    await user.remove_roles(role)
    await ctx.send(f"Moderator {ctx.author.mention} has fired {user.mention} from the role of {role}.")


@bot.command()
@commands.has_permissions(moderate_members=True)
async def clear(ctx, arg):
    """___category__Moderation___category__
___parameters__`arg` - The number of messages to clear.___parameters__
___description__Deletes messages in a channel.___description__
___duplicate__purge___description"""
    msg = await ctx.send(f"Purging/clearing {arg} messages...")
    await msg.delete()
    await ctx.channel.purge(limit=(int(arg) + 1))
    successmsg = await ctx.send(f"Successfully purged/cleared {arg} message(s).")
    await successmsg.delete(delay=5)


@bot.command()
@commands.has_permissions(moderate_members=True)
async def purge(ctx, arg):
    """___category__Moderation___category__
___parameters__`arg` - The number of messages to clear.___parameters__
___description__Deletes messages in a channel.___description__
___duplicate__##none##___duplicate__"""
    await ctx.invoke(clear, arg)


@bot.command()
@commands.has_permissions(moderate_members=True)
async def timeout(ctx, user: discord.Member = None, time=None, *, reason=None):
    """___category__Moderation___category__
___parameters__`user` - The user to timeout.
`time` - The length of the timeout. (e.g. 1h)
`reason` - *Optional*. The reason for the timeout, shown in the audit log.___parameters__
___description__Timeouts a user.___description__
___duplicate__##none##___duplicate__"""
    time = humanfriendly.parse_timespan(time)
    await user.timeout(until=discord.utils.utcnow() + datetime.timedelta(seconds=time),
                       reason=f"{ctx.author} - {reason}")
    await ctx.send(
        f"{user} has been timed out for {time} seconds by {ctx.author.mention} | \"{reason}\" -{ctx.author}.")


@bot.command()
@commands.has_permissions(moderate_members=True)
async def untimeout(ctx, user: discord.Member = None, *, reason=None):
    """___category__Moderation___category__
___parameters__`user` - The user to remove the timeout from.
`reason` - *Optional*. The reason for removing the timeout, shown in the audit log.___parameters__
___description__Removes a timeouts from a user.___description__
___duplicate__##none##___duplicate__"""
    await user.timeout(until=None, reason=reason)
    await ctx.send(f"Timeout has been removed from {user.mention} by {ctx.author.mention}. [Reason: {reason}]")


@bot.command()
@commands.has_permissions(moderate_members=True)
async def kick(ctx, user: discord.Member = None, *kick_reason):
    """___category__Moderation___category__
___parameters__`user` - The user to kick.
`reason` - *Optional*. The reason for the kick, shown in the audit log.___parameters__
___description__Kicks a user.___description__
___duplicate__##none##___duplicate__"""
    reason = " ".join(kick_reason)
    if user == None:
        await ctx.reply("Specify a user.")
    else:
        await user.kick(reason=reason)
        await ctx.reply(f"Successfully kicked {user.mention}. Reason: ``{ctx.author} - {reason}``")


@bot.command(description="Bans a user from the server.")
@commands.has_permissions(moderate_members=True)
async def ban(ctx, user: discord.Member = None, deletemessages="false", reason=None):
    """___category__Moderation___category__
___parameters__`user` - The user to ban.
`reason` - *Optional*. The reason for the ban, shown in the audit log.___parameters__
___description__Bans a user.___description__
___duplicate__##none##___duplicate__"""
    if user == None:
        await ctx.reply("Specify a user.")
    else:
        if deletemessages == "yes," or deletemessages == "true,":
            await user.ban(delete_message_days=7, reason=reason)
            await ctx.reply(
                f"Successfully banned {user.mention}, and deleted their messages in the past week. Reason: ``{ctx.author} - {reason}``")
        elif deletemessages == "no," or deletemessages == "false,":
            await user.ban(delete_message_days=0, reason=reason)
            await ctx.reply(
                f"Successfully banned {user.mention} (messages were not cleared). Reason: ``{ctx.author} - {reason}``")


@bot.command(description="Unbans a user from the server.")
@commands.has_permissions(moderate_members=True)
async def unban(ctx, user: discord.User = None, reason=None):
    """___category__Moderation___category__
___parameters__`user` - The user to unban.
`reason` - *Optional*. The reason for the revocation of the ban, shown in the audit log.___parameters__
___description__Unbans a user.___description__
___duplicate__##none##___duplicate__"""
    if user is None:
        await ctx.reply("Specify a user.")
    else:
        await ctx.guild.unban(user=user, reason=reason)
        await ctx.reply(f"Successfully unbanned {user.mention} from the server. Reason: ``{ctx.author} - {reason}``")


@bot.command(description="Kicks members who have been inactive.")
@commands.has_permissions(moderate_members=True)
async def prune(ctx, duration=7, reason="None.", *roles):
    """___category__Moderation___category__
___parameters__`duration` - The time range for the prune.
`reason` - *Optional*. The reason for the prune, shown in the audit log.___parameters__
___description__Prunes members - kicks members who have been inactive.___description__
___duplicate__##none##___duplicate__"""
    guild = ctx.guild

    pruning = await guild.prune_members(days=duration, roles=roles, reason=f"{ctx.author} - reason")
    await ctx.reply(
        f"Pruned {pruning} members who were inactive on this server for more than {duration} days. | Reason: {reason}")


# Server administration
@bot.command()
@commands.has_permissions(administrator=True)
async def addrole(ctx, *role_name):
    """___category__Server Management___category__
___parameters__`role_name` - The name of the role to create.___parameters__
___description__Adds a role with permission options.___description__
___duplicate__##none##___duplicate__"""
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
    """___category__Server Management___category__
___parameters__`role_name` - The name of the role to delete.___parameters__
___description__Deletes a role.___description__
___duplicate__##none##___duplicate__"""
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
    """___category__Server Management___category__
___parameters__None.___parameters__
___description__Creates an invite.___description__
___duplicate__##none##___duplicate__"""
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
    """___category__Server Management___category__
___parameters__`inv` - The link, or ID of the invite to revoke.___parameters__
___description__Revokes an invite.___description__
___duplicate__##none##___duplicate__"""
    arg1 = arg.replace("https://discord.gg/", "")
    delete_invite = await bot.fetch_invite(url=f"https://discord.gg/{arg1}", with_counts=False, with_expiration=False)
    await delete_invite.delete(reason=reason)
    await ctx.reply(f"Invite \"{arg1}\" has been revoked.")


# Tools
@bot.command()
async def ping(ctx):
    """___category__Tools___category__
___parameters__None.___parameters__
___description__Responds with the bot's latency.___description__
___duplicate__##none##___duplicate__"""
    pingembed = discord.Embed(
        title="Pong!",
        description=f"Latency: {round(bot.latency * 1000)} ms.",
        color=discord.Colour.green()
    )
    await ctx.reply(embed=pingembed)


@bot.command(name="wiki")
async def cmd_wikipedia(ctx, *args):
    """___category__Tools___category__
___parameters__`subject` - The thing to search on Wikipedia.___parameters__
___description__Gets a result from Wikipedia.___description__
___duplicate__##none##___duplicate__"""
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
    """___category__Tools___category__
___parameters__`term` - The word to search up in the dictionary.___parameters__
___description__Searches up a word in the dictionary.___description__
___duplicate__##none##___duplicate__"""
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
    """___category__Tools___category__
___parameters__
**Quick Note:** The poll automatically ends after 5 minutes of inactivity. Results will automatically be sent out through a new message.

`title` - **Wrap in quotes.** The title of the poll.
`*options` - The options for the poll, separated with a comma.___parameters__
___description__Creates a poll for everyone to vote in the server.___description__
___duplicate__##none##___duplicate__"""
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
        try:
            castedvotes[f"{interaction.user.id}"] = poll_options.values[0]
        except IndexError:
            await interaction.response.defer()
        await interaction.response.send_message("Vote updated!", ephemeral=True)

    async def poll_end_callback(interaction):
        if interaction.user == ctx.author:
            option_list = list(args_list)
            count_list = castedvotes.values()
            counted_dict = Counter(count_list)
            prepared_poll = ""
            try:
                winning = \
                    list({_i for _i in counted_dict.keys() if counted_dict[_i] == max(set(counted_dict.values()))})[0]
            except IndexError:
                winning = "None."
                prepared_poll = "No votes."

            tie = len(set(counted_dict.values()))

            if tie == 1:
                if len(counted_dict) > 1:  # Check if there are multiple options.
                    winning = "Tie!"
            elif len(counted_dict) != tie:  # Check if they are not tie.
                if list(counted_dict.values()).count(
                        max(set(counted_dict.values()))) > 1:  # Check for tie-winning options.
                    winning = f"Tie - {', '.join({_i for _i in counted_dict.keys() if counted_dict[_i] == max(set(counted_dict.values()))})}"

            j_count = 0
            counted_dict_copy = copy.copy(counted_dict)

            for j in counted_dict_copy.keys():
                counted_dict[str(j)] = counted_dict[option_list[j_count]]
                del counted_dict[str(j)]
                j_count += 1

            if prepared_poll != "No votes.":
                prepared_poll = "**" + str(counted_dict_copy).replace('Counter(', '').replace(')', '').replace('{',
                                                                                                               '').replace(
                    '}', '').replace('\'', '').replace(", ", "\n**").replace(":", ":**")

            poll_new_embed = discord.Embed(
                title=f"POLL: \"{name}\" - Results",
                description=f"**Winning Vote: {winning}**\n\n{prepared_poll}",
                color=discord.Colour.green()
            )
            poll_view.on_timeout = None
            await interaction.response.send_message(content=f"{ctx.author.mention}, your poll results are out:",
                                                    view=None, embed=poll_new_embed)
            await interaction.message.delete()
        elif interaction.user != ctx.author:
            await interaction.response.send_message("This poll isn't created by you!", ephemeral=True)

    async def poll_timeout():
        option_list = list(args_list)
        count_list = castedvotes.values()
        counted_dict = Counter(count_list)
        prepared_poll = ""
        try:
            winning = list({_i for _i in counted_dict.keys() if counted_dict[_i] == max(set(counted_dict.values()))})
        except ValueError:
            winning = "None."
            prepared_poll = "No votes."

        tie = len(set(counted_dict.values()))

        if tie == 1:
            if len(counted_dict) > 1:  # Check if there are multiple options.
                winning = "Tie!"
        elif len(counted_dict) != tie:  # Check if they are not tie.
            if list(counted_dict.values()).count(max(set(counted_dict.values()))) > 1:  # Check for tie-winning options.
                winning = f"Tie - {', '.join({_i for _i in counted_dict.keys() if counted_dict[_i] == max(set(counted_dict.values()))})}"

        j_count = 0
        counted_dict_copy = copy.copy(counted_dict)

        for j in counted_dict_copy.keys():
            counted_dict[str(j)] = counted_dict[option_list[j_count]]
            del counted_dict[str(j)]
            j_count += 1

        if prepared_poll != "No votes.":
            prepared_poll = "**" + str(counted_dict_copy).replace('Counter(', '').replace(')', '').replace('{',
                                                                                                           '').replace(
                '}', '').replace('\'', '').replace(", ", "\n**").replace(":", ":**")

        poll_new_embed = discord.Embed(
            title=f"POLL: \"{name}\" - Results",
            description=f"**Winning Vote: {winning}**\n\n{prepared_poll}",
            color=discord.Colour.green()
        )
        poll_view.clear_items()
        await ctx.reply(content=f"{ctx.author.mention}, your poll results are out:", embed=poll_new_embed, view=None)
        await msg.delete()

    poll_options.callback = poll_select_callback
    poll_vote.callback = poll_vote_callback
    poll_end.callback = poll_end_callback

    poll_view = View(timeout=300)
    poll_view.on_timeout = poll_timeout
    poll_view.add_item(poll_vote)
    poll_view.add_item(poll_options)
    poll_view.add_item(poll_end)

    msg = await ctx.reply(content=None, embed=poll_embed, view=poll_view)


@bot.command(name="8ball")
async def _8ball(ctx, arg: str):
    """___category__Tools___category__
___parameters__
**Quick Note:** Please ask close-ended (yes/no) questions to make the command make sense.

`question` - Your question to ask.___parameters__
___description__Get responses to your questions.___description__
___duplicate__##none##___duplicate__"""
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

    await ctx.reply(content=None, embed=discord.Embed(title="8-ball", description=random.choice(possibleanswers),
                                                      colour=discord.Colour.blurple()).set_footer(text=arg))


@bot.command(name="random")
async def _random(ctx, *numbers):
    """___category__Tools___category__
___parameters__
(You can seperate your numbers with commas.)
`lower` - Your lower limit for the random number.
`upper` - Your upper limit for the random number.___parameters__
___description__Generate a random number.___description__
___duplicate__##none##___duplicate__"""
    numbers = [int(i.replace(" ", "")) for i in
               (" ".join(numbers).split(",") if len(" ".join(numbers).split(",")) > 1 else numbers)]
    embed = discord.Embed(title="CRIME.NET/Random Number Generator", colour=discord.Colour.blurple())
    embed.add_field(name="Result", value=baintools.format_number(random.randint(*numbers)), inline=False)
    embed.set_footer(
        text=f"Lower limit: {baintools.format_number(numbers[0])}; Upper limit: {baintools.format_number(numbers[1])}\nProcessing ID: {baintools.generate_transaction_id(10)}")
    await ctx.reply(content=None, embed=embed)


# Trolling
@bot.command()
async def nitro(ctx):
    """___category__General___category__
___parameters__None.___parameters__
___description__Generates a fake Nitro claim embed.___description__
___duplicate__##none##___duplicate__"""
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
    """___category__General___category__
___parameters__`user (optional)` - The user you want to tell "try it and see".___parameters__
___description__Tell someone to try it and see.___description__
___duplicate__##none##___duplicate__"""
    if user is None:
        user = ctx.author
    try:
        await ctx.message.reference.cached_message.reply(content=f"From {ctx.author},\nhttps://tryitands.ee")
    except Exception:
        await ctx.reply(content=f"{user.mention}, from {ctx.author},\nhttps://tryitands.ee")
    finally:
        await ctx.message.delete()


@bot.command()
async def kill(ctx, *, arg: str):
    """___category__General___category__
___parameters__`user` - The user to kill (verbally).___parameters__
___description__Kills a user (verbally).___description__
___duplicate__##none##___duplicate__"""
    if arg == "me" or arg == ctx.author.mention:
        await ctx.send(f"You've committed suicide. Welcome to The Bad Place.")
    elif arg.lower() in ["bain", pr_secrets.bain_id, f"<@{pr_secrets.bain_id}>"]:
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
            await ctx.send(
                f"<:glock_17:966176633398644757> {ctx.message.author.mention} killed {arg} with {quotenumber}")


@bot.command()
async def hack(ctx, user: discord.Member):
    """___category__General___category__
___parameters__`user` - The user to hack.___parameters__
___description__Hacks a user.___description__
___duplicate__##none##___duplicate__"""
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
        if interaction.user == ctx.author and user.mention != pr_secrets.owner_id and user.mention != pr_secrets.bain_id:
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
            balance = baintools.format_number(random.randint(-1000, 100000))
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
        elif interaction.user == ctx.author and user.mention == pr_secrets.owner_id:
            await interaction.response.edit_message(content="``Couldn't hack him. Perhaps try someone else?``",
                                                    embed=None, view=None)
        elif interaction.user == ctx.author and user.mention == pr_secrets.bain_id:
            await interaction.response.edit_message(content="``Couldn't hack him. Perhaps try someone else?``",
                                                    embed=None, view=None)
        elif interaction.user != ctx.author:
            await interaction.response.send_message("This hack isn't for you!", ephemeral=True)

    async def hack_id_callback(interaction):
        if interaction.user == ctx.author and user.mention != pr_secrets.owner_id and user.mention != pr_secrets.bain_id:
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
        elif interaction.user == ctx.author and user.mention == pr_secrets.owner_id:
            await interaction.response.edit_message(content="``Couldn't hack him. Perhaps try someone else?``",
                                                    embed=None, view=None)
        elif interaction.user == ctx.author and user.mention == pr_secrets.bain_id:
            await interaction.response.edit_message(content="``Couldn't hack him. Perhaps try someone else?``",
                                                    embed=None, view=None)
        elif interaction.user != ctx.author:
            await interaction.response.send_message("This hack isn't for you!", ephemeral=True)

    async def hack_pc_callback(interaction):
        if interaction.user == ctx.author and user.mention != pr_secrets.owner_id and user.mention != pr_secrets.bain_id:
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






        elif interaction.user == ctx.author and user.mention == pr_secrets.owner_id:
            await interaction.response.edit_message(content="``Couldn't hack him. Perhaps try someone else?``",
                                                    embed=None, view=None)
        elif interaction.user == ctx.author and user.mention == pr_secrets.bain_id:
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
    """___category__General___category__
___parameters__**Quick Note:** The rickroll will be sent to everyone. Specifying who to rickroll will ping them in the message sent.

`user (optional)` - The user to rickroll.___parameters__
___description__Rickrolls a user (and whoever that sees it).___description__
___duplicate__##none##___duplicate__"""
    if user is None:
        user = ctx.author
    embed = discord.Embed(title=":)",
                          description=f"You have been rolled by {ctx.author.mention}. You cannot delete this message... Teehee!",
                          colour=discord.Color.blurple())
    embed.set_image(url="https://media.tenor.com/_4YgA77ExHEAAAAd/rick-roll.gif")

    await ctx.reply(content=f"{user.mention}:" if user != ctx.author else None, embed=embed)
    await ctx.message.delete()


# Voice
@bot.command()
async def join(ctx):
    """___category__Voice___category__
___parameters__**Quick Note:** The bot can only join one voice channel per server.___parameters__
___description__Joins the voice channel you are connected to.___description__
___duplicate__##none##___duplicate__"""
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
async def leave(ctx):
    """___category__Voice___category__
___parameters__None.___parameters__
___description__Leaves whichever voice channel Bain is connected to.___description__
___duplicate__##none##___duplicate__"""
    try:
        await ctx.guild.voice_client.disconnect()
    except Exception:
        await ctx.reply("Error. Most likely that I had not been in a voice channel in the first place.")


@bot.command()
@commands.has_permissions(moderate_members=True)
async def disconnect(ctx, user: discord.Member, reason=None):
    """___category__Voice___category__
___parameters__`user` - The user to disconnect.

`reason` - *Optional.* The reason for disconnecting the user, shown in the audit log.___parameters__
___description__Disconnects a user from a voice channel.___description__
___duplicate__##none##___duplicate__"""
    try:
        if ctx.author.top_role > user.top_role:
            # noinspection PyTypeChecker
            await user.move_to(channel=None, reason=reason)
            await ctx.reply(f"Disconnected {user}.")
        else:
            await ctx.reply("You can only disconnect users lower than your highest role.")
    except Exception:
        await ctx.reply("An error occured.")


@bot.command()
async def stop(ctx):
    """___category__Voice___category__
___parameters__None.___parameters__
___description__Leaves whichever voice channel Bain is connected to.___description__
___duplicate__leave___duplicate"""
    await ctx.invoke(leave)


@bot.command()
async def play(ctx: commands.Context, *, song: str):
    """___category__Voice___category__
___parameters__**Note:** You can only play songs available on Spotify. You can enter a song name and Bain will search for you, or enter the Spotify URL directly.

`song` - The song you would like to play.___parameters__
___description__Plays a song in your voice channel.___description__
___duplicate__##none##___duplicate__"""
    if song.startswith("https://open.spotify.com/album"):
        await ctx.reply("You can only play songs, not albums for now. (Skill issue.)")
        return
    origin_msg = await ctx.reply("`Initializing...`")
    try:
        if ctx.author.voice.channel is None:
            raise ValueError("'NoneType' object has no attribute 'channel'")
    except Exception as e:
        if str(e) == "'NoneType' object has no attribute 'channel'":
            await origin_msg.delete()
            await ctx.reply(content=None, embed=discord.Embed(title="Audio Player: Error",
                                                              description="You are not connected to a voice channel.",
                                                              colour=discord.Color.red()))
    else:
        async with ctx.typing():
            await origin_msg.edit(content="`Updating path...`")
            spotify_link = song
            log_file = open("_Music/#log.txt", "w")
            list_of_files = os.listdir("_Music")
            for i in list_of_files:
                if i.startswith(str(ctx.author.guild.id)):
                    try:
                        os.remove(pr_secrets.os_dir_music + "\\" + i)
                    except PermissionError:
                        pass
        async with ctx.typing():
            await origin_msg.edit(content="`Downloading song...`")
            subprocess.Popen(
                f"{sys.executable} {spotdl.__main__.__file__} download \"{spotify_link}\" --output \"{pr_secrets.os_dir_music}\\{ctx.author.guild.id}{'___{artists} - {title}.{output-ext}'}\" --overwrite force",
                stdout=log_file, stderr=log_file, shell=True)
            time = 0
            while True:
                await asyncio.sleep(1)
                time += 1
                try:
                    file = [i for i in os.listdir(pr_secrets.os_dir_music) if i.startswith(str(ctx.author.guild.id))][0]
                except IndexError:
                    if time >= 60:
                        await throw_crimenet_error(ctx, 400,
                                                   "`**TIMEOUT** - `Download failed - likely because of a lookup error: Spotify couldn't find your song.")
                        return
                    else:
                        continue
                else:
                    break
            source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(f"{pr_secrets.os_dir_music}\\{file}"))
            channel = ctx.author.voice.channel
        try:
            async with ctx.typing():
                await origin_msg.edit(content="`Connecting...`")
                connection = await channel.connect()
        except discord.errors.ClientException:
            await origin_msg.delete()
            await ctx.reply(content=None, embed=discord.Embed(title="Audio Player: Error",
                                                              description="Audio is already playing in a voice channel.",
                                                              colour=discord.Color.red()))
        else:
            async with ctx.typing():
                connection.play(source)

            await origin_msg.delete()
            await ctx.reply(content=None, embed=discord.Embed(title="Audio Player",
                                                              description=f"Now playing: **{[i for i in os.listdir(pr_secrets.os_dir_music) if i.startswith(str(ctx.author.guild.id))][0].split(str(ctx.author.guild.id) + '___')[1].replace('.mp3', '')}**",
                                                              colour=discord.Color.blurple()))


# Owner-only.
@bot.command()
@commands.is_owner()
async def _status(ctx):
    await ctx.reply(f"Online! Running.")


@bot.command()
@commands.is_owner()
async def _logout(ctx: commands.Context):
    print(f"Terminating program in {ctx.guild.name} <{datetime.datetime.now()}>...")
    await ctx.send(f"`Program terminated by {ctx.author.mention} at {datetime.datetime.now()}.`")
    try:
        await ctx.bot.close()
    except Exception as e:
        print(f"An error occurred.\n{e}")
        return


@bot.command(name="_geninv")
@commands.is_owner()
async def _gen_inv(ctx, id: int):
    if id is None:
        id = ctx.guild.id
    await ctx.message.delete()
    guild = bot.get_guild(id)
    user = ctx.author

    name = guild.name
    owner = guild.owner
    member_count = guild.approximate_member_count
    online_count = guild.approximate_presence_count
    channel = await guild.text_channels[0].create_invite(max_age=0, max_uses=1, temporary=False, unique=False)

    embed = discord.Embed(title=f"Invite Link for {name}")
    embed.add_field(name="Owner", value=f"{owner} (ID: {owner.id})", inline=False)
    embed.add_field(name="No. of members", value=f"{member_count}", inline=False)
    embed.add_field(name="No. of **online** members", value=f"```diff\n{online_count}\n```", inline=False)

    dm = await user.create_dm()
    await dm.send(content=f"{str(channel.url)}", embed=embed)


@bot.command(name="_emoji_id")
@commands.is_owner()
async def _emoji_id(ctx, emoji: discord.Emoji):
    await ctx.reply(
        f"**Emoji Information**\nEmoji: <:{emoji.name}:{emoji.id}>\nEmoji name: `{emoji.name}`\nEmoji ID: `{emoji.id}`\nEmoji Qualname: `:{emoji.name}:{emoji.id}`\nEmoji Qualified Syntax: `<:{emoji.name}:{emoji.id}>`")


@bot.command(name="_pyver")
@commands.is_owner()
async def _pyver(ctx):
    embed = discord.Embed(title="Version Info", colour=discord.Colour.blurple()).add_field(name="Pycord Version",
                                                                                           value=discord.__version__,
                                                                                           inline=False).add_field(
        name="Pycord Release Level",
        value=f"Major: {discord.version_info.major}\nMinor: {discord.version_info.minor}\nMicro: {discord.version_info.micro}\nRelease Level: `{discord.version_info.release_level}`\nSerial: `{discord.version_info.serial}`\nBuild: {discord.version_info.build}\nCommit: `{discord.version_info.commit}`\nDate: {discord.version_info.date}",
        inline=False).add_field(name="Python version", value=sys.version, inline=False).set_thumbnail(
        url="https://www.python.org/static/img/python-logo@2x.png")
    await ctx.reply(content=None, embed=embed)


@bot.slash_command(name="refresh", description="Refreshes the limit for Discord's ADB.", guilds=[pr_secrets.gifted_fireplace_id])
async def _refresh(ctx: discord.ApplicationContext):
    if ctx.author.id == pr_secrets.owner_id:
        try:
            await ctx.respond(content="Done!")
        except discord.NotFound:
            await ctx.response.defer()
    else:
        await ctx.response.defer()


# Function dependencies.
# .define command
async def dictsearch(arg):
    async with aiohttp.ClientSession() as session:
        word_id = arg.lower()
        url = "https://api.dictionaryapi.dev/api/v2/entries/en/" + word_id.lower()
        async with session.get(url) as res:
            r = await res.text()
            return r


# .wiki command
def wikisummary(arg):
    definition = wikipedia.summary(arg, sentences=3, chars=1000)
    url = wikipedia.page(arg, redirect=True).url
    search_keyword = wikipedia.page(arg, redirect=True).title
    return definition, url, search_keyword


# Error presets.
async def throw_crimenet_error(ctx: commands.Context, error_code: int, message: str):
    error_dict = {
        400: "Bad request. Try passing some valid arguments, yes?",
        404: "Not found. Try using some valid commands, yes?"
    }
    embed = discord.Embed(title=f"CRIME.NET/Error/{error_code}", description=f"{error_dict[error_code]}\n`{message}`", colour=discord.Colour.red())
    await ctx.reply(message=None, embed=embed)


bot.run(pr_secrets.discord_bot_token)
print(f"Program terminated at {datetime.datetime.now()}")
