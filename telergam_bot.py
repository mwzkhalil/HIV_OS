import telebot
from config import apikey
import requests


TOKEN = apikey
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
	bot.reply_to(message, "Howdy, how are you doing?")

@bot.message_handler()
def echo_all(message):
  print(message)

  user = message.from_user.username
  prompts = message.text
  prompt = prompts.replace("/chat","")
  headers={'Content-Type': 'application/json'}
  body = {
    "user_id":user,
    "prompt":prompt

  }
  r = requests.post('http://127.0.0.1:5000/chat',headers=headers,json=body)
  ans = r.json()
  print(ans)
  anss = ans['message']['content']
  # print(ans)
  bot.reply_to(message, anss)



@bot.message_handler(commands=['help'])
def echo_all(message):
  msg = "Hi! \n\n I'am ReplyTensor your assistant.\n\nTo ask me anything  use /chat command. \n\nHappy Mining! :)"
  bot.reply_to(message, msg)



bot.infinity_polling()