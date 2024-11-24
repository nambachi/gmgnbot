import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import nest_asyncio
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
import re

# Nest asyncio
nest_asyncio.apply()

# Bot Token
BOT_TOKEN = '8191864923:AAG31RGKG5CgxAJqcgZkZATgoCDWjJYCJ0A'

# サービスアカウントキーのファイルパス
CREDENTIALS_FILE = 'gmgn-bot-0f9a5cdd9171.json'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
# スプレッドシートID（URLから取得）
SHEET_ID= '1a2RAwhNsR2N7PwryBoeY3wiRgTRZL060nD9Sri_YNqA'

# Google Sheetsの認証とアクセス
def connect_to_google_sheet():
    creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, SCOPES)
    client = gspread.authorize(creds)
    return client.open_by_key(SHEET_ID).sheet1  # 最初のシートを開く

sheet = connect_to_google_sheet()

# メッセージを解析して辞書形式でトピック別にデータを抽出する関数
def parse_message(message):
    data = {}

    # 定型文のパターンに基づいてデータを抽出
    data["Platform"] = re.search(r"【(\w+)】", message).group(1) if re.search(r"【(\w+)】", message) else ""
    data["Project"] = re.search(r"【\w+】(.+)", message).group(1).strip() if re.search(r"【\w+】(.+)", message) else ""
    data["Pump Status"] = re.search(r"Pump Status: (.+)", message).group(1) if re.search(r"Pump Status: (.+)", message) else ""
    data["Price"] = re.search(r"\$(\d+\.\d+)", message).group(0) if re.search(r"\$(\d+\.\d+)", message) else ""
    data["MC"] = re.search(r"MC:\s*(\$\d+(\.\d+)?[KM]?)", message).group(1) if re.search(r"MC:\s*(\$\d+(\.\d+)?[KM]?)", message) else ""
    data["Liq"] = re.search(r"Liq:\s+([\d\.]+ SOL)", message).group(1) if re.search(r"Liq:\s+([\d\.]+ SOL)", message) else ""
    data["Initial LP"] = re.search(r"💰 Initial LP: (.+)", message).group(1) if re.search(r"💰 Initial LP: (.+)", message) else ""
    data["Holders"] = re.search(r"👥 Holders: (\d+)", message).group(1) if re.search(r"👥 Holders: (\d+)", message) else ""

    # 📈 5m, 1h, 6h
    match_timeframes = re.search(r"📈 5m \| 1h \| 6h: ([\d\.\-]+%) \| ([\d\.\-]+%) \| ([\d\.\-]+%)", message)
    if match_timeframes:
        data["5m"] = match_timeframes.group(1).strip()
        data["1h"] = match_timeframes.group(2).strip()
        data["6h"] = match_timeframes.group(3).strip()
    else:
        data["5m"], data["1h"], data["6h"] = "", "", ""

    data["DEV Burnt"] = re.search(r"🔥 DEV Burnt: (.+)", message).group(1) if re.search(r"🔥 DEV Burnt: (.+)", message) else ""
    data["Smart Buy/Sell"] = re.search(r"🔥 Smart Buy/Sell: (.+)", message).group(1) if re.search(r"🔥 Smart Buy/Sell: (.+)", message) else ""
    data["Audit"] = re.search(r"🔔 Audit: (.+)", message).group(1) if re.search(r"🔔 Audit: (.+)", message) else ""
    data["Top 10"] = re.search(r"✅ Top 10: ([\d\.]+%)", message).group(1) if re.search(r"✅ Top 10: ([\d\.]+%)", message) else ""
    data["Hold"] = re.search(r"🌕 Hold:\s+(\d+)", message).group(1) if re.search(r"🌕 Hold:\s+(\d+)", message) else ""
    data["Bought more"] = re.search(r"🌝 Bought more:\s+(\d+)", message).group(1) if re.search(r"🌝 Bought more:\s+(\d+)", message) else ""
    data["Sold part"] = re.search(r"🌗 Sold part:\s+(\d+)", message).group(1) if re.search(r"🌗 Sold part:\s+(\d+)", message) else ""
    data["Sold out"] = re.search(r"🌑 Sold out:\s+(\d+)", message).group(1) if re.search(r"🌑 Sold out:\s+(\d+)", message) else ""
    data["Token"] = re.search(r"Token\s+([\w\d]+)", message).group(1) if re.search(r"Token\s+([\w\d]+)", message) else ""

    return data

# メッセージを処理する関数
async def handle_message(update: Update, context):
    message = update.message.text  # 受信したメッセージのテキストを取得

    # メッセージに「Token」が含まれている場合
    if "Token" in message:
        try:
            # メッセージを解析して辞書形式にする
            parsed_data = parse_message(message)

            # スプレッドシートに書き込む行を準備
            row = [
                parsed_data.get("Platform", ""),
                parsed_data.get("Project", ""),
                parsed_data.get("Pump Status", ""),
                parsed_data.get("Price", ""),
                parsed_data.get("MC", ""),
                parsed_data.get("Liq", ""),
                parsed_data.get("Initial LP", ""),
                parsed_data.get("Holders", ""),
                parsed_data.get("5m", ""),
                parsed_data.get("1h", ""),
                parsed_data.get("6h", ""),
                parsed_data.get("DEV Burnt", ""),
                parsed_data.get("Smart Buy/Sell", ""),
                parsed_data.get("Audit", ""),
                parsed_data.get("Top 10", ""),
                parsed_data.get("Hold", ""),
                parsed_data.get("Bought more", ""),
                parsed_data.get("Sold part", ""),
                parsed_data.get("Sold out", ""),
                parsed_data.get("Token", ""),
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),  # タイムスタンプ
            ]

            # スプレッドシートにデータを記載
            sheet.append_row(row)

            await context.bot.send_message(
                chat_id=update.effective_chat.id, text="スプレッドシートに記録しました！"
            )
        except Exception as e:
            await context.bot.send_message(
                chat_id=update.effective_chat.id, text=f"エラーが発生しました: {e}"
            )

# メイン関数
async def main():
    # Telegram Bot Applicationを作成
    application = Application.builder().token(BOT_TOKEN).build()

    # メッセージを監視するハンドラーを追加
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot is running...")
    # ボットをポーリングで実行
    await application.run_polling()


# Pythonスクリプトとしてのエントリーポイント
if __name__ == '__main__':
    import asyncio
    import nest_asyncio

    # 既存のイベントループを修正（必須）
    nest_asyncio.apply()

    # イベントループを起動してmain()を実行
    asyncio.run(main())


