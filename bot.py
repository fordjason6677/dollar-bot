import telebot
from telebot import types
import requests
import time
import traceback
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
API_TOKEN = os.getenv("API_TOKEN")
API_URL = f"https://api.alanchand.com/?type=currencies&token={API_TOKEN}"

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="Markdown")

def get_currency_data():
    try:
        r = requests.get(API_URL, timeout=15)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print("API Error:", e)
        return None

def format_number(num):
    return f"{num:,}".replace(",", "٬")

def create_main_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        types.KeyboardButton("💵 دلار آمریکا"),
        types.KeyboardButton("💶 یورو"),
        types.KeyboardButton("💷 پوند"),
        types.KeyboardButton("🇦🇪 درهم"),
        types.KeyboardButton("🇹🇷 لیر"),
        types.KeyboardButton("🔄 همه ارزها"),
        types.KeyboardButton("ℹ️ راهنما")
    )
    return markup

@bot.message_handler(commands=['start', 'help'])
def start(message):
    text = """🤖 *ربات قیمت لحظه‌ای ارز*

از دکمه‌های پایین استفاده کن."""
    bot.send_message(message.chat.id, text, reply_markup=create_main_keyboard())

@bot.message_handler(func=lambda m: m.text in ["💵 دلار آمریکا", "/dollar"])
def dollar(message):
    data = get_currency_data()
    if not data or "usd" not in data:
        bot.reply_to(message, "❌ خطا در دریافت قیمت.")
        return
    usd = data["usd"]
    text = f"""💵 *دلار آمریکا*

🟢 فروش: `{format_number(usd['sell'])}` تومان
🔴 خرید: `{format_number(usd['buy'])}` تومان

📈 سقف: `{format_number(usd['high'])}`
📉 کف: `{format_number(usd['low'])}`
📊 تغییر: `{usd['dayChange']}%`

⏰ `{usd['updated_at']}`"""
    bot.send_message(message.chat.id, text)

@bot.message_handler(func=lambda m: m.text in ["💶 یورو", "/euro"])
def euro(message):
    data = get_currency_data()
    if not data or "eur" not in data:
        bot.reply_to(message, "❌ خطا در دریافت قیمت.")
        return
    eur = data["eur"]
    text = f"""💶 *یورو*

🟢 فروش: `{format_number(eur['sell'])}` تومان
🔴 خرید: `{format_number(eur['buy'])}` تومان
📊 تغییر: `{eur['dayChange']}%`
⏰ `{eur['updated_at']}`"""
    bot.send_message(message.chat.id, text)

@bot.message_handler(func=lambda m: m.text in ["💷 پوند"])
def gbp(message):
    data = get_currency_data()
    if not data or "gbp" not in data:
        bot.reply_to(message, "❌ خطا.")
        return
    g = data["gbp"]
    text = f"""💷 *پوند*

🟢 فروش: `{format_number(g['sell'])}` تومان
🔴 خرید: `{format_number(g['buy'])}` تومان"""
    bot.send_message(message.chat.id, text)

@bot.message_handler(func=lambda m: m.text in ["🇦🇪 درهم"])
def aed(message):
    data = get_currency_data()
    if not data or "aed" not in data:
        bot.reply_to(message, "❌ خطا.")
        return
    a = data["aed"]
    text = f"""🇦🇪 *درهم*

🟢 فروش: `{format_number(a['sell'])}` تومان
🔴 خرید: `{format_number(a['buy'])}` تومان"""
    bot.send_message(message.chat.id, text)

@bot.message_handler(func=lambda m: m.text in ["🇹🇷 لیر"])
def try_currency(message):
    data = get_currency_data()
    if not data or "try" not in data:
        bot.reply_to(message, "❌ خطا.")
        return
    t = data["try"]
    text = f"""🇹🇷 *لیر ترکیه*

🟢 فروش: `{format_number(t['sell'])}` تومان
🔴 خرید: `{format_number(t['buy'])}` تومان"""
    bot.send_message(message.chat.id, text)

@bot.message_handler(func=lambda m: m.text in ["🔄 همه ارزها", "/all"])
def all_currencies(message):
    data = get_currency_data()
    if not data:
        bot.reply_to(message, "❌ خطا در دریافت اطلاعات.")
        return
    keys = ["usd", "eur", "gbp", "aed", "try", "cad", "aud"]
    text = "📊 *قیمت‌های لحظه‌ای*\n\n"
    for k in keys:
        if k in data:
            item = data[k]
            text += f"• *{item['name']}*: `{format_number(item['sell'])}` / `{format_number(item['buy'])}`\n"
    text += f"\n⏰ `{data['usd']['updated_at']}`"
    bot.send_message(message.chat.id, text)

@bot.message_handler(func=lambda m: m.text == "ℹ️ راهنما")
def help_msg(message):
    bot.send_message(message.chat.id, "ربات روی سرور رایگان اجرا می‌شود.")

print("ربات شروع به کار کرد...")
while True:
    try:
        bot.infinity_polling(timeout=25, long_polling_timeout=25)
    except Exception as e:
        print("خطا:", e)
        traceback.print_exc()
        time.sleep(10)
