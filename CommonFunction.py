#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
共通関数
"""

import CommonConstants
from aiohttp import ClientSession
from asyncio import sleep
from base64 import b64decode
from codecs import open
from configparser import ConfigParser
from datetime import datetime
from feedparser import parse
from googleapiclient.discovery import build
from json import dump, load
from random import randint
from re import match, sub
from requests import get
from time import mktime
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
        return rtn
    except Exception as e:
        print("GetMyLogger:例外発生")
        print(e)
        raise e

class CommonFunction:
    """
    共通関数クラス
    """

    def __init__(self, ini, logger, client):
        """
        コンストラクタ

        :param configparser.ConfigParser ini: INIファイル
        :param logging.Logger logger: ロガー
        :param discord.Client client: Discordクライアント
        """
        try:
            self.ini = ini
            self.logger = logger
            self.client = client
        except Exception as e:
            self.logger.error("__init__:例外発生")
            self.logger.exception("%s", e)
            raise e

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
            self.logger.error("search:例外発生")
            self.logger.exception("%s", e)
            return CommonConstants.ERROR_CHAT_MESSAGE

    def getLonelyMassage(self, name, channel):
        """
        独りぼっち通知のメッセージの一覧から、ランダムに選択したものを取得

        :param str name: ユーザ名
        :param str channel: チャンネル名
        :rtype: str
        :return: 選択した通知メッセージ
        """
        try:
            f = open(self.ini.get(CommonConstants.INI_SECTION_GENERAL, CommonConstants.INI_OPTION_EXEC_DIR) + "Json/" + CommonConstants.JSON_NAME_MESSAGE + ".json", "r", CommonConstants.FILE_ENCODING)
            json_data = load(f)
            messageList = json_data[CommonConstants.JSON_KEY_LONELY]
            message = messageList[randint(0, len(messageList) - 1)] # ランダムにメッセージを選択
            return message.replace(CommonConstants.LONELY_MESSAGE_NAME, name).replace(CommonConstants.LONELY_MESSAGE_CHANNEL, channel) # ユーザ名、チャンネル名を置換
        except Exception as e:
            self.logger.error("getLonelyMassage:例外発生")
            self.logger.exception("%s", e)
            return CommonConstants.ERROR_CHAT_MESSAGE

    def getLonelyList(self):
        """
        独りぼっち通知のメッセージの一覧を取得

        :rtype: str
        :return: 改行で成形された通知メッセージの一覧
        """
        try:
            rtn = ""
            with open(self.ini.get(CommonConstants.INI_SECTION_GENERAL, CommonConstants.INI_OPTION_EXEC_DIR) + "Json/" + CommonConstants.JSON_NAME_MESSAGE + ".json", "r", CommonConstants.FILE_ENCODING) as f:
                json_data = load(f)
            messageList = json_data[CommonConstants.JSON_KEY_LONELY]

            i = 0
            for message in messageList:
                if rtn != "":
                    rtn += "\n" # 2件目以降は改行
                rtn += str(i) + " : " + message
                i += 1
            return rtn
        except Exception as e:
            self.logger.error("getLonelyList:例外発生")
            self.logger.exception("%s", e)
            return CommonConstants.ERROR_CHAT_MESSAGE

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

            with open(self.ini.get(CommonConstants.INI_SECTION_GENERAL, CommonConstants.INI_OPTION_EXEC_DIR) + "Json/" + CommonConstants.JSON_NAME_MESSAGE + ".json", "r", CommonConstants.FILE_ENCODING) as fIn:
                json_data = load(fIn)
            messageList = json_data[CommonConstants.JSON_KEY_LONELY]
            if message in messageList:
                return "入力されたテンプレートは既に存在します"

            messageList.append(message)
            json_data[CommonConstants.JSON_KEY_LONELY] = messageList
            with open(self.ini.get(CommonConstants.INI_SECTION_GENERAL, CommonConstants.INI_OPTION_EXEC_DIR) + "Json/" + CommonConstants.JSON_NAME_MESSAGE + ".json", "w", CommonConstants.FILE_ENCODING) as fOut:
                dump(json_data, fOut) # JSONファイル更新
            return "テンプレート\"" + message + "\"を追加しました"
        except Exception as e:
            self.logger.error("addLonelyList:例外発生")
            self.logger.exception("%s", e)
            return CommonConstants.ERROR_CHAT_MESSAGE

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

            with open(self.ini.get(CommonConstants.INI_SECTION_GENERAL, CommonConstants.INI_OPTION_EXEC_DIR) + "Json/" + CommonConstants.JSON_NAME_MESSAGE + ".json", "r", CommonConstants.FILE_ENCODING) as fIn:
                json_data = load(fIn)
            messageList = json_data[CommonConstants.JSON_KEY_LONELY]
            if len(messageList) <= index:
                return "入力されたインデックスのテンプレートは存在しません"

            delMessage = messageList[index] # チャットに流すためにテンプレートを取得
            messageList.pop(index)
            json_data[CommonConstants.JSON_KEY_LONELY] = messageList
            with open(self.ini.get(CommonConstants.INI_SECTION_GENERAL, CommonConstants.INI_OPTION_EXEC_DIR) + "Json/" + CommonConstants.JSON_NAME_MESSAGE + ".json", "w", CommonConstants.FILE_ENCODING) as fOut:
                dump(json_data, fOut) # JSONファイル更新
            return "テンプレート\"" + delMessage +  "\"を削除しました"
        except Exception as e:
            self.logger.error("deleteLonelyList:例外発生")
            self.logger.exception("%s", e)
            return CommonConstants.ERROR_CHAT_MESSAGE

    def getReadme(self):
        """
        readmeを取得

        :rtype: str
        :return: 取得したreadme
        """
        try:
            response = get(CommonConstants.README_URL) # githubのreadme取得APIをコール
            responseJson = response.json()
            readme = b64decode(responseJson[CommonConstants.JSON_KEY_CONTENT]).decode("utf_8") #結果をbase64でデコードして、さらにutf8でデコード

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
            self.logger.error("getReadme:例外発生")
            self.logger.exception("%s", e)
            return CommonConstants.ERROR_CHAT_MESSAGE

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
            self.logger.exception("%s", e)
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
                self.logger.exception("%s", e)

    def getTaskList(self, channelID):
        """
        タスク一覧を表示

        :param str channelID: タスクを取得するチャンネルID
        :rtype: str
        :return: タスク一覧
        """
        try:
            rtn = ""
            # Jsonファイル取得
            with open(self.ini.get(CommonConstants.INI_SECTION_GENERAL, CommonConstants.INI_OPTION_EXEC_DIR) + "Json/" + CommonConstants.JSON_NAME_TASK + ".json", "r", CommonConstants.FILE_ENCODING) as fIn:
                json_data = load(fIn)

            for channel in json_data[CommonConstants.JSON_KEY_CHANNEL]:
                if channel[CommonConstants.JSON_KEY_CHANNEL_ID] == channelID:
                    i = 0
                    for task in channel[CommonConstants.JSON_KEY_TASK]:
                        if rtn != "":
                            rtn += "\n" # 2件目以降は改行
                        rtn += str(i) + " : " + task[CommonConstants.JSON_KEY_TIME] + " " + task[CommonConstants.JSON_KEY_MESSAGE]
                        i += 1
                    break

            if rtn == "":
                rtn = "登録されたタスクはありません"
            return rtn
        except Exception as e:
            self.logger.error("getTaskList:例外発生")
            self.logger.exception("%s", e)
            return CommonConstants.ERROR_CHAT_MESSAGE

    def addTaskList(self, message, channelID):
        """
        タスクを追加

        :param str message: 登録するタスクのメッセージ
        :param str channelID: タスクを登録するチャンネルID
        :rtype: str
        :return: 処理結果メッセージ
        """
        try:
            splitList = message.split()
            # バリデーション
            if len(splitList) < 3:
                return "task add %Y-%m-%d %H:%M {タスク内容}の形式で入力してください。"
            time = self.strToDatetime(" ".join(splitList[:2]))
            if time is None:
                return "task add %Y-%m-%d %H:%M {タスク内容}の形式で入力してください。"
            elif time < datetime.now():
                return "未来の時間を指定してください。"

            # タスクを作成
            taskMessage = " ".join(splitList[2:])
            task = {}
            task[CommonConstants.JSON_KEY_TIME] = time.strftime("%Y-%m-%d %H:%M")
            task[CommonConstants.JSON_KEY_MESSAGE] = taskMessage

            # Jsonファイル取得
            with open(self.ini.get(CommonConstants.INI_SECTION_GENERAL, CommonConstants.INI_OPTION_EXEC_DIR) + "Json/" + CommonConstants.JSON_NAME_TASK + ".json", "r", CommonConstants.FILE_ENCODING) as fIn:
                json_data = load(fIn)

            # チャンネルIDで検索して追加
            exists = False
            for i in range(len(json_data[CommonConstants.JSON_KEY_CHANNEL])):
                if json_data[CommonConstants.JSON_KEY_CHANNEL][i][CommonConstants.JSON_KEY_CHANNEL_ID] == channelID:
                    json_data[CommonConstants.JSON_KEY_CHANNEL][i][CommonConstants.JSON_KEY_TASK].append(task)
                    exists = True
                    break

            if not exists:
                # なければ作成
                channel = {}
                channel[CommonConstants.JSON_KEY_CHANNEL_ID] = channelID
                channel[CommonConstants.JSON_KEY_TASK] = [task]
                json_data[CommonConstants.JSON_KEY_CHANNEL].append(channel)

            with open(self.ini.get(CommonConstants.INI_SECTION_GENERAL, CommonConstants.INI_OPTION_EXEC_DIR) + "Json/" + CommonConstants.JSON_NAME_TASK + ".json", "w", CommonConstants.FILE_ENCODING) as fOut:
                dump(json_data, fOut) # JSONファイル更新
            return time.strftime("%Y-%m-%d %H:%M") + "に" + taskMessage + "を追加しました。"
        except Exception as e:
            self.logger.error("addTaskList:例外発生")
            self.logger.exception("%s", e)
            return CommonConstants.ERROR_CHAT_MESSAGE

    def deleteTaskList(self, strIndex, channelID):
        """
        タスクを削除

        :param str message: 削除するタスクのインデックス
        :param str channelID: タスクを削除するチャンネルID
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

            with open(self.ini.get(CommonConstants.INI_SECTION_GENERAL, CommonConstants.INI_OPTION_EXEC_DIR) + "Json/" + CommonConstants.JSON_NAME_TASK + ".json", "r", CommonConstants.FILE_ENCODING) as fIn:
                json_data = load(fIn)

            # チャンネルIDで検索して削除
            exists = False
            for i in range(len(json_data[CommonConstants.JSON_KEY_CHANNEL])):
                if json_data[CommonConstants.JSON_KEY_CHANNEL][i][CommonConstants.JSON_KEY_CHANNEL_ID] == channelID:
                    if index < len(json_data[CommonConstants.JSON_KEY_CHANNEL][i][CommonConstants.JSON_KEY_TASK]):
                        exists = True
                        delTask = json_data[CommonConstants.JSON_KEY_CHANNEL][i][CommonConstants.JSON_KEY_TASK][index] # チャットに流すためにタスクを取得
                        json_data[CommonConstants.JSON_KEY_CHANNEL][i][CommonConstants.JSON_KEY_TASK].pop(index)
                    break

            if not exists:
                return "入力されたインデックスのタスクは存在しません"

            with open(self.ini.get(CommonConstants.INI_SECTION_GENERAL, CommonConstants.INI_OPTION_EXEC_DIR) + "Json/" + CommonConstants.JSON_NAME_TASK + ".json", "w", CommonConstants.FILE_ENCODING) as fOut:
                dump(json_data, fOut) # JSONファイル更新
            return "タスク\"" + delTask[CommonConstants.JSON_KEY_TIME] + " " + delTask[CommonConstants.JSON_KEY_MESSAGE] +  "\"を削除しました"
        except Exception as e:
            self.logger.error("addTaskList:例外発生")
            self.logger.exception("%s", e)
            return CommonConstants.ERROR_CHAT_MESSAGE

    def strToDatetime(self, strDatetime):
        """
        strをDateTimeに変換

        :param str strDatetime: 変換する文字列(%Y-%m-%d %H:%M)
        :rtype: datetime
        :return: 変換した値 変換失敗時はNone
        """
        try:
            return datetime.strptime(strDatetime, "%Y-%m-%d %H:%M")
        except Exception as e:
            self.logger.error("strToDatetime:例外発生")
            self.logger.exception("%s", e)
            return None

    async def remindTask(self):
        """
        タスクをリマインド
        """
        try:
            self.logger.info("remindTask開始")
            with open(self.ini.get(CommonConstants.INI_SECTION_GENERAL, CommonConstants.INI_OPTION_EXEC_DIR) + "Json/" + CommonConstants.JSON_NAME_TASK + ".json", "r", CommonConstants.FILE_ENCODING) as fIn:
                json_data = load(fIn)

            for i in range(len(json_data[CommonConstants.JSON_KEY_CHANNEL])):
                channelID = json_data[CommonConstants.JSON_KEY_CHANNEL][i][CommonConstants.JSON_KEY_CHANNEL_ID]
                for j in range(len(json_data[CommonConstants.JSON_KEY_CHANNEL][i][CommonConstants.JSON_KEY_TASK])):
                    taskTime = json_data[CommonConstants.JSON_KEY_CHANNEL][i][CommonConstants.JSON_KEY_TASK][j][CommonConstants.JSON_KEY_TIME]
                    taskMessage = json_data[CommonConstants.JSON_KEY_CHANNEL][i][CommonConstants.JSON_KEY_TASK][j][CommonConstants.JSON_KEY_MESSAGE]
                    if self.strToDatetime(taskTime) < datetime.now():
                        # 時間を過ぎているものはリマインドして削除
                        message = "リマインド : " + taskTime + " " + taskMessage
                        await self.client.send_message(self.client.get_channel(channelID), message)
                        json_data[CommonConstants.JSON_KEY_CHANNEL][i][CommonConstants.JSON_KEY_TASK].pop(j)

            with open(self.ini.get(CommonConstants.INI_SECTION_GENERAL, CommonConstants.INI_OPTION_EXEC_DIR) + "Json/" + CommonConstants.JSON_NAME_TASK + ".json", "w", CommonConstants.FILE_ENCODING) as fOut:
                dump(json_data, fOut) # JSONファイル更新
        except Exception as e:
            self.logger.error("remindTask:例外発生")
            self.logger.exception("%s", e)
            raise e
        finally:
            self.logger.info("remindTask終了")

    async def asyncRemindTask(self):
        """
        非同期でリマインド処理を実行
        """
        while True:
            try:
                await self.remindTask()
                await sleep(30) # 30秒に1回実行
            except Exception as e:
                self.logger.error("asyncRemindTask:例外発生")
                self.logger.exception("%s", e)

    def getRSSList(self, channelID):
        """
        RSS一覧を表示

        :param str channelID: RSSを取得するチャンネルID
        :rtype: str
        :return: RSS一覧
        """
        try:
            rtn = ""
            # Jsonファイル取得
            with open(self.ini.get(CommonConstants.INI_SECTION_GENERAL, CommonConstants.INI_OPTION_EXEC_DIR) + "Json/" + CommonConstants.JSON_NAME_RSS + ".json", "r", CommonConstants.FILE_ENCODING) as fIn:
                json_data = load(fIn)

            for channel in json_data[CommonConstants.JSON_KEY_CHANNEL]:
                if channel[CommonConstants.JSON_KEY_CHANNEL_ID] == channelID:
                    i = 0
                    for rss in channel[CommonConstants.JSON_KEY_RSS]:
                        if rtn != "":
                            rtn += "\n" # 2件目以降は改行
                        rtn += str(i) + " : " + rss[CommonConstants.JSON_KEY_URL]
                        i += 1
                    break

            if rtn == "":
                rtn = "登録されたRSSはありません"
            return rtn
        except Exception as e:
            self.logger.error("getRSSList:例外発生")
            self.logger.exception("%s", e)
            return CommonConstants.ERROR_CHAT_MESSAGE

    async def addRSSList(self, url, channelID):
        """
        タスクを追加

        :param str url: 登録するRSSのURL
        :param str channelID: RSSを登録するチャンネルID
        :rtype: str
        :return: 処理結果メッセージ
        """
        try:
            # RSS取得
            parseResult = await self.parseRSS(url)
            if len(parseResult["entries"]) < 1:
                return "RSSではありません"

            # エントリのIDを取得
            entries = []
            for entrie in parseResult["entries"]:
                entries.append(entrie["link"])

            rss = {}
            rss[CommonConstants.JSON_KEY_URL] = url
            rss[CommonConstants.JSON_KEY_ENTRIES] = entries

            # Jsonファイル取得
            with open(self.ini.get(CommonConstants.INI_SECTION_GENERAL, CommonConstants.INI_OPTION_EXEC_DIR) + "Json/" + CommonConstants.JSON_NAME_RSS + ".json", "r", CommonConstants.FILE_ENCODING) as fIn:
                json_data = load(fIn)

            # チャンネルIDで検索して追加
            exists = False
            for i in range(len(json_data[CommonConstants.JSON_KEY_CHANNEL])):
                if json_data[CommonConstants.JSON_KEY_CHANNEL][i][CommonConstants.JSON_KEY_CHANNEL_ID] == channelID:
                    for chackRss in json_data[CommonConstants.JSON_KEY_CHANNEL][i][CommonConstants.JSON_KEY_RSS]:
                        if chackRss[CommonConstants.JSON_KEY_URL] == url:
                            return "入力されたURLは登録済みです。"
                    json_data[CommonConstants.JSON_KEY_CHANNEL][i][CommonConstants.JSON_KEY_RSS].append(rss)
                    exists = True
                    break

            if not exists:
                # なければ作成
                channel = {}
                channel[CommonConstants.JSON_KEY_CHANNEL_ID] = channelID
                channel[CommonConstants.JSON_KEY_RSS] = [rss]
                json_data[CommonConstants.JSON_KEY_CHANNEL].append(channel)

            with open(self.ini.get(CommonConstants.INI_SECTION_GENERAL, CommonConstants.INI_OPTION_EXEC_DIR) + "Json/" + CommonConstants.JSON_NAME_RSS + ".json", "w", CommonConstants.FILE_ENCODING) as fOut:
                dump(json_data, fOut) # JSONファイル更新
            return url + " を追加しました。"
        except Exception as e:
            self.logger.error("addRSSList:例外発生")
            self.logger.exception("%s", e)
            return CommonConstants.ERROR_CHAT_MESSAGE

    def deleteRSSList(self, strIndex, channelID):
        """
        RSSを削除

        :param str message: 削除するRSSのインデックス
        :param str channelID: RSSを削除するチャンネルID
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

            with open(self.ini.get(CommonConstants.INI_SECTION_GENERAL, CommonConstants.INI_OPTION_EXEC_DIR) + "Json/" + CommonConstants.JSON_NAME_RSS + ".json", "r", CommonConstants.FILE_ENCODING) as fIn:
                json_data = load(fIn)

            # チャンネルIDで検索して削除
            exists = False
            for i in range(len(json_data[CommonConstants.JSON_KEY_CHANNEL])):
                if json_data[CommonConstants.JSON_KEY_CHANNEL][i][CommonConstants.JSON_KEY_CHANNEL_ID] == channelID:
                    if index < len(json_data[CommonConstants.JSON_KEY_CHANNEL][i][CommonConstants.JSON_KEY_RSS]):
                        exists = True
                        delURL = json_data[CommonConstants.JSON_KEY_CHANNEL][i][CommonConstants.JSON_KEY_RSS][index][CommonConstants.JSON_KEY_URL] # チャットに流すためにURLを取得
                        json_data[CommonConstants.JSON_KEY_CHANNEL][i][CommonConstants.JSON_KEY_RSS].pop(index)
                    break

            if not exists:
                return "入力されたインデックスのRSSは存在しません"

            with open(self.ini.get(CommonConstants.INI_SECTION_GENERAL, CommonConstants.INI_OPTION_EXEC_DIR) + "Json/" + CommonConstants.JSON_NAME_RSS + ".json", "w", CommonConstants.FILE_ENCODING) as fOut:
                dump(json_data, fOut) # JSONファイル更新
            return delURL + " を削除しました"
        except Exception as e:
            self.logger.error("deleteRSSList:例外発生")
            self.logger.exception("%s", e)
            return CommonConstants.ERROR_CHAT_MESSAGE

    async def getRSS(self):
        """
        RSSを取得してチャットに流す
        """
        try:
            self.logger.info("getRSS開始")
            with open(self.ini.get(CommonConstants.INI_SECTION_GENERAL, CommonConstants.INI_OPTION_EXEC_DIR) + "Json/" + CommonConstants.JSON_NAME_RSS + ".json", "r", CommonConstants.FILE_ENCODING) as fIn:
                json_data = load(fIn)

            for i in range(len(json_data[CommonConstants.JSON_KEY_CHANNEL])):
                channelID = json_data[CommonConstants.JSON_KEY_CHANNEL][i][CommonConstants.JSON_KEY_CHANNEL_ID]
                for j in range(len(json_data[CommonConstants.JSON_KEY_CHANNEL][i][CommonConstants.JSON_KEY_RSS])):
                    parseResult = await self.parseRSS(json_data[CommonConstants.JSON_KEY_CHANNEL][i][CommonConstants.JSON_KEY_RSS][j][CommonConstants.JSON_KEY_URL])
                    title = parseResult["feed"]["title"] # タイトルを取得
                    entries = []
                    for entrie in parseResult["entries"]:
                        entries.append(entrie["link"])
                        if entrie["link"] not in json_data[CommonConstants.JSON_KEY_CHANNEL][i][CommonConstants.JSON_KEY_RSS][j][CommonConstants.JSON_KEY_ENTRIES]:
                            # 前回取得していない分はチャットに流す
                            message = title + "\n" + entrie["title"] + "\n" + entrie["link"]
                            await self.client.send_message(self.client.get_channel(channelID), message)
                    json_data[CommonConstants.JSON_KEY_CHANNEL][i][CommonConstants.JSON_KEY_RSS][j][CommonConstants.JSON_KEY_ENTRIES] = entries # 今回取得したエントリを登録

            with open(self.ini.get(CommonConstants.INI_SECTION_GENERAL, CommonConstants.INI_OPTION_EXEC_DIR) + "Json/" + CommonConstants.JSON_NAME_RSS + ".json", "w", CommonConstants.FILE_ENCODING) as fOut:
                dump(json_data, fOut) # JSONファイル更新
        except Exception as e:
            self.logger.error("getRSS:例外発生")
            self.logger.exception("%s", e)
            raise e
        finally:
            self.logger.info("getRSS終了")

    async def asyncRSS(self):
        """
        非同期でRSS処理を実行
        """
        while True:
            try:
                await self.getRSS()
                await sleep(300) # 5分に1回実行
            except Exception as e:
                self.logger.error("asyncRSS:例外発生")
                self.logger.exception("%s", e)

    async def parseRSS(self, url):
        """
        :param str url: rssを取得するurl
        :rtype: feedparser.FeedParserDict
        :return: 取得したrss
        非同期でRSSを取得
        """
        try:
            async with ClientSession() as session:
                async with session.get(url) as response:
                    body = await response.read()
            return parse(body)
        except Exception as e:
            self.logger.error("parseRSS:例外発生")
            self.logger.exception("%s", e)
