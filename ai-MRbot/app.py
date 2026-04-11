from flask import Flask, request, abort
import json
import os

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

# 環境變數設定
configuration = Configuration(access_token=os.getenv('LINE_CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.getenv('LINE_CHANNEL_SECRET'))

# 取得目前 app.py 所在的資料夾 (ai-MRbot)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def load_flex(filepath):
    """
    因為 case1/case2 在 ai-MRbot 外層，所以使用 ".." 回到上一層
    """
    full_path = os.path.normpath(os.path.join(BASE_DIR, "..", filepath))
    
    # Debug 用：如果檔案還是找不到，可以在 Render Log 看到實際路徑
    if not os.path.exists(full_path):
        print(f"Error: 找不到檔案 {full_path}")
        
    with open(full_path, "r", encoding="utf-8") as f:
        return json.load(f)


@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        app.logger.info("Invalid signature.")
        abort(400)
    return 'OK'


@app.route("/liff/<folder>/<name>")
def liff_page(folder, name):
    """
    LIFF 頁面同樣需要跳到外層資料夾尋找
    """
    filename = f"liff_{name}.html"
    # 使用 ".." 回到根目錄再進入指定的 folder
    filepath = os.path.normpath(os.path.join(BASE_DIR, "..", folder, filename))
    
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        return content, 200, {"Content-Type": "text/html; charset=utf-8"}
    except FileNotFoundError:
        return "File Not Found", 404


@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    user_msg = event.message.text.strip()

    if user_msg == "小如如":
        # 這裡會去找 ai-MRbot/../case1/card_luru.json
        flex_json = load_flex("case1/card_luru.json")
        reply_msg = FlexMessage(
            alt_text="小如如的電子名片",
            contents=FlexContainer.from_dict(flex_json)
        )
    elif user_msg == "鍾師富":
        # 這裡會去找 ai-MRbot/../case2/card_chung.json
        flex_json = load_flex("case2/card_chung.json")
        reply_msg = FlexMessage(
            alt_text="鍾師富的電子名片",
            contents=FlexContainer.from_dict(flex_json)
        )
    else:
        reply_msg = TextMessage(text="請輸入關鍵字：\n🔹 小如如\n🔹 鍾師富")

    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        line_bot_api.reply_message_with_http_info(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[reply_msg]
            )
        )


if __name__ == "__main__":
    app.run()
