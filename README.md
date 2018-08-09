# DiscordBot

DiscordのBot  
だれか面白いBOT作って
___

## チャット

### readme表示

`@{BOT} readme`でreadme表示

### google画像検索

`@{BOT} gogle search {検索キーワード}`でgoogle画像検索

### 独りぼっち通知メッセージ編集

`@{BOT} lonely list`で独りぼっち通知メッセージの一覧表示  
`@{BOT} lonely add {追加したいテンプレート}`で独りぼっち通知メッセージ追加  
`@{BOT} lonely delete {削除したいテンプレートのインデックス}`で独りぼっち通知メッセージ削除

### タスク管理

`@{BOT} task list`でタスクの一覧表示  
`@{BOT} task add {追加したいテンプレート}`でタスク追加  
`@{BOT} task delete {削除したいテンプレートのインデックス}`でタスク削除  
時間になったら登録したチャンネルにリマインドする

### RSSリーダー

`@{BOT} rss list`でRSSの一覧表示  
`@{BOT} rss add {追加したいURL}`でRSS追加  
`@{BOT} rss delete {削除したいURLのインデックス}`でRSS削除  
定期的に登録したRSSをチャンネルに流す
___

## 通知

### 独りぼっち通知

ボイスチャンネルに誰かが独りぼっちだと、チャットで通知する

## 使用ライブラリ

- asyncio
- click
- discord.py
- feedparser
- google-api-python-client
