# -*- coding: utf-8 -*-

import click
import discord

from configparser import ConfigParser
from googleapiclient.discovery import build
from random import randint

# ---------------------------------------
# DiscordのBOT
# ---------------------------------------

# iniファイル関係の定数
INI_SECTION_GENERAL = "general"
INI_OPTION_TOKEN = "token"

INI_SECTION_TEXT_CHANNEL = "textChannel"
INI_OPTION_NAME = "name"

INI_SECTION_GOOGLE = "google"
INI_OPTION_API_KEY = "apiKey"
INI_OPTION_ENGINE_KEY = "engineKey"

client = discord.Client()
config = ConfigParser()

# メッセージ受信時
@client.event
async def on_message(message):
    try:
        if client.user != message.author:
            # 送り主が自分意外のみ反応する
            m = ""
            if message.content.startswith("おはよう"):
                # おはようで始まる
                m = "おはようございます" + message.author.name + "さん！"
            elif message.content.startswith("google search "):
                # gogle searchで始まる
                m = search(message.content.replace("gogle search ", ""))

            if m != "":
                # メッセージが送られてきたチャンネルへメッセージを送る
                await client.send_message(message.channel, m)
    except Exception as e:
        print("on_message:例外発生")
        print(e)

# 誰かがボイスチャンネルを移動した時
@client.event
async def on_voice_state_update(before, after):
    try:
        if after.voice.voice_channel is not None:
            # ボイスチャンネルに参加している
            if before.voice.voice_channel is None or before.voice.voice_channel.id != after.voice.voice_channel.id:
                # beforeとafterが違うチャンネル
                if len(after.voice.voice_channel.voice_members) == 1:
                    # 参加したボイスチャンネルが独りぼっち
                    for channel in after.server.channels:
                        if channel.name == config.get(INI_SECTION_TEXT_CHANNEL, INI_OPTION_NAME) and channel.type == discord.ChannelType.text:
                            # ボイスチャンネルの"general"に通知
                            m = after.display_name + "さんが" + after.voice.voice_channel.name + "で独りぼっちです…"
                            await client.send_message(channel, m)
                            break
    except Exception as e:
        print("on_voice_state_update:例外発生")
        print(e)

# BOT起動
@click.command()
@click.argument("ini", type=str)
def main(ini):
    try:
        # iniファイルを読み込む
        config.read(ini, "utf-8")
        client.run(config.get(INI_SECTION_GENERAL, INI_OPTION_TOKEN))
    except Exception as e:
        print("main:例外発生")
        print(e)

# googleで検索
def search(searchWord):
    try:
        service = build("customsearch", "v1", developerKey = config.get(INI_SECTION_GOOGLE, INI_OPTION_API_KEY))
        # 取得する画像のインデックス
        start = randint(1, 50)

        # 失敗時は何回かリトライ
        for i in range(3):
            try:
                result = service.cse().list(
                    q = searchWord,
                    cx = config.get(INI_SECTION_GOOGLE, INI_OPTION_ENGINE_KEY),
                    lr = "lang_ja",
                    start = start,
                    num = 1,
                    searchType = "image"
                ).execute()
                # 成功時はループを抜ける
                break
            except Exception as e:
                # 失敗時は取得する画像のインデックスを小さくする
                start = randint(1, start - 1)

        if result is None:
            rtn = ""
        else:
            rtn = result.get("items")[0].get("link")
        return rtn
    except Exception as e:
        print("search:例外発生")
        print(e)

if __name__ == '__main__':
    main()
