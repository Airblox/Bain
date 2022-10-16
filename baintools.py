import time
import random
import string
import discord
import json
from discord.ui import View, Button, Select
from discord import SelectOption
from re import sub


def snake_case(s):
    return '_'.join(
        sub('([A-Z][a-z]+)', r' \1',
            sub('([A-Z]+)', r' \1',
                s.replace('-', ' '))).split()).lower()

def split_page(_t, _i):
    res = []
    cur_res = []
    while len(_t):
        for item, count in zip(_t, range(_i)):
            cur_res.append(item)
        _t = _t[_i:]
        res.append(cur_res)
        cur_res = []
    return res

def to_roman(number: int):
    result = ""
    remainder = number
    guide = {1000: "M", 900: "CM", 500: "D", 400: "CD", 100: "C", 90: "XC", 50: "L", 40: "XL", 10: "X", 9: "IX", 5: "V",
             4: "IV", 1: "I"}

    for index, (i, v) in enumerate(guide.items()):
        q, r = divmod(remainder, i)
        remainder = r
        result += "".join([v for i in range(q)])

    return result


def calculate_experience(level: int):
    if 10 < level < 100:
        return ((1.3654321 * ((level - 10) ** 3)) + 4600).__ceil__()
    else:
        levels = {
            0: 900,
            1: 900,
            2: 1250,
            3: 1550,
            4: 1850,
            5: 2200,
            6: 2600,
            7: 3000,
            8: 3500,
            9: 4000,
            10: 4600,
            100: 1000000
        }
        return levels[level]


def calculate_success_rate(data):
    success_heist_amt = data['heist_stat_success']
    failure_heist_amt = data['heist_stat_failure']
    try:
        return str('{:.1f}'.format(success_heist_amt / (success_heist_amt + failure_heist_amt) * 100)) + "%"
    except ZeroDivisionError:
        return "0%"


def generate_transaction_id(length: int = 20):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))


def heist_autocorrect(_contract: str):
    return snake_case(_contract).replace("'", "").replace("í", "i")


async def player_heist_end(*, user_id: str, heist: str, loot: int, success: bool, difficulty: str = "normal"):
    async def player_database():
        with open("mainbank.json") as file:
            _data = json.load(file)
            return _data

    async def player_get_heist_rewards(_heist):
        with open("heist_rewards_database.json") as file:
            if heist is not None:
                return json.load(file)[heist]
            else:
                return json.load(file)

    async def player_save(_data):
        with open("mainbank.json", "w") as file:
            json.dump(_data, file)

    async def player_exp_adjust(_user_id: int):
        _data = await player_database()
        while _data[str(_user_id)]["exp"] >= calculate_experience(_data[str(_user_id)]["reputation"]) and _data[str(_user_id)]["reputation"] < 100:
            _data[str(_user_id)]["exp"] = _data[str(_user_id)]["exp"] - calculate_experience(_data[str(_user_id)]["reputation"])
            _data[str(_user_id)]["reputation"] += 1
        await player_save(_data)

    data = await player_database()
    if success:

        player_heist_rewards = await player_get_heist_rewards(heist)

        for attr, val in player_heist_rewards.items():
            data[str(user_id)][attr] += val
        data[str(user_id)]["cash"] += ((loot * (difficulty_scaling[difficulty])) * 0.2).__floor__()
        data[str(user_id)]["offshore"] += ((loot * (difficulty_scaling[difficulty])) * 0.8).__floor__()
        data[str(user_id)]["heist_stat_success"] += 1
        while data[str(user_id)]["exp"] >= calculate_experience(data[str(user_id)]["reputation"]) and \
                data[str(user_id)]["reputation"] < 100:
            data[str(user_id)]["exp"] = data[str(user_id)]["exp"] - calculate_experience(
                data[str(user_id)]["reputation"])
            data[str(user_id)]["reputation"] += 1
        await player_save(data)
    else:
        data[str(user_id)]["heist_stat_failure"] += 1
        while data[str(user_id)]["exp"] >= calculate_experience(data[str(user_id)]["reputation"]) and \
                data[str(user_id)]["reputation"] < 100:
            data[str(user_id)]["exp"] = data[str(user_id)]["exp"] - calculate_experience(
                data[str(user_id)]["reputation"])
            data[str(user_id)]["reputation"] += 1
        await player_save(data)

difficulty_scaling = {
    "normal": float(1),
    "hard": 1.5,
    "very hard": float(2),
    "overkill": 2.5,
    "mayhem": float(3),
    "death wish": 4.5,
    "death sentence": 5.5
}
emojis = {
    "diff_skull": "<:diff_skull:1029041261107236904>",
    "diff_mayhem": "<:mayhem_skull:1029041319638732813>",
    "diff_death_wish": "<:dw_skull:1029041359618834442>",
    "diff_death_sentence": "<:ds_skull:1029041401406685245>",
    "diff_od": "<:one_down:1029041082257899560>"
}
difficulty_select = Select(placeholder="Select a difficulty...", options=[
    SelectOption(label="Normal", emoji=emojis["diff_skull"], value="normal"),
    SelectOption(label="Hard", emoji=emojis["diff_skull"], value="hard"),
    SelectOption(label="Very Hard", emoji=emojis["diff_skull"], value="very hard"),
    SelectOption(label="Overkill", emoji=emojis["diff_skull"], value="overkill"),
    SelectOption(label="Mayhem", emoji=emojis["diff_mayhem"], value="mayhem"),
    SelectOption(label="Death Wish", emoji=emojis["diff_death_wish"], value="death wish"),
    SelectOption(label="Death Sentence", emoji=emojis["diff_death_sentence"], value="death sentence"),
])
difficulty_od_select = Select(placeholder="One Down", options=[
    SelectOption(label="Full Downs", description="You start with 3/4 downs.", emoji=emojis["diff_od"], value="False"),
    SelectOption(label="One Down", description="You start with 1/2 down(s).", emoji=emojis["diff_od"], value="True")
])
difficulty_finish = Button(label="Accept", style=discord.ButtonStyle.blurple)
difficulty_cancel = Button(label="Decline", style=discord.ButtonStyle.red)


