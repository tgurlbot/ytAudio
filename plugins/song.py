import os
import time
import ffmpeg
import logging
import requests
import youtube_dl
from pyrogram import filters, Client, idle
from youtube_search import YoutubeSearch
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

# Convert hh:mm:ss to seconds
def time_to_seconds(time):
    stringt = str(time)
    return sum(int(x) * 60 ** i for i, x in enumerate(reversed(stringt.split(':'))))


## Commands --------
@Client.on_message(filters.command(['start']))
async def start(client, message):
       await message.reply(f"Hi {message.from_user.mention()} !\nI'm YT Audio Downloader\nSend me any YT link or song name",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton('Search Inline', switch_inline_query_current_chat='')
                ]
            ]
        )
    )
@Client.on_message(filters.command(['about']))
async def about(client, message):
       await message.reply("**📝 Language:** [Python 3](https://www.python.org/)\n\n**📚 Framework:** [Pyrogram](https://github.com/pyrogram/pyrogram)\n\n**📡 Hosted On:** [Heroku](https://heroku.com)", disable_web_page_preview=True, 
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton('Developer', url='https://t.me/FeelDeD')
                ]
            ]
        )
    )
@Client.on_message(filters.text)
def a(client, message):
    query=message.text
    print(query)
    m = message.reply('`Downloading ...`')
    ydl_opts = {"format": "bestaudio[ext=m4a]"}
    try:
        results = []
        count = 0
        while len(results) == 0 and count < 6:
            if count>0:
                time.sleep(1)
            results = YoutubeSearch(query, max_results=1).to_dict()
            count += 1
        # results = YoutubeSearch(query, max_results=1).to_dict()
        try:
            link = f"https://youtube.com{results[0]['url_suffix']}"
            # print(results)
            title = results[0]["title"]
            thumbnail = results[0]["thumbnails"][0]
            duration = results[0]["duration"]

            ## UNCOMMENT THIS IF YOU WANT A LIMIT ON DURATION. CHANGE 1800 TO YOUR OWN PREFFERED DURATION AND EDIT THE MESSAGE (30 minutes cap) LIMIT IN SECONDS
            # if time_to_seconds(duration) >= 1800:  # duration limit
            #     m.edit("Exceeded 30mins cap")
            #     return

            views = results[0]["views"]
            thumb_name = f'thumb{message.message_id}.jpg'
            thumb = requests.get(thumbnail, allow_redirects=True)
            open(thumb_name, 'wb').write(thumb.content)

        except Exception as e:
            print(e)
            m.edit('`Found Nothing. Try change spelling`')
            return
    except Exception as e:
        m.edit(
            "`No result found`"
        )
        print(str(e))
        return
    m.edit("`Uploading ...`")
    try:
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(link, download=False)
            audio_file = ydl.prepare_filename(info_dict)
            ydl.process_info(info_dict)
        rep =  f"**Title:** [{title[:35]}]({link})\n**Duration:** `{duration}`\n**Views:** `{views}`"
        secmul, dur, dur_arr = 1, 0, duration.split(':')
        for i in range(len(dur_arr)-1, -1, -1):
            dur += (int(dur_arr[i]) * secmul)
            secmul *= 60
        message.reply_audio(audio_file, caption=rep,quote=False, title=title, duration=dur, performer=str(info_dict["uploader"]), thumb=thumb_name)
        m.delete()
    except Exception as e:
        m.edit('`Plesase try again later`')
        print(e)
    try:
        os.remove(audio_file)
        os.remove(thumb_name)
    except Exception as e:
        print(e)
