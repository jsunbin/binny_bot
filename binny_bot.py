import ssl
import json
import yaml
import kworkday
import requests
import urllib.request
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from telegram.ext import Updater, MessageHandler, Filters, CommandHandler

ssl._create_default_https_context = ssl._create_unverified_context

_config = 'bot_config.yaml'
with open(_config, encoding='utf-8') as f:
    config = yaml.load(f, Loader=yaml.SafeLoader)

my_token = config["params"]["my_token"]
api_key = config["params"]["google"]["api_key"]
cx = config["params"]["google"]["search_engine_id"]

updater = Updater(my_token)


def help_bot(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="도와줘?")


def message_control(update, context):
    input_message = update.message.text
    print(input_message)
    tired_message_to_handle_list = ["힘들다", "힘들어", "피곤해"]
    hungry_message_to_handle_list = ["배고파"]
    fucking_message_to_handle_list = ["ㅗ"]

    if input_message in tired_message_to_handle_list:
        context.bot.sendPhoto(chat_id=update.effective_chat.id, photo=open(config["params"]["pics"]["tired"], 'rb'))

    elif input_message in hungry_message_to_handle_list:
        context.bot.sendPhoto(chat_id=update.effective_chat.id, photo=open(config["params"]["pics"]["hungry"], 'rb'))

    elif input_message in fucking_message_to_handle_list:
        context.bot.sendMessage(chat_id=update.effective_chat.id, text="""
        ㅗㅗㅗㅗㅗㅗㅗㅗㅗㅗㅗㅗㅗㅗㅗㅗㅗㅗㅗㅗㅗㅗㅗㅗㅗㅗㅗㅗㅗㅗㅗㅗㅗㅗㅗㅗㅗㅗㅗㅗㅗㅗㅗㅗㅗㅗㅗㅗㅗㅗㅗㅗㅗㅗㅗㅗㅗㅗㅗㅗㅗㅗㅗㅗㅗㅗㅗㅗㅗㅗㅗㅗㅗㅗㅗㅗㅗㅗㅗㅗㅗㅗㅗㅗㅗㅗㅗㅗㅗㅗㅗㅗㅗㅗㅗㅗㅗㅗㅗㅗㅗㅗㅗㅗㅗㅗㅗㅗㅗㅗㅗㅗㅗㅗㅗㅗㅗㅗㅗㅗㅗㅗㅗㅗㅗㅗㅗㅗㅗㅗㅗ
        """)


def pay_day(update, context):
    today_date = datetime.today().date()
    this_month_25 = today_date.replace(day=25)

    # 주말 게산
    weekday_num = this_month_25.weekday()

    while True:
        if this_month_25.weekday() == 5 or this_month_25.weekday() == 6 or kworkday.get_today_holiday(
                this_month_25) is True:
            this_month_25 = this_month_25 - relativedelta(days=1)
        else:
            print(this_month_25)
            break

    # 월급날까지 남은 날짜 계산
    if today_date < this_month_25:
        d_day = this_month_25 - today_date
        d_day = str(d_day).replace(' days, 0:00:00', '')
    elif today_date == this_month_25:
        d_day = 0
    else:
        next_month_25 = today_date.replace(day=25) + relativedelta(months=1)
        d_day = today_date - next_month_25
        d_day = str(d_day).replace(' days, 0:00:00', '').replace('-', '')

    if d_day != 0:
        message_to_send = f"{d_day}일 남았용용ㅠㅠ\n이번달 월급은 {this_month_25.day}일"
    else:
        message_to_send = "🤩오늘이 월급날!!"

    context.bot.sendMessage(chat_id=update.effective_chat.id, text=message_to_send)


def work_(update, context):
    now = datetime.now().strftime("%m월 %d일 %H:%M:%S 출근완료!")
    home_time = datetime.now() + timedelta(hours=9)
    home_time = home_time.strftime("🫠퇴근 시간: %H:%M:%S")

    context.bot.sendMessage(chat_id=update.effective_chat.id, text=now + '\n' +home_time)


def search_image(update, context):
    search_keyword = context.args[0]
    url = f'https://customsearch.googleapis.com/customsearch/v1?cx={cx}&searchType=image&imgColorType=color&q={search_keyword}&key={api_key}'
    res = requests.get(url)
    if res.status_code == 200:
        google_search_data = json.loads(res.text)
        img_url = google_search_data["items"][0]["image"]["thumbnailLink"]
        content_url = google_search_data["items"][0]["image"]["contextLink"]

        urllib.request.urlretrieve(img_url, 'search.jpg')

        context.bot.sendPhoto(chat_id=update.effective_chat.id, photo=open('search.jpg', 'rb'))
        context.bot.sendMessage(chat_id=update.effective_chat.id, text=content_url)

        print(img_url)
        print(content_url)


def main():
    message_handler = MessageHandler(Filters.text & (~Filters.command), message_control)
    pay_day_handler = CommandHandler("payday", pay_day)
    help_handler = CommandHandler('help', help_bot)
    work_handler = CommandHandler('work', work_)
    search_handler = CommandHandler('p', search_image)

    updater.dispatcher.add_handler(message_handler)
    updater.dispatcher.add_handler(help_handler)
    updater.dispatcher.add_handler(pay_day_handler)
    updater.dispatcher.add_handler(work_handler)
    updater.dispatcher.add_handler(search_handler)

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
