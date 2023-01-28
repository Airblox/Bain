import json
import os
import discord
import datetime
import traceback
import sys

from keep_alive import keep_alive
from discord.ext import commands


with open("ServerSupport/rep_secrets.json") as rep:
    rep_secrets: dict = json.load(rep)

bot = commands.Bot(command_prefix="_",
                   intents=discord.Intents.all(),
                   owner_id=rep_secrets['owner_id'],
                   auto_sync_commands=True)
bot.remove_command("help")


@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game(name="CRIME.NET"))
    guild_count = 0
    print(f">>> Server info <{datetime.datetime.now()}>")
    for guild in bot.guilds:
        print(f"- {guild.name} ({guild.owner}, {guild.id}).")
        guild_count = guild_count + 1

    print(
        f"(In {guild_count} servers in total.)\n\nAK17-EVA is online. Terminate the program to get it offline."
    )


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
            await ctx.author.send(
                f'{ctx.command} can not be used in Private Messages.')
        except discord.HTTPException:
            pass

    elif isinstance(error, commands.BadArgument):
        await ctx.reply(f'Bad argument passed for {ctx.command}')

    elif isinstance(error, commands.MissingPermissions):
        await ctx.reply(
            f'Sorry - you do not have the permissions for using {ctx.command}.')

    elif isinstance(error, discord.errors.Forbidden):
        await ctx.reply(content=f"Sorry - `{error}`")

    elif isinstance(error, commands.NotOwner):
        await ctx.reply("Sorry - you are not the owner of this bot.")

    elif isinstance(error, discord.errors.NotFound):
        pass

    else:
        print(f"Error time: {datetime.datetime.now()}\n" +
              'Ignoring exception in command {}:'.format(ctx.command),
              file=sys.stderr)
        await ctx.reply("`An error occurred!`")
        traceback.print_exception(type(error),
                                  error,
                                  error.__traceback__,
                                  file=sys.stderr)


@bot.command(name="setup")
async def setup(ctx: commands.Context, _id: discord.TextChannel):
    print("Server setup message sent.")
    file = discord.File("ServerSupport/AK17-EVA.png")
    context = """**Welcome to Bain's community and support server! Please read the rules to continue.**

**#1** - Please use common. No spam, no racism, be respectful, etc.
**#2** - If the moderators/administrators call you out for your behavior, you're clearly doing something wrong. Behave, or you will be kicked or banned.
**#3** - Be respectful. Toxic behavior is NOT allowed here. Friendly ones, as long as both parties are clearly fine with, are fine, but if you take it too far, or it's clear that it's not friendly between both parties involved, moderators/administrators will take action.
**#4** - No spam. It is not fun.
**#5** - Use the channels for their intended purposes.
**#6** - No racism or discrimination of any kind, as well as slurs.
**#7** - No discussions about politics/religion.
**#8** - No NSFW content. If you want those, go somewhere else for that.
**#9** - Just because something isn't explicitly written in the rules, that doesn't mean that it's allowed. Please use common sense.
**#10** - Do not abuse the ping feature. It is not fun for a person to receive many notifications that have no important content.
**#11** - Do not DM people for advertisement, harassment, insulting, or scamming purposes. If found, please report to the moderators or the administrators.
**#12** - Memes are allowed, but please do not post offensive ones. Please refer to the rules above."""

    class MyView(discord.ui.View):

        def __init__(self):
            super().__init__(timeout=None)

        @discord.ui.button(label="I have read and agreed to the rules.",
                           style=discord.ButtonStyle.primary)
        async def button_callback(self, _, interaction):
            if discord.Object(rep_secrets['role_verified']) not in interaction.user.roles:
                await interaction.user.add_roles(interaction.user.guild.get_role(
                    int(rep_secrets['role_verified'])),
                    reason="Verification.")
                await interaction.response.defer()

    await _id.send(file=file)
    await _id.send(content=context, view=MyView())
    await ctx.message.delete()


keep_alive()

try:
    bot.run(rep_secrets['__token'])
except discord.errors.HTTPException:
    print("\n\n\nBLOCKED BY RATE LIMITS\nRESTARTING NOW\n\n\n")
    os.system('kill 1')
    os.system("python restarter.py")

print("AK17-EVA is now offline.")