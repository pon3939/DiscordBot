#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
共通関数
"""

import CommonConstants
from codecs import open
from configparser import ConfigParser
from googleapiclient.discovery import build
from json import dump, load
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
            f = open(self.ini.get(CommonConstants.INI_SECTION_GENERAL, CommonConstants.INI_OPTION_MESSAGE_JSON), "r", CommonConstants.FILE_ENCODING)
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
            with open(self.ini.get(CommonConstants.INI_SECTION_GENERAL, CommonConstants.INI_OPTION_MESSAGE_JSON), "r", CommonConstants.FILE_ENCODING) as f:
                json_data = load(f)
            messageList = json_data[CommonConstants.JSON_MESSAGE_LONELY]

            i = 0
            for message in messageList:
                if rtn != "":
                    rtn += "\n" # 2件目以降は改行
                rtn += str(i) + ":" + message
                i += 1
            return rtn
        except Exception as e:
            print("getLonelyList:例外発生")
            print(e)

    def addLonelyList(self, message):
        """
        独りぼっち通知のメッセージを追加
        """
        try:
            # バリデーション
            if message.find(CommonConstants.LONELY_MESSAGE_NAME) == -1:
                return "テンプレートには" + CommonConstants.LONELY_MESSAGE_NAME + "が含まれる必要があります"
            elif message.find(CommonConstants.LONELY_MESSAGE_CHANNEL) == -1:
                return "テンプレートには" + CommonConstants.LONELY_MESSAGE_CHANNEL + "が含まれる必要があります"

            with open(self.ini.get(CommonConstants.INI_SECTION_GENERAL, CommonConstants.INI_OPTION_MESSAGE_JSON), "r", CommonConstants.FILE_ENCODING) as fIn:
                json_data = load(fIn)
            messageList = json_data[CommonConstants.JSON_MESSAGE_LONELY]
            if message in messageList:
                return "入力されたテンプレートは既に存在します"
            messageList.append(message)
            json_data[CommonConstants.JSON_MESSAGE_LONELY] = messageList
            with open(self.ini.get(CommonConstants.INI_SECTION_GENERAL, CommonConstants.INI_OPTION_MESSAGE_JSON), "w", CommonConstants.FILE_ENCODING) as fOut:
                dump(json_data, fOut) # JSONファイル更新
            return "テンプレート\"" + message + "\"を追加しました"
        except Exception as e:
            print("addLonelyList:例外発生")
            print(e)

    def deleteLonelyList(self, strIndex):
        """
        独りぼっち通知のメッセージを追加
        """
        try:
            # バリデーション
            if not strIndex.isdigit():
                return "数値を指定してください"
            index = int(strIndex) # 整数値に変換
            if index < 0:
                return "0以上の数値を指定してください"

            with open(self.ini.get(CommonConstants.INI_SECTION_GENERAL, CommonConstants.INI_OPTION_MESSAGE_JSON), "r", CommonConstants.FILE_ENCODING) as fIn:
                json_data = load(fIn)
            messageList = json_data[CommonConstants.JSON_MESSAGE_LONELY]
            if len(messageList) <= index:
                return "入力されたインデックスのテンプレートは存在しません"
            delMessage = messageList[index] # チャットに流すためにテンプレートを取得
            messageList.pop(index)
            json_data[CommonConstants.JSON_MESSAGE_LONELY] = messageList
            with open(self.ini.get(CommonConstants.INI_SECTION_GENERAL, CommonConstants.INI_OPTION_MESSAGE_JSON), "w", CommonConstants.FILE_ENCODING) as fOut:
                dump(json_data, fOut) # JSONファイル更新
            return "テンプレート\"" + delMessage +  "\"を削除しました"
        except Exception as e:
            print("deleteLonelyList:例外発生")
            print(e)
