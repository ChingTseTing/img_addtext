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



def analysis_plot(record):
  tt =  get_stock( record[1] ,record[2] , record[3] )
  # Create subplots and mention plot grid size
  fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.03, subplot_titles=( record[1] , ''), row_width=[0.3, 0.3,1])
  # Plot OHLC on 1st row
  fig.add_trace(go.Candlestick(x=tt.index, open=tt["Open"], high=tt["High"],low=tt["Low"], close=tt["Close"], name="OHLC", showlegend=True ), row=1, col=1 )
  fig.add_trace(go.Scatter(x=tt.index, y=ta.SMA( np.array(tt['Close']) ,timeperiod=5), mode='lines' ,name='MA5', showlegend=True)  , row=1, col=1 )
  fig.add_trace(go.Scatter(x=tt.index, y=ta.SMA( np.array(tt['Close']) ,timeperiod=10), mode='lines' ,name='MA10', showlegend=True)  , row=1, col=1 )
  fig.add_trace(go.Scatter(x=tt.index, y=ta.SMA( np.array(tt['Close']) ,timeperiod=20), mode='lines' ,name='MA20', showlegend=True)  , row=1, col=1 )
  fig.add_trace(go.Scatter(x=tt.index, y=ta.SMA( np.array(tt['Close']) ,timeperiod=60), mode='lines' ,name='MA60', showlegend=True)  , row=1, col=1 )
  # Bar trace for volumes on 2nd row without legend
  fig.add_trace(go.Bar(x=tt.index, y=tt['Volume'], showlegend=False), row=2, col=1)
  # plot index
  if record[4]=="RSI":
    fig.add_trace(go.Scatter(x=tt.index, y=ta.RSI(tt['Close']), mode='lines' ,name=record[4], showlegend=True)  , row=3, col=1 ) #ta.RSI( np.array(tt['Close']) ,timeperiod=14)
    fig['layout']['yaxis3']['title']='RSI' 
  if record[4]=="KD":
    K,D = ta.STOCH(tt['High'], tt['Low'], tt['Close'])
    fig.add_trace(go.Scatter(x=tt.index, y=K, mode='lines' ,name='K', showlegend=True)  , row=3, col=1 ) #ta.RSI( np.array(tt['Close']) ,timeperiod=14)
    fig.add_trace(go.Scatter(x=tt.index, y=D, mode='lines' ,name='D', showlegend=True)  , row=3, col=1 ) #ta.RSI( np.array(tt['Close']) ,timeperiod=14)
    fig['layout']['yaxis3']['title']='KD'
  if record[4]=="MACD":
    MACD_DIF , MACD_SIGNAL, MACD_BAR = ta.MACD(tt['Close'])
    fig.add_trace(go.Scatter(x=tt.index, y=MACD_DIF, mode='lines' ,name='MACD_DIF', showlegend=True)  , row=3, col=1 ) #ta.RSI( np.array(tt['Close']) ,timeperiod=14)
    fig.add_trace(go.Scatter(x=tt.index, y=MACD_SIGNAL, mode='lines' ,name='MACD_SIGNAL', showlegend=True)  , row=3, col=1 ) #ta.RSI( np.array(tt['Close']) ,timeperiod=14)
    fig.add_trace(go.Bar(x=tt.index, y=MACD_BAR,name='MACD_BAR', showlegend=True)  , row=3, col=1 ) #ta.RSI( np.array(tt['Close']) ,timeperiod=14)
    fig['layout']['yaxis3']['title']='MACD'

  fig['layout']['yaxis']['title']='Price'
  fig['layout']['yaxis2']['title']='Volume'

  fig.update_layout(margin=dict(l=30, r=30, t=30, b=30) , template='plotly_dark',paper_bgcolor ='rgb(10,10,10)')
  # Do not show OHLC's rangeslider plot 
  fig.update(layout_xaxis_rangeslider_visible=False)
  # save image
  fig.write_image("send.png")
  CLIENT_ID = "08680019f3643c6"  #"TingChingTse"
  PATH = "send.png"
  im = pyimgur.Imgur(CLIENT_ID)
  uploaded_image = im.upload_image(PATH, title="Uploaded with PyImgur")
  return uploaded_image.link





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
  local_save = './Image/' + event.message.id + '.png'
  with open(local_save, 'wb') as fd:
    for chenk in SendImage.iter_content():
      fd.write(chenk)

  tmp = Image.open(    local_save   )
  draw = ImageDraw.Draw(tmp)
  font = ImageFont.truetype( font = "Times New Roman.ttf"  , size = 20 )
  draw.text( xy=( 0.75*tmp.size[0] , 0.8*tmp.size[1] ) , text = 'Iris Chong' , fill = (255, 255 , 255) , font=font )
  tmp.save(  local_save  )
  
  img_url = img_getlink(local_save)

	line_bot_api.reply_message(event.reply_token, ImageSendMessage(original_content_url=img_url, preview_image_url=img_url))



  # message_content = line_bot_api.get_message_content(event.message.id)

	# SendImage = line_bot_api.get_message_content(event.message.id)
	# local_save = './static/' + event.message.id + '.png'
	# with open(local_save, 'wb') as fd:
	# 	for chenk in SendImage.iter_content():
	# 		fd.write(chenk)


  line_bot_api.reply_message(event.reply_token, ImageSendMessage(original_content_url = ngrok_url + "/static/" + event.message.id + ".png", preview_image_url = ngrok_url + "/static/" + event.message.id + ".png"))
  # line_bot_api.reply_message(event.reply_token, TextSendMessage(text=os.getcwd() )  )


#主程式
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
