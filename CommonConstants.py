#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
共通定数
"""

# ファイル読み込み時の文字コード
FILE_ENCODING = "utf_8"

# iniファイルのセクション
INI_SECTION_GENERAL = "general"
INI_SECTION_TEXT_CHANNEL = "textChannel"
INI_SECTION_GOOGLE = "google"

# iniファイルのキー
INI_OPTION_TOKEN = "token"
INI_OPTION_NAME = "name"
INI_OPTION_API_KEY = "apiKey"
INI_OPTION_ENGINE_KEY = "engineKey"
INI_OPTION_EXEC_DIR = "execDir"

# JSONのファイル名
JSON_NAME_TASK = "Task"
JSON_NAME_MESSAGE = "Message"

# JSONのキー
JSON_KEY_CHANNEL = "Channel"
JSON_KEY_CHANNEL_ID = "ChannelID"
JSON_KEY_CONTENT = "content"
JSON_KEY_LONELY = "Lonely"
JSON_KEY_MESSAGE = "Message"
JSON_KEY_TASK = "Task"
JSON_KEY_TIME = "Time"

# 独りぼっち通知の置換文字列
LONELY_MESSAGE_NAME = "{name}"
LONELY_MESSAGE_CHANNEL = "{channel}"

ERROR_CHAT_MESSAGE = "エラーが発生しました。管理者に連絡してください。" # エラー時にチャットに流すメッセージ
README_URL = "https://api.github.com/repos/pon3939/DiscordBot/readme" # githubのreadme取得APIのURL
