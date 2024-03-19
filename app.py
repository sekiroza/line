from flask import Flask
app = Flask(__name__)

from flask import request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import openai
import os

openai.api_key = os.getenv('OPENAI_API_KEY')
line_bot_api = LineBotApi(os.getenv('CHANNEL_ACCESS_TOKEN'))
handler1 = WebhookHandler(os.getenv('CHANNEL_SECRET'))

# 設定訊息計數器
message_counter = 0

@app.route('/callback', methods=['POST'])
def callback():
    global message_counter
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    try:
        handler1.handle(body, signature)
        # 每當接收到一條訊息，計數器就加1
        message_counter += 1
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler1.add(MessageEvent, message=TextMessage)
def handle_message(event):
    global message_counter
    text1 = event.message.text
    
    # 在對話文本中間接地表達特定的個性
    text_with_personality = f"我是一個熱愛運動的人，喜歡聊天和激勵他人！\n{text1}"
    
    response = openai.ChatCompletion.create(
        messages=[
            {"role": "user", "content": text_with_personality}
        ],
        model="gpt-3.5-turbo-0125",
        temperature=0.5,
    )
    try:
        ret = response['choices'][0]['message']['content'].strip()
        # 加入運動員個性的回應
        ret = f"🏆 {ret} 🏅"  # 添加表情符號以表示運動員個性
        # 添加運動專業術語
        ret += "\n堅持突破極限，永不放棄！ 💪"
        ret += "\n記住，這不是關於勝利或失敗，而是關於在場上盡力而為。 🌟"
    except:
        ret = '發生錯誤！'
    
    # 回覆訊息
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=ret))

if __name__ == '__main__':
    app.run()
