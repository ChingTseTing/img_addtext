# -*- coding: utf-8 -*-
#載入LineBot所需要的套件

from flask import Flask, request, abort
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)


from linebot.models import *
import sys, os
import pyimgur
import psycopg2
from PIL import Image , ImageDraw , ImageFont
from datetime import datetime
app = Flask(__name__)
from flask import send_from_directory

@app.route("/result/<token>")
def get_image_url(token):
    return send_from_directory('/tmp/', path=f'{token}.jpeg')

# LINE 聊天機器人的基本資料
# 必須放上自己的Channel Access Token
line_bot_api = LineBotApi(os.environ["CHANNEL_ACCESS_TOKEN"])
# 必須放上自己的Channel Secret
handler = WebhookHandler(os.environ["CHANNEL_SECRET"])
# 監聽所有來自 /callback 的 Post Request
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
