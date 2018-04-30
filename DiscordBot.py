#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
DiscordのBOT
"""

import click
import CommonConstants
import discord
from asyncio import ensure_future, get_event_loop
from CommonFunction import CommonFunction, getMyLogger
from configparser import ConfigParser

client = discord.Client()
ini = ConfigParser()
logger = None
commonFunction = None

@client.event
async def on_ready():
    """
    BOT起動時の処理
    """
    try:
        # 定期実行処理を非同期で開始(discord.py側で非同期処理開始しているため、非同期処理を追加するだけでOK)
        logger.info("BOT起動")
        ensure_future(commonFunction.asyncDeleteLog())
    except Exception as e:
        logger.error("on_ready:例外発生")
        logger.error(e)

@client.event
async def on_message(message):
    """
    メッセージ受信時の処理

    :param discord.Message message: 受信したメッセージ
    """
    try:
        if client.user != message.author:
            # 送り主が自分意外
            if client.user in message.mentions:
                # 自分宛てのメンション
                rtn = ""
                content = message.content.replace(client.user.mention, "").strip() # メンション部分と空白を削除
                if content.startswith("おはよう"):
                    # おはようで始まる
                    rtn = "おはようございます" + message.author.name + "さん！"
                elif content.startswith("google search "):
                    # gogle searchで始まる
                    rtn = commonFunction.search(content.replace("gogle search ", ""))
                elif content.startswith("lonely list"):
                    # 独りぼっち通知のリストを表示
                    rtn = commonFunction.getLonelyList()
                elif content.startswith("lonely add "):
                    # 独りぼっち通知のリストに追加
                    rtn = commonFunction.addLonelyList(content.replace("lonely add ", ""))
                elif content.startswith("lonely delete "):
                    # 独りぼっち通知のリストから削除
                    rtn = commonFunction.deleteLonelyList(content.replace("lonely delete ", ""))
                elif content.startswith("readme"):
                    # readmeを表示
                    rtn = commonFunction.getReadme()
                else:
                    # 対応していないメッセージだと通知
                    rtn = "何を言っているかわからないよ:sweat_smile:\n" \
                        "***" + client.user.mention + " readme*** を確認してね:exclamation:"

                if rtn != "":
                    # メッセージが送られてきたチャンネルへメッセージを送る
                    await client.send_message(message.channel, rtn)
    except Exception as e:
        print("on_message:例外発生")
        print(e)

@client.event
async def on_voice_state_update(before, after):
    """
    誰かがボイスチャンネルの状態を変更した時の処理

    :param discord.Member before: 移動前のユーザの情報
    :param discord.Member after: 移動後のユーザの情報
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

    :param str ini_path: INIファイルのパス
    """
    try:
        global logger, commonFunction

        # iniファイル、ロガーの設定
        ini.read(ini_path, "utf-8")
        logger = getMyLogger(ini.get(CommonConstants.INI_SECTION_GENERAL, CommonConstants.INI_OPTION_EXEC_DIR) + "logging.conf", __name__)
        commonFunction = CommonFunction(ini, logger)
        client.run(ini.get(CommonConstants.INI_SECTION_GENERAL, CommonConstants.INI_OPTION_TOKEN))
    except Exception as e:
        print("main:例外発生")
        print(e)

if __name__ == '__main__':
    main()
