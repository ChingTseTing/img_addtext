
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
  
  img_url = img_getlink(  local_save)#f'https://{os.getenv("YOUR_HEROKU_APP_NAME")}.herokuapp.com/result/{file_name}'


#   img_url = img_getlink(local_save)
  line_bot_api.reply_message(event.reply_token, ImageSendMessage(original_content_url=img_url, preview_image_url=img_url))