class PlayerInfo:
    # Use database store key names as keys in this dictionary.
    player_objects = {
        # Profile
        "cash": 0,
        "offshore": 0,
        "join": time.time().__floor__(),
        "char": "dallas",
        "weapon": "w_amcar",

        # Saves
        "daily": 0,

        # Levels
        "exp": 0,
        "reputation": 0,
        "infamy": 0,

        # Primary Weapons
        "w_amcar": 1,
        "w_ak": 0,
        "w_car4": 0,
        "w_uar": 0,
        "w_ak762": 0,

        # Secondary Weapons
        "w_chimano88": 1,
        "w_crosskill": 0,

        # Heists
        "heist_stat_success": 0,
        "heist_stat_failure": 0
    }
    player_heist_multiplier = {
        "normal": float(1),
        "hard": float(3),
        "very hard": float(6),
        "overkill": float(11),
        "mayhem": float(12.5),
        "death wish": float(14),
        "death sentence": float(15)
    }
    player_heist_difficulty_autocomplete = {
        "n": "normal",
        "normal": "normal",
        "h": "hard",
        "hard": "hard",
        "vh": "very hard",
        "vhard": "very hard",
        "v-hard": "very hard",
        "very hard": "very hard",
        "ovk": "overkill",
        "o": "overkill",
        "overkill": "overkill",
        "mh": "mayhem",
        "m": "mayhem",
        "mayhem": "mayhem",
        "dw": "death wish",
        "d": "death wish",
        "d wish": "death wish",
        "d-wish": "death wish",
        "deathwish": "death wish",
        "death wish": "death wish",
        "ds": "death sentence",
        "d-sentence": "death sentence",
        "d sentence": "death sentence",
        "death sentence": "death sentence"
    }


class PlayerHeist:
    # return [heist success?], [heist name], [rewards.loot], [difficulty]
    async def jewelry_store(self, ctx, difficulty, od):
        class Info:
            def __init__(self):
                self.bags = 0
                self.loot = 0
                self.exp = 0
                self.heist_not_end = True

        rewards = Info()
        embed = discord.Embed(title="Precious Things (Jewelry Store)", description=f"Bain: We'll need {difficulty_scaling[difficulty].__ceil__()+2} bags. Go get it!", colour=discord.Colour.blurple())
        view = View()
        for i in range(difficulty_scaling[difficulty].__ceil__()+2):
            bag = Button(label="Jewelry", style=discord.ButtonStyle.blurple, custom_id=f"jewelry_{i}")

            async def bag_callback(interaction):
                if interaction.user == ctx.author:
                    await interaction.response.defer()
                    rewards.bags += 1
                    rewards.loot += 5000*difficulty_scaling[difficulty]/2
                    rewards.exp += 500*difficulty_scaling[difficulty]/2
                    view.children = view.children[1:]

                    await interaction.followup.edit_message(message_id=interaction.message.id, view=view)

            bag.callback = bag_callback
            view.add_item(bag)

        escape = Button(label="ESCAPE!", style=discord.ButtonStyle.green)

        async def escape_callback(interaction):
            if interaction.user == ctx.author:
                if rewards.bags >= difficulty_scaling[difficulty].__ceil__()+2:
                    new_embed = discord.Embed(title="Jewelry Store: Success", description=f"**Heist successful!**\n**Your rewards:**\n${'{:,}'.format(rewards.loot)}\n{'{:,}'.format(rewards.exp)} EXP\n\n**Sent to offshore:** ${'{:,}'.format(rewards.loot*0.8.__floor__())}", colour=discord.Colour.green())
                    await interaction.response.edit_message(embed=new_embed, view=None)
                    rewards.heist_not_end = False
                    result = True, "jewelry store", rewards.loot, difficulty

                    if result[0]:  # Fail!
                        await player_heist_end(user_id=ctx.author.id, heist=result[1], loot=result[2],
                                               difficulty=result[3], success=True)
                    elif not result[0]:
                        await player_heist_end(user_id=ctx.author.id, heist=result[1], loot=result[2], success=False,
                                               difficulty=result[3])
                else:
                    new_embed = discord.Embed(title="Jewelry Store: Failed", description="You failed. No money will be paid out, all assets will be locked, and any valuables you held have been confiscated.", colour=discord.Colour.red())
                    await interaction.response.edit_message(content=None, embed=new_embed, view=None)
                    rewards.heist_not_end = False
                    result = False, "jewelry store", rewards.loot, difficulty

                    if result[0]:  # Fail!
                        await player_heist_end(user_id=ctx.author.id, heist=result[1], loot=result[2],
                                               difficulty=result[3], success=True)
                    elif not result[0]:
                        await player_heist_end(user_id=ctx.author.id, heist=result[1], loot=result[2], success=False,
                                               difficulty=result[3])

        escape.callback = escape_callback
        view.add_item(escape)

        await ctx.reply(embed=embed, view=view)


heist_list = [i.replace("_", " ").lower() for i in dir(PlayerHeist()) if not i.startswith("__")]
