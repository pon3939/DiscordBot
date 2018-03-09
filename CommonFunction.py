#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
共通関数
"""

import CommonConstants
from configparser import ConfigParser
from googleapiclient.discovery import build
from json import load
from random import randint

class CommonFunction:
    def __init__(self, ini = None):
        """
        コンストラクタ
        """
        try:
            self.ini = ini
        except Exception as e:
            print("__init__:例外発生")
            print(e)

    def search(self, searchWord):
        """
        googleで検索
        """
        try:
            service = build("customsearch", "v1", developerKey = self.ini.get(CommonConstants.INI_SECTION_GOOGLE, CommonConstants.INI_OPTION_API_KEY))
            # 取得する画像のインデックス
            start = randint(1, 50)

            # 失敗時は何回かリトライ
            for i in range(3):
                try:
                    result = service.cse().list(
                        q = searchWord,
                        cx = self.ini.get(CommonConstants.INI_SECTION_GOOGLE, CommonConstants.INI_OPTION_ENGINE_KEY),
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

    def getLonelyMassage(self, name, channel):
        """
        独りぼっち通知のメッセージの一覧から、ランダムに選択したものを取得
        """
        try:
            f = open(self.ini.get(CommonConstants.INI_SECTION_GENERAL, CommonConstants.INI_OPTION_MESSAGE_JSON), "r")
            json_data = load(f)
            messageList = json_data[CommonConstants.JSON_MESSAGE_LONELY]
            message = messageList[randint(0, len(messageList) - 1)] # ランダムにメッセージを選択
            return message.replace(CommonConstants.LONELY_MESSAGE_NAME, name).replace(CommonConstants.LONELY_MESSAGE_CHANNEL, channel) # ユーザ名、チャンネル名を置換
        except Exception as e:
            print("getLonelyMassage:例外発生")
            print(e)

    def getLonelyList(self):
        """
        独りぼっち通知のメッセージの一覧を取得
        """
        try:
            rtn = ""
            f = open(self.ini.get(CommonConstants.INI_SECTION_GENERAL, CommonConstants.INI_OPTION_MESSAGE_JSON), "r")
            json_data = load(f)
            messageList = json_data[CommonConstants.JSON_MESSAGE_LONELY]
            for message in messageList:
                if rtn != "":
                    rtn += "\n" # 2件目以降は改行
                rtn += message
            return rtn
        except Exception as e:
            print("getLonelyList:例外発生")
            print(e)
