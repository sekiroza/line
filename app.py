from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import openai
import os

app = Flask(__name__)

openai.api_key = os.getenv('OPENAI_API_KEY')
line_bot_api = LineBotApi(os.getenv('CHANNEL_ACCESS_TOKEN'))
handler1 = WebhookHandler(os.getenv('CHANNEL_SECRET'))

# 設定訊息計數器
openai_message_counter = 0

@app.route('/callback', methods=['POST'])
def callback():
    global openai_message_counter
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    try:
        handler1.handle(body, signature)
        # 每當接收到 OpenAI 的回應，計數器就加1
        openai_message_counter += 1
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@app.route('/counter', methods=['GET'])
def get_counter():
    return f'OpenAI 共傳送了 {openai_message_counter} 則訊息'

@handler1.add(MessageEvent, message=TextMessage)
def handle_message(event):
    global openai_message_counter
    text1 = event.message.text
    
    response = openai.ChatCompletion.create(
        messages=[
            {"role": "user", "content": text1}
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
        # 在回應中包含 OpenAI 傳送的訊息數量
        ret += f"\nOpenAI 共傳送了 {openai_message_counter} 則訊息"
    except:
        ret = '發生錯誤！'
    
    # 回覆訊息
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=ret))

if __name__ == '__main__':
    app.run()
