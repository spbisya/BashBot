import logging
import random

import lxml
import telegram
import requests
from lxml import html
import re
from telegram.ext import CommandHandler, Updater, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ForceReply


def getMaxPageAndNumber():
    page = requests.get('http://bash.im')
    maxPage = re.search('max="...."', page.content.decode('CP1251').replace("<br>", "\n"))
    return int(maxPage.group(0).replace("max=\"", "").replace("\"", ""))


def postNews(bot, chat_id):
    page = requests.get('http://bash.im/')
    dom = lxml.html.fromstring(page.content.decode('CP1251').replace("<br>", "\n"))
    # tree = html.fromstring(page.text)
    posts = dom.xpath('//div[@class="text"]/text()')
    numbers = dom.xpath('//a[@class="id"]/text()')
    for number in range(0, 10):
        stri = createMsg(numbers[9 - number].replace("#", ""),
                         posts[9 - number])
        send(bot, stri, chat_id)


def createMsg(text, number):
    return "*Цитата* [#" + text + "](http://bash.im/quote/" + text + ")\n\n" + number + "\n"


def send(bot, text, chat_id):
    bot.sendMessage(chat_id=chat_id, text=text,
                    parse_mode=telegram.ParseMode.MARKDOWN, disable_web_page_preview=True, disable_notification=True)


def sendRandom(bot, text, chat_id):
    keyboard = [[InlineKeyboardButton("More", callback_data='1', message=str(chat_id))]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    bot.sendMessage(chat_id=chat_id, text=text,
                    parse_mode=telegram.ParseMode.MARKDOWN, disable_web_page_preview=True, disable_notification=True,
                    reply_markup=reply_markup)


def button(bot, update):
    getRandPost(bot, update.callback_query.message.chat.id)


def getRandPost(bot, chat_id):
    page = requests.get('http://bash.im/index/' + str(random.randrange(1, getMaxPageAndNumber())))
    dom = lxml.html.fromstring(page.content.decode('CP1251').replace("<br>", "\n"))
    # tree = html.fromstring(page.text)
    posts = dom.xpath('//div[@class="text"]/text()')
    numbers = dom.xpath('//a[@class="id"]/text()')
    num = random.randrange(0, len(numbers) - 1)
    sendRandom(bot, createMsg(numbers[num].replace("#", ""), posts[num]), chat_id)


def randomf(bot, update):
    getRandPost(bot, update.message.chat_id)


def new(bot, update):
    postNews(bot, update.message.chat_id)


def start(bot, update):
    keyboard = [[InlineKeyboardButton("Да будет рандом!", callback_data='1', message=str(update.message.chat_id))]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    bot.sendMessage(chat_id=update.message.chat_id,
                    text="Привет, предлагаю начать с последних новостей\n/new\nили сразу получить случайную цитату",
                    parse_mode=telegram.ParseMode.MARKDOWN, disable_web_page_preview=True, disable_notification=True,
                    reply_markup=reply_markup)


def error(bot, update, error):
    logging.warning('Update "%s" caused error "%s"' % (update, error))


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

updater = Updater("234300031:AAGCWAR4xTlq-52l9H3Kqtmlet2iTjcd5vw")

# return random post from random page
updater.dispatcher.add_handler(CommandHandler('random', randomf))
# return new 10 posts
updater.dispatcher.add_handler(CommandHandler('new', new))
updater.dispatcher.add_handler(CommandHandler('start', start))

updater.dispatcher.add_handler(CallbackQueryHandler(button))
updater.dispatcher.add_error_handler(error)
# Start the Bot
updater.start_polling()

# Run the bot until the user presses Ctrl-C or the process receives SIGINT,
# SIGTERM or SIGABRT
updater.idle()
