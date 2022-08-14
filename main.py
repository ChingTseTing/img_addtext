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


def access_database():    
    DATABASE_URL = os.environ["DATABASE_URL"]
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cursor = conn.cursor()
    return conn, cursor

####  CallDatabase  TABLE_NAME(a string) replace user_dualtone_settings
def init_table(TABLE_NAME):
    conn, cursor = access_database()
    postgres_table_query = "SELECT tablename FROM pg_catalog.pg_tables WHERE schemaname != 'pg_catalog' AND schemaname != 'information_schema'"
    cursor.execute(postgres_table_query)
    table_records = cursor.fetchall()
    table_records = [i[0] for i in table_records]

    if TABLE_NAME not in table_records:

        create_table_query = """CREATE TABLE """+ TABLE_NAME +""" (
            user_id VARCHAR ( 50 ) PRIMARY KEY,
            problem VARCHAR ( 20 ) NOT NULL,
            stock VARCHAR ( 20 ) NOT NULL,
            period VARCHAR ( 20 ) NOT NULL,
            interval VARCHAR ( 20 ) NOT NULL,
            indicator VARCHAR ( 20 ) NOT NULL,
            model VARCHAR ( 20 ) NOT NULL,
            result_model VARCHAR ( 50 ) NOT NULL,
            predicted_price VARCHAR ( 50 ) NOT NULL
        );"""
        cursor.execute(create_table_query)
        conn.commit()
    return True

def drop_table(TABLE_NAME):
  conn, cursor = access_database()
  delete_table_query = '''DROP TABLE IF EXISTS ''' + TABLE_NAME
  cursor.execute(delete_table_query)
  conn.commit()
  cursor.close()
  conn.close()
  return True


def init_record(user_id,   problem  ,TABLE_NAME ):
    conn, cursor = access_database()
    table_columns = '(user_id,  problem ,stock, period, interval, indicator ,model, result_model , predicted_price)'
    postgres_insert_query = "INSERT INTO "+ TABLE_NAME + f" {table_columns} VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)"
    record = (user_id, problem ,'2330.TW', '3y', '1d', 'MACD','LSTM' ,'0','0')
    cursor.execute(postgres_insert_query, record)
    conn.commit()
    cursor.close()
    conn.close()
    return record

def check_record(user_id, TABLE_NAME):
    conn, cursor = access_database()
    postgres_select_query = "SELECT * FROM "+ TABLE_NAME + f" WHERE user_id = '{user_id}';"
    cursor.execute(postgres_select_query)
    user_settings = cursor.fetchone()
    return user_settings

def find_record(user_id, TABLE_NAME, col_name):
    conn, cursor = access_database()
    postgres_select_query = "SELECT "+col_name+" FROM "+ TABLE_NAME + f" WHERE user_id = '{user_id}';"
    cursor.execute(postgres_select_query)
    user_settings = cursor.fetchone()
    return user_settings

def update_record(user_id, col, value, TABLE_NAME):
    conn, cursor = access_database()
    postgres_update_query = "UPDATE " + TABLE_NAME +f" SET {col} = %s WHERE user_id = %s"
    cursor.execute(postgres_update_query, (value, user_id))
    conn.commit()
    postgres_select_query = "SELECT * FROM "+ TABLE_NAME + f" WHERE user_id = '{user_id}';"
    cursor.execute(postgres_select_query)
    user_settings = cursor.fetchone()
    cursor.close()
    conn.close()
    return user_settings



def img_getlink( imgpath):
	im = pyimgur.Imgur("08680019f3643c6")
	upload_image = im.upload_image(imgpath, title="Uploaded with PyImgur")
	return upload_image.link


# 文字事件
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
  message = TextSendMessage(text=event.message.text)
  line_bot_api.reply_message(event.reply_token, TextSendMessage(text=os.getcwd() )  )
# 照片事件   
@handler.add(MessageEvent, message=ImageMessage)
def handle_image(event):
  SendImage = line_bot_api.get_message_content(event.message.id)
  file_name = event.reply_token
  local_save =  f"/tmp/{file_name}.jpeg" # '/tmp/myimg.png'
  with open(local_save, 'wb') as fd:
    for chenk in SendImage.iter_content():
      fd.write(chenk)

  tmp = Image.open(    local_save   )
  draw = ImageDraw.Draw(tmp)
  font = ImageFont.truetype( font = "Times New Roman.ttf"  , size = 20 )
  draw.text( xy=( 0.75*tmp.size[0] , 0.8*tmp.size[1] ) , text = 'Iris Chong' , fill = (255, 255 , 255) , font=font )
  tmp.save(  local_save  )
  
  img_url = f'https://{os.getenv("YOUR_HEROKU_APP_NAME")}.herokuapp.com/result/{file_name}'


#   img_url = img_getlink(local_save)
  line_bot_api.reply_message(event.reply_token, ImageSendMessage(original_content_url=img_url, preview_image_url=img_url))




#主程式
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
