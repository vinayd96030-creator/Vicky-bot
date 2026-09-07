import os, requests, telebot
BOT_TOKEN = os.environ.get("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

def fetch_yahoo(symbol):
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
        r = requests.get(url, headers={'User-Agent':'Mozilla/5.0'}, timeout=10)
        data = r.json()
        if not data['chart']['result']: return None
        meta = data['chart']['result'][0]['meta']
        return {'symbol':symbol, 'price':meta.get('regularMarketPrice'), 'high':meta.get('regularMarketDayHigh'), 'low':meta.get('regularMarketDayLow'), 'currency':meta.get('currency','INR')}
    except: return None

def get_any_price(raw):
    raw=raw.upper().replace(" ","")
    if "-USD" in raw:
        res=fetch_yahoo(raw)
        if res: return res
    for s in [f"{raw}.NS", raw, f"{raw}.BO"]:
        res=fetch_yahoo(s)
        if res and res['price']: return res
    return None

@bot.message_handler(commands=['price'])
def price_cmd(m):
    symbols=[p for p in m.text.replace("\n"," ").split() if p.lower()!="/price"]
    if not symbols:
        bot.send_message(m.chat.id, "Use: /price TCS INFY TSLA"); return
    bot.send_message(m.chat.id, f"Fetching {len(symbols)} stocks...")
    for raw in symbols:
        data=get_any_price(raw)
        if data and data['price']:
            curr="Rs" if data['currency']=="INR" else "$"
            bot.send_message(m.chat.id, f"📈 {data['symbol']}\n💰 {curr} {data['price']} | 🔺{data['high']} 🔻{data['low']}")
        else:
            bot.send_message(m.chat.id, f"❌ Not found: {raw}")

print("Bot Running 24/7...")
bot.polling()
