#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
DiscordのBOT
"""

import click
import CommonConstants
import discord
from CommonFunction import CommonFunction
from configparser import ConfigParser

client = discord.Client()
ini = ConfigParser()
commonFunction = CommonFunction(ini)

@client.event
async def on_message(message):
    """
    メッセージ受信時の処理
    """
    try:
        if client.user != message.author:
            # 送り主が自分意外のみ反応する
            m = ""
            if message.content.startswith("おはよう"):
                # おはようで始まる
                m = "おはようございます" + message.author.name + "さん！"
            elif message.content.startswith("google search "):
                # gogle searchで始まる
                m = commonFunction.search(message.content.replace("gogle search ", ""))
            elif message.content.startswith("lonely list"):
                # 独りぼっち通知のリストを表示
                m = commonFunction.getLonelyList()

            if m != "":
                # メッセージが送られてきたチャンネルへメッセージを送る
                await client.send_message(message.channel, m)
    except Exception as e:
        print("on_message:例外発生")
        print(e)

@client.event
async def on_voice_state_update(before, after):
    """
    誰かがボイスチャンネルを移動した時の処理
    """
    try:
        if after.voice.voice_channel is not None:
            # ボイスチャンネルに参加している
            if before.voice.voice_channel is None or before.voice.voice_channel.id != after.voice.voice_channel.id:
                # beforeとafterが違うチャンネル
                if len(after.voice.voice_channel.voice_members) == 1:
                    # 参加したボイスチャンネルが独りぼっち
                    for channel in after.server.channels:
                        if channel.name == ini.get(CommonConstants.INI_SECTION_TEXT_CHANNEL, CommonConstants.INI_OPTION_NAME) and channel.type == discord.ChannelType.text:
                            # ボイスチャンネルの"general"に通知
                            m = commonFunction.getLonelyMassage(after.display_name, after.voice.voice_channel.name)
                            await client.send_message(channel, m)
                            break
    except Exception as e:
        print("on_voice_state_update:例外発生")
        print(e)

@click.command()
@click.argument("ini_path", type=str)
def main(ini_path):
    """
    メイン処理
    """
    try:
        # iniファイルを読み込む
        ini.read(ini_path, "utf-8")
        client.run(ini.get(CommonConstants.INI_SECTION_GENERAL, CommonConstants.INI_OPTION_TOKEN))
    except Exception as e:
        print("main:例外発生")
        print(e)

if __name__ == '__main__':
    main()
