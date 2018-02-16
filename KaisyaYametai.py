# -*- coding: utf-8 -*-

import discord

# ---------------------------------------
# DiscordのBOT
# ---------------------------------------

client = discord.Client()

# BOT起動時
@client.event
async def on_ready():
    try:
        print('Logged in as')
        print(client.user.name)
        print(client.user.id)
        print('------')
    except Exceptino as e:
        print("例外発生")
        print(e)

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
            elif message.content.startswith("おやすみ"):
                # おやすみで始まる
                m = "おやすみムーミン" + message.author.name + "さん！"
            elif message.content.startswith("出てこんのかい"):
                # 出てこんのかいで始まる
                m = "ごめんね" + message.author.name + "さん！"
            elif message.content.startswith("ゆるさん"):
                # ゆるさんで始まる
                m = ":poop:"

            if m != "":
                # メッセージが送られてきたチャンネルへメッセージを送る
                await client.send_message(message.channel, m)
    except Exceptino as e:
        print("例外発生")
        print(e)

# 誰かがボイスチャンネルを移動した時
@client.event
async def on_voice_state_update(before, after):
    try:
        if after.voice.voice_channel is not None and len(after.voice.voice_channel.voice_members) == 1:
            # 通話終了でなく、移動後のチャンネルが独りぼっちの場合のみ通知
            for channel in after.server.channels:
                if channel.name == "general" and channel.type == discord.ChannelType.text:
                    # ボイスチャンネルの"general"に通知
                    # nameで判定するのはダサい…
                    # 一人目だけ通知も微妙かも？
                    m = after.display_name + "さんが" + after.voice.voice_channel.name + "で独りぼっちです…"
                    await client.send_message(channel, m)
                    break
    except Exceptino as e:
        print("例外発生")
        print(e)

# BOT起動
client.run("token")
