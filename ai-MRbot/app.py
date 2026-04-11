import os
import json
import sys
from flask import Flask, request, abort, render_template

from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage,
    FlexMessage,
    FlexContainer
)
from linebot.v3.webhooks import MessageEvent, TextMessageContent

app = Flask(__name__)

# --- LINE Bot 設定 ---
# 請確保你在 Render 的 Environment Variables 設定了這兩個變數
configuration = Configuration(access_token=os.getenv('LINE_CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.getenv('LINE_CHANNEL_SECRET'))

def load_flex(filepath):
    """載入 Flex Message JSON 檔案，路徑相對於 app.py"""
    # 取得目前 app.py 所在的絕對路徑 (ai-MRbot 資料夾)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    full_path = os.path.join(current_dir, filepath)
    
    print(f"DEBUG: 正在嘗試讀取: {full_path}")
    
    if not os.path.exists(full_path):
        # 偵錯用：如果找不到檔案，印出目前目錄下的所有東西
        content = os.listdir(current_dir)
        print(f"ERROR: 找不到檔案 {filepath}。目前目錄內容: {content}")
        # 回傳一個簡單的文字訊息以免程式完全當掉
        return None

    with open(full_path, "r", encoding="utf-8") as f:
        return json.load(f)

# --- 路由設定 ---

@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers.get('X-Line-Signature')
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        app.logger.error("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'

# LIFF 頁面路由：小如如
@app.route("/liff/case1/luru")
def liff_luru():
    return render_template("case1/liff_luru.html")

# LIFF 頁面路由：鍾師富
@app.route("/liff/case2/chung")
def liff_chung():
    return render_template("case2/liff_chung.html")

# --- LINE 訊息處理 ---

@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    user_msg = event.message.text.strip()
    
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        
        # 邏輯判斷：根據關鍵字發送對應的 Flex Message
        if "小如如" in user_msg:
            flex_data = load_flex("case1/card_luru.json")
            if flex_data:
                flex_msg = FlexMessage(
                    alt_text="小如如的電子名片",
                    contents=FlexContainer.from_dict(flex_data)
                )
                line_bot_api.reply_message(
                    ReplyMessageRequest(reply_token=event.reply_token, messages=[flex_msg])
                )
            else:
                line_bot_api.reply_message(
                    ReplyMessageRequest(reply_token=event.reply_token, messages=[TextMessage(text="抱歉，名片檔案讀取失敗")])
                )

        elif "鍾師富" in user_msg:
            flex_data = load_flex("case2/card_chung.json")
            if flex_data:
                flex_msg = FlexMessage(
                    alt_text="鍾師富的電子名片",
                    contents=FlexContainer.from_dict(flex_data)
                )
                line_bot_api.reply_message(
                    ReplyMessageRequest(reply_token=event.reply_token, messages=[flex_msg])
                )
            else:
                line_bot_api.reply_message(
                    ReplyMessageRequest(reply_token=event.reply_token, messages=[TextMessage(text="抱歉，名片檔案讀取失敗")])
                )

if __name__ == "__main__":
    # Render 會透過環境變數指定 Port，預設為 10000
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
