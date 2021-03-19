from flask import Flask, request, abort
import os

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,ImageSendMessage,ImageMessage
)

app = Flask(__name__,static_folder="tmp")

#環境変数取得
YOUR_CHANNEL_ACCESS_TOKEN = os.environ["YOUR_CHANNEL_ACCESS_TOKEN"]
YOUR_CHANNEL_SECRET = os.environ["YOUR_CHANNEL_SECRET"]

line_bot_api = LineBotApi(YOUR_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(YOUR_CHANNEL_SECRET)

@app.route("/")
def hello_world():
    return "hello world!"

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    if event.message.text != "画像":
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=event.message.text))
    if event.message.text == "画像":
        line_bot_api.reply_message(
        event.reply_token,
        ImageSendMessage(original_content_url='https://kosakae256-testapp-linebot.herokuapp.com/tmp/testimg.jpg',preview_image_url="https://kosakae256-testapp-linebot.herokuapp.com/tmp/testimg.jpg"))

@handler.add(MessageEvent, message=ImageMessage)
def handle_image(event):
    message_id = event.message.id

    # message_idから画像のバイナリデータを取得
    message_content = line_bot_api.get_message_content(message_id)

    with open(Path(f"tmp/{message_id}.jpg").absolute(), "wb") as f:
        # バイナリを1024バイトずつ書き込む
        for chunk in message_content.iter_content():
            f.write(chunk)
    line_bot_api.reply_message(
    event.reply_token,
    ImageSendMessage(original_content_url=f'https://kosakae256-testapp-linebot.herokuapp.com/tmp/{message_id}.jpg',preview_image_url=f"https://kosakae256-testapp-linebot.herokuapp.com/tmp/{message_id}.jpg"))

if __name__ == "__main__":
#    app.run()
    port = int(os.getenv("PORT"))
    app.run(host="0.0.0.0", port=port)
