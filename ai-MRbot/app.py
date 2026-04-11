from flask import Flask, request, abort, send_from_directory
import json
import os

from linebot.v3 import (
    WebhookHandler
)
from linebot.v3.exceptions import (
    InvalidSignatureError
)
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage,
    FlexMessage,
    FlexContainer
)
from linebot.v3.webhooks import (
    MessageEvent,
    TextMessageContent
)
import os

app = Flask(__name__)

configuration = Configuration(access_token=os.getenv('LINE_CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.getenv('LINE_CHANNEL_SECRET'))


elif user_msg == "小如如":
    flex_json = load_flex("case1/card_luru.json")

elif user_msg == "鍾師富":
    flex_json = load_flex("case2/card_chung.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        app.logger.info("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)
    return 'OK'


@app.route("/liff/<folder>/<name>")
def liff_page(folder, name):
    filename = f"liff_{name}.html"
    filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), folder, filename)
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), filename), "r", encoding="utf-8") as f:
        content = f.read()
    return content, 200, {"Content-Type": "text/html; charset=utf-8"}


@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    user_msg = event.message.text.strip()

    if user_msg == "小如如":
        flex_json = load_flex("card_luru.json")
        reply_msg = FlexMessage(
            alt_text="小如如的電子名片",
            contents=FlexContainer.from_dict(flex_json)
        )

    elif user_msg == "鍾師富":
    flex_json = load_flex("card_chung.json")
    reply_msg = FlexMessage(
        alt_text="鍾師富的電子名片",
        contents=FlexContainer.from_dict(flex_json)
    )
    
    else:
        reply_msg = TextMessage(text="小如如")

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
