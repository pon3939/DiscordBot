#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
共通関数
"""

import CommonConstants
from asyncio import sleep
from base64 import b64decode
from codecs import open
from configparser import ConfigParser
from googleapiclient.discovery import build
from json import dump, load
from random import randint
from re import match, sub
from requests import get
from logging import getLogger
from logging.config import fileConfig
from pathlib import Path

def getMyLogger(confFile, loggerName):
    """
    ロガー取得処理

    :param str confFile: ログ設定ファイルパス
    :param str loggerName: ロガー名
    :return: ロガー
    """
    try:
        fileConfig(confFile)
        rtn = getLogger(loggerName)
        return(rtn)
    except Exception as e:
        print("GetMyLogger:例外発生")
        print(e)
        return None

class CommonFunction:
    """
    共通関数クラス
    """

    def __init__(self, ini, logger):
        """
        コンストラクタ

        :param configparser.ConfigParser ini: INIファイル
        """
        try:
            self.ini = ini

            # ログ出力設定
            self.logger = logger
        except Exception as e:
            print("__init__:例外発生")
            print(e)

    def search(self, searchWord):
        """
        googleで検索

        :param str searchWord: 検索語句
        :rtype: str
        :return: 検索結果のURL
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
            print(e)
            return(CommonConstants.ERROR_CHAT_MESSAGE)

    def getLonelyMassage(self, name, channel):
        """
        独りぼっち通知のメッセージの一覧から、ランダムに選択したものを取得

        :param str name: ユーザ名
        :param str channel: チャンネル名
        :rtype: str
        :return: 選択した通知メッセージ
        """
        try:
            f = open(self.ini.get(CommonConstants.INI_SECTION_GENERAL, CommonConstants.INI_OPTION_EXEC_DIR) + "Message.json", "r", CommonConstants.FILE_ENCODING)
            json_data = load(f)
            messageList = json_data[CommonConstants.JSON_MESSAGE_LONELY]
            message = messageList[randint(0, len(messageList) - 1)] # ランダムにメッセージを選択
            return message.replace(CommonConstants.LONELY_MESSAGE_NAME, name).replace(CommonConstants.LONELY_MESSAGE_CHANNEL, channel) # ユーザ名、チャンネル名を置換
        except Exception as e:
            print(e)
            return(CommonConstants.ERROR_CHAT_MESSAGE)

    def getLonelyList(self):
        """
        独りぼっち通知のメッセージの一覧を取得

        :rtype: str
        :return: 改行で成形された通知メッセージの一覧
        """
        try:
            rtn = ""
            with open(self.ini.get(CommonConstants.INI_SECTION_GENERAL, CommonConstants.INI_OPTION_EXEC_DIR) + "Message.json", "r", CommonConstants.FILE_ENCODING) as f:
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
            print(e)
            return(CommonConstants.ERROR_CHAT_MESSAGE)

    def addLonelyList(self, message):
        """
        独りぼっち通知のメッセージを追加

        :param str message: 登録する独りぼっち通知のメッセージ
        :rtype: str
        :return: 処理結果メッセージ
        """
        try:
            # バリデーション
            if message.find(CommonConstants.LONELY_MESSAGE_NAME) == -1:
                return "テンプレートには" + CommonConstants.LONELY_MESSAGE_NAME + "が含まれる必要があります"
            elif message.find(CommonConstants.LONELY_MESSAGE_CHANNEL) == -1:
                return "テンプレートには" + CommonConstants.LONELY_MESSAGE_CHANNEL + "が含まれる必要があります"

            with open(self.ini.get(CommonConstants.INI_SECTION_GENERAL, CommonConstants.INI_OPTION_EXEC_DIR) + "Message.json", "r", CommonConstants.FILE_ENCODING) as fIn:
                json_data = load(fIn)
            messageList = json_data[CommonConstants.JSON_MESSAGE_LONELY]
            if message in messageList:
                return "入力されたテンプレートは既に存在します"

            messageList.append(message)
            json_data[CommonConstants.JSON_MESSAGE_LONELY] = messageList
            with open(self.ini.get(CommonConstants.INI_SECTION_GENERAL, CommonConstants.INI_OPTION_EXEC_DIR) + "Message.json", "w", CommonConstants.FILE_ENCODING) as fOut:
                dump(json_data, fOut) # JSONファイル更新
            return "テンプレート\"" + message + "\"を追加しました"
        except Exception as e:
            print(e)
            return(CommonConstants.ERROR_CHAT_MESSAGE)

    def deleteLonelyList(self, strIndex):
        """
        独りぼっち通知のメッセージを削除

        :param str strIndex: 削除する独りぼっち通知のインデックス
        :rtype: str
        :return: 処理結果メッセージ
        """
        try:
            # バリデーション
            if not strIndex.isdigit():
                return "数値を指定してください"
            index = int(strIndex) # 整数値に変換
            if index < 0:
                return "0以上の数値を指定してください"

            with open(self.ini.get(CommonConstants.INI_SECTION_GENERAL, CommonConstants.INI_OPTION_EXEC_DIR) + "Message.json", "r", CommonConstants.FILE_ENCODING) as fIn:
                json_data = load(fIn)
            messageList = json_data[CommonConstants.JSON_MESSAGE_LONELY]
            if len(messageList) <= index:
                return "入力されたインデックスのテンプレートは存在しません"

            delMessage = messageList[index] # チャットに流すためにテンプレートを取得
            messageList.pop(index)
            json_data[CommonConstants.JSON_MESSAGE_LONELY] = messageList
            with open(self.ini.get(CommonConstants.INI_SECTION_GENERAL, CommonConstants.INI_OPTION_EXEC_DIR) + "Message.json", "w", CommonConstants.FILE_ENCODING) as fOut:
                dump(json_data, fOut) # JSONファイル更新
            return "テンプレート\"" + delMessage +  "\"を削除しました"
        except Exception as e:
            print(e)
            return(CommonConstants.ERROR_CHAT_MESSAGE)

    def getReadme(self):
        """
        readmeを取得

        :rtype: str
        :return: 取得したreadme
        """
        try:
            response = get(CommonConstants.README_URL) # githubのreadme取得APIをコール
            responseJson = response.json()
            readme = b64decode(responseJson[CommonConstants.JSON_README_CONTENT]).decode("utf_8") #結果をbase64でデコードして、さらにutf8でデコード

            rtn = []
            for line in readme.split("\n"):
                # Discordで適用されないMarkdownの記法を置き換える
                if match("#+ ", line):
                    line = sub("#+ ", "**", line) + "**" # 見出しを太字に置き換え
                elif line == "___":
                    line = "" # 水平線を空白行に置き換え
                rtn.append(line)
            return "\n".join(rtn) # 改行を挟んで連結
        except Exception as e:
            print(e)
            return(CommonConstants.ERROR_CHAT_MESSAGE)

    def deleteLog(self):
        """
        古いログファイルを削除
        """
        try:
            self.logger.info("deleteLog開始")
            pathList = list(sorted(Path(self.ini.get(CommonConstants.INI_SECTION_GENERAL, CommonConstants.INI_OPTION_EXEC_DIR) + "log/").glob("*.log.*")))
            self.logger.info("ファイル一覧:" + str(pathList))
            if len(pathList) < 10:
                return

            cnt = 0
            for path in pathList:
                path.unlink()
                self.logger.info("ファイル削除:" + str(path))
                cnt += 1
                if len(pathList) - cnt < 10:
                    return
        except Exception as e:
            self.logger.error("deleteLog:例外発生")
            self.logger.error(e)
            raise e
        finally:
            self.logger.info("deleteLog終了")

    async def asyncDeleteLog(self):
        """
        非同期でログファイル削除処理を実行
        """
        while True:
            try:
                self.deleteLog()
                await sleep(86400) # 一日に1回実行
            except Exception as e:
                self.logger.error("asyncDeleteLog:例外発生")
                self.logger.error(e)
