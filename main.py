import asyncio
import logging
import os
import urllib.parse as parse
import urllib.request as request
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from enum import Enum

import pretty_errors
import pyrogram
from pyrogram.errors import QueryIdInvalid

logging.getLogger('pyrogram').setLevel(logging.WARNING)
pretty_errors.replace_stderr()
pretty_errors.whitelist(__file__)

API_ID = os.environ["API_ID"]
API_HASH = os.environ["API_HASH"]
BOT_TOKEN = os.environ["BOT_TOKEN"]

bot = pyrogram.Client("yandereBot", API_ID, API_HASH, bot_token=BOT_TOKEN)

xdict = {}
ydict = {}


class Rating(Enum):
    Explicit = "e"
    Questionable = "q"
    Safe = "s"


@dataclass
class Post:
    id: str
    preview_url: str
    sample_url: str
    rating: Rating


@bot.on_inline_query()
async def _(client: pyrogram.client.Client,
            query: pyrogram.types.inline_mode.inline_query.InlineQuery):
    user_id = str(query.from_user.id)

    if user_id in xdict:
        query.offset = xdict[user_id].offset
        xdict[user_id] = query
        return
    else:
        xdict[user_id] = query
        await asyncio.sleep(3)
        query = xdict[user_id]
        tags = parse.quote(query.query)
        next_offset = str(float(query.offset or 1)+0.5)

        if not tags:
            del xdict[user_id]
            return

        # delete previous requests with other tags
        for x in list(ydict):
            x: str
            if x.startswith(user_id) and not x.startswith(user_id + tags):
                del ydict[x]

        if user_id+tags in ydict:
            resp_list = ydict[user_id+tags]
            del ydict[user_id+tags]
        else:
            page = 1 if not query.offset else int(float(query.offset))
            posts = make_request(page, tags)
            resp_list = []
            ext_list = []
            count = 0
            for post in posts:
                count += 1
                if count <= 50:
                    resp_list.append(create_result_photo(query, post))
                else:
                    ext_list.append(create_result_photo(query, post))
            if ext_list:
                ydict[user_id+tags] = ext_list

        if len(resp_list) < 50:
            next_offset = ""
        print("len resp_list:", len(resp_list))
        print("next offset:", next_offset)
        try:
            await client.answer_inline_query(query.id,
                                             results=resp_list,
                                             cache_time=900,  # 15 minutes cache
                                             next_offset=next_offset,
                                             is_gallery=True)
        except QueryIdInvalid:
            pass
        finally:
            del xdict[user_id]
            if float(next_offset or 0) % 1 > 0:
                print("------------")
            else:
                print("----------------------")


def make_request(page, tags):
    limit = 100
    url: str = f"https://www.yande.re/post.xml/?limit={limit}&page={page}&tags={tags}"
    print(url)
    xml: ET.Element = ET.fromstring(
        request.urlopen(url).read().decode('utf-8'))
    posts = xml.findall("post")
    if not posts:
        return None
    for post in posts:
        yield Post(post.attrib["id"], post.attrib["preview_url"], post.attrib["sample_url"],
                   Rating(post.attrib["rating"]))


def create_result_photo(query, post: Post):
    link_url: str = f"https://yande.re/post/show/{post.id}"
    rating_btn = pyrogram.types.InlineKeyboardButton(
        post.rating.name, callback_data="0_0")
    post_link_btn = pyrogram.types.InlineKeyboardButton(
        "🔗", url=link_url)
    resend_btn = pyrogram.types.InlineKeyboardButton(
        "🔄", switch_inline_query_current_chat=query.query)
    keyboard = pyrogram.types.InlineKeyboardMarkup(
        [[rating_btn, post_link_btn, resend_btn]])

    return pyrogram.types.InlineQueryResultPhoto(
        photo_url=post.sample_url,
        thumb_url=post.preview_url,
        reply_markup=keyboard)


@bot.on_callback_query()
async def _(
        client: pyrogram.client.Client,
        query: pyrogram.types.bots_and_keyboards.callback_query.CallbackQuery):
    # 7 days cache
    await client.answer_callback_query(query.id, cache_time=604800)


if __name__ == "__main__":
    print("Bot running...")
    try:
        bot.run()
    finally:
        print("\nBot stopped...")
