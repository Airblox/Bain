import random
import string
from typing import TypeVar
from re import sub


T = TypeVar("T")


def snake_case(s):
    return '_'.join(
        sub('([A-Z][a-z]+)', r' \1',
            sub('([A-Z]+)', r' \1',
                s.replace('-', ' '))).split()).lower()


def split_page(_t, _i):
    """
    Splits a list into a list of lists.
    :param _t: The list.
    :param _i: The number of items per list.
    :return:
    """
    res = []
    cur_res = []
    while len(_t):
        for item, count in zip(_t, range(_i)):
            cur_res.append(item)
        _t = _t[_i:]
        res.append(cur_res)
        cur_res = []
    return res


def format_number(number: int):
    return "{:,}".format(number)


def generate_transaction_id(length: int = 20):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))


emojis = {
    "diff_skull": "<:diff_skull:1029041261107236904>",
    "diff_mayhem": "<:mayhem_skull:1029041319638732813>",
    "diff_death_wish": "<:dw_skull:1029041359618834442>",
    "diff_death_sentence": "<:ds_skull:1029041401406685245>",
    "diff_od": "<:one_down:1029041082257899560>",

    "category_klas_shovel": "<:klas_shovel:1033590341456109659>",
    "category_icepick": "<:icepick:1033784960622010419>",
    "category_carpenters_delight": "<:carpenters_delight:1033585443603763270>",
    "category_tradecard_bain": "<:tradecard_bain:1033584291990491146>",

    "amcar": "<:amcar:1032610038226890812>",
    "ak": "<:ak:1032610040462454845>",
    "car4": "<:car4:1032610042865778728>",
    "uar": "<:uar:1032610044648357918>",
    "ak762": "<:ak762:1032610046636470302>",
    "jp36": "<:jp36:1048236130904064061>",
    "galant": "<:galant:1048632788691210351>",
    "m308": "<:m308:1048635597905997844>",
    "ak5": "<:ak5:1048636791688806421>",
    "amr16": "<:amr16:1048795631499612271>",
    "tempest21": "<:tempest21:1048796552023527574>",
    "union556": "<:union556:1048837519883649054>",
    "commando553": "<:commando553:1068922952462119015>",
    "eagleheavy": "<:eagleheavy:1068923085547384972>",

    "chimano88": "<:chimano_88:1032610049006239744>",
    "crosskill": "<:crosskill:1032610050717519892>",

    "ketchdev": "<:ketchnovdev:1068928489463500880>"
}
