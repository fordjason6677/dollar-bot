import telebot
from telebot import types
import requests
import os
import time
import traceback

BOT_TOKEN = os.getenv("BOT_TOKEN")
API_TOKEN = os.getenv("API_TOKEN")

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="Markdown")

def get_data(data_type="currencies"):
    try:
        url = f"https://api.alanchand.com/?type={data_type}&token={API_TOKEN}"
        r = requests.get(url, timeout=12)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f"Error fetching {data_type}:", e)
        return None

def format_number(num):
    try:
        return f"{int(num):,}".replace(",", "٬")
    except:
        return str(num)

def main_menu():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("💵 ارزها", callback_data="currencies"),
        types.InlineKeyboardButton("🥇 طلا و سکه", callback_data="golds"),
        types.InlineKeyboardButton("₿ ارز دیجیتال", callback_data="crypto"),
        types.InlineKeyboardButton("🔄 بروزرسانی", callback_data="refresh"),
        types.InlineKeyboardButton("🌐 منبع قیمت‌ها", url="https://alanchand.com")
    )
    return markup

def back_button():
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔙 بازگشت به منو", callback_data="home"))
    return markup

@bot.message_handler(commands=['start', 'help'])
def start(message):
    text = """
🤖 *ربات حرفه‌ای قیمت لحظه‌ای*

قیمت‌های بازار آزاد ارز، طلا و ارز دیجیتال

از دکمه‌های زیر استفاده کنید:
"""
    bot.send_message(message.chat.id, text, reply_markup=main_menu())

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    chat_id = call.message.chat.id
    message_id = call.message.message_id

    if call.data == "home" or call.data == "refresh":
        text = """
🤖 *ربات حرفه‌ای قیمت لحظه‌ای*

قیمت‌های بازار آزاد ارز، طلا و ارز دیجیتال
"""
        bot.edit_message_text(text, chat_id, message_id, reply_markup=main_menu())
        bot.answer_callback_query(call.id)
        return

    if call.data == "currencies":
        data = get_data("currencies")
        if not data:
            bot.answer_callback_query(call.id, "خطا در دریافت اطلاعات", show_alert=True)
            return

        text = "💵 *قیمت ارزهای مهم*\n\n"
        important = ["usd", "eur", "gbp", "aed", "try", "cad", "aud", "cny"]
        for key in important:
            if key in data:
                item = data[key]
                text += f"*{item['name']}*\n"
                text += f"🟢 فروش: `{format_number(item['sell'])}`\n"
                text += f"🔴 خرید: `{format_number(item['buy'])}`\n"
                text += f"📊 تغییر: `{item.get('dayChange', '-')}%`\n\n"

        text += f"⏰ `{data['usd']['updated_at']}`"
        bot.edit_message_text(text, chat_id, message_id, reply_markup=back_button())
        bot.answer_callback_query(call.id)

    elif call.data == "golds":
        data = get_data("golds")
        if not data:
            bot.answer_callback_query(call.id, "خطا در دریافت اطلاعات", show_alert=True)
            return

        text = "🥇 *قیمت طلا و سکه*\n\n"
        # نمایش چند مورد مهم
        count = 0
        for key, item in data.items():
            if count >= 8:
                break
            name = item.get('name', key)
            sell = item.get('sell') or item.get('price')
            if sell:
                text += f"*{name}*: `{format_number(sell)}` تومان\n"
                count += 1

        bot.edit_message_text(text, chat_id, message_id, reply_markup=back_button())
        bot.answer_callback_query(call.id)

    elif call.data == "crypto":
        data = get_data("crypto")
        if not data:
            bot.answer_callback_query(call.id, "خطا در دریافت اطلاعات", show_alert=True)
            return

        text = "₿ *قیمت ارزهای دیجیتال*\n\n"
        important_crypto = ["btc", "eth", "usdt", "bnb", "xrp", "sol", "doge"]
        for key in important_crypto:
            if key in data:
                item = data[key]
                name = item.get('name', key.upper())
                price = item.get('sell') or item.get('price') or item.get('usd')
                if price:
                    text += f"*{name}*: `{format_number(price)}`\n"

        bot.edit_message_text(text, chat_id, message_id, reply_markup=back_button())
        bot.answer_callback_query(call.id)

print("ربات پیشرفته شروع به کار کرد...")
while True:
    try:
        bot.infinity_polling(timeout=25, long_polling_timeout=25)
    except Exception as e:
        print("Error:", e)
        traceback.print_exc()
        time.sleep(10)
