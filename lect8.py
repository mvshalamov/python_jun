import io
import logging
import os
import random
from collections import deque

import matplotlib.pyplot as plt
import requests
from gtts import gTTS
from telegram import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (Updater, CommandHandler, RegexHandler,
                          ConversationHandler, CallbackQueryHandler)

TOKEN = os.environ.get('TOKEN', '')

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

markup = ReplyKeyboardMarkup([
    ['Как пионер!',
     'Мне надо подумать...']
], one_time_keyboard=True)

CHOOSING, NUMBER_SEND, DUMMY = range(3)


def start(bot, update):
    update.message.reply_text(
        "Привет! Я простой бот из туториала по Python программированию.\n"
        "И сегодня мы будем угадывать числа!\n"
        "Are you ready?",
        reply_markup=markup)

    return CHOOSING


def dummy(bot, update):
    update.message.reply_text(
        "Девчонка! Будь мужиком, сыграй в игру! В общем, если надумаешь - жми /start")

    return ConversationHandler.END


def number_create(bot, update, user_data):
    user_data['number'] = random.randint(1, 100)
    user_data['number_attempts'] = 0
    update.message.reply_text(
        "Я загадал число от 1 до 100. Попробуй его угадать!")

    return NUMBER_SEND


def number_send(bot, update, user_data):
    user_data['number_attempts'] += 1
    if user_data['number_attempts'] >= 10:
        update.message.reply_text("Вот ты дно, не смог с 10 попыток угадать")
        return ConversationHandler.END
    number = int(update.message.text)
    if number == user_data['number']:
        update.message.reply_text("Вот это да! Ты угадал всего с %s попыток!\n"
                                  "Жми /start чтобы сыграть еще" % user_data['number_attempts'])
        return ConversationHandler.END
    elif number > user_data['number']:
        update.message.reply_text("Число, которое я загадал меньше твоего!")
        return NUMBER_SEND
    else:
        update.message.reply_text("Число, которое я загадал больше твоего!")
        return NUMBER_SEND


def not_a_number(bot, update, user_data):
    user_data['number_attempts'] += 1
    if user_data['number_attempts'] >= 10:
        update.message.reply_text("Вот ты дно, не смог с 10 попыток угадать")
        return ConversationHandler.END
    update.message.reply_text("Ты впариваешь мне какую-то дичь. Но счетчик попыток я увеличил!")
    return NUMBER_SEND


def error(bot, update, error):
    logger.warning('Update "%s" caused error "%s"' % (update, error))


# Kitty

def kitty(bot, update):
    with open('kitty.jpg', 'rb') as f:
        update.message.reply_photo(f)


# Bitcoin

btc_deque = deque(maxlen=100)
current_price = None


def _get_btc():
    global current_price
    res = requests.get('https://api.cryptonator.com/api/ticker/btc-usd').json()
    price, change = float(res['ticker']['price']), float(res['ticker']['change'])

    # Save history
    if price != current_price:
        current_price = price
        btc_deque.append(price)

    return price, change


def bitcoin(bot, update):
    price, change = _get_btc()
    update.message.reply_text(
        f"Текущий курс BTC / USD: {price} "
        f"({'⬆️' if change > 0 else '⬇️'} "
        f"{abs(change)})"
    )


def bitcoin_graph(bot, update):
    _get_btc()

    plt.figure()
    items = [i for i in btc_deque]
    plt.plot(list(range(len(items))), items)
    plt.title("BTC / USD")
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)

    update.message.reply_photo(buf)


# Inline button


keyboard = InlineKeyboardMarkup([
    [
        InlineKeyboardButton('Мужской', callback_data='male'),
        InlineKeyboardButton('Женский', callback_data='female')
    ]
])


def sex_button(bot, update):
    update.message.reply_text('Выберите пол:', reply_markup=keyboard)


def sex_button_edit(bot, update):
    query = update.callback_query

    bot.edit_message_text(text="Выбрано: {}".format(query.data),
                          chat_id=query.message.chat_id,
                          message_id=query.message.message_id)


# TTS

def tts(bot, update):
    tts = gTTS(text=update.message.text[5:], lang='en', slow=True)
    buf = io.BytesIO()
    tts.write_to_fp(buf)
    buf.seek(0)

    update.message.reply_voice(buf)


def main():
    updater = Updater(TOKEN)
    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            CHOOSING: [
                RegexHandler('^Как пионер!$', number_create, pass_user_data=True),
                RegexHandler('^Мне надо подумать...$', dummy),
            ],
            NUMBER_SEND: [
                RegexHandler('^\d+$', number_send, pass_user_data=True),
                RegexHandler('^(\D*)$', not_a_number, pass_user_data=True)
            ],
        },
        fallbacks=[]
    )

    # Other types
    dp.add_handler(CommandHandler('kitty', kitty))

    # requests
    dp.add_handler(CommandHandler('bitcoin', bitcoin))
    dp.add_handler(CommandHandler('bitcoin_graph', bitcoin_graph))

    # inline mode
    dp.add_handler(CommandHandler('sex', sex_button))
    dp.add_handler(CallbackQueryHandler(sex_button_edit))

    # tts
    dp.add_handler(CommandHandler('tts', tts))

    dp.add_handler(conv_handler)

    dp.add_error_handler(error)

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
