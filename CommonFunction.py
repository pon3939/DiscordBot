# -*- coding: utf-8 -*-

import CommonConstants
from configparser import ConfigParser
from googleapiclient.discovery import build
from random import randint

# ---------------------------------------
# 共通関数クラス
# ---------------------------------------

class CommonFunction:
    # コンストラクタ
    def __init__(self, ini = None):
        try:
            self.ini = ini
        except Exception as e:
            print("__init__:例外発生")
            print(e)

    # googleで検索
    def search(self, searchWord):
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
