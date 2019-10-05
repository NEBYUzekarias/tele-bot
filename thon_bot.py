#!/usr/bin/python
# -*- coding: utf-8 -*-
from telethon import TelegramClient, events

from config import conf, help_msg
from async_direct_request import get_student_info
import logging


logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',
                    level=logging.WARNING)

# error text when invalid admission number format is given
INCORRECT_ADMISSION_ERROR = \
    "Incorrect admission number. \n" \
    "Please, use appropriate admission number which is 6 digits."
HELP_MSG = "Just send me your admission number to know which university you are assigned.\n\n" \
    "For more exciting hot news and recommendations for new university students, click the link below and join our channel\n" \
    "@campus_recommendations"

JOIN_MSG = "For more exciting hot news and recommendations for new university students, click the link below and join our channel\n" \
    "@campus_recommendations"

api_id = '925419'
api_hash = '90603f7d0fb71c4a41a191248a4306e7'
bot_token = '863015219:AAECu1DFH8PJNagyaWViZslZJrqhxuQdkzk'
# bot = telebot.TeleBot(conf['telegram_token'])
bot = TelegramClient('mdebabot', api_id, api_hash).start(
    bot_token=bot_token)

#
# this function will catch the help command
# this command will print a little help to screen
# so users know what commands are available
#
@bot.on(events.NewMessage(pattern='/start'))
async def send_welcome(event):
    await event.reply(HELP_MSG)


@bot.on(events.NewMessage)
async def show_campus_info(event):
    # remove '/campus' and get clean argument
    # i have to check event.text with "await event.text()"
    try:
        admission_number = event.text
        # validate admission number (must be 6 digits)
        if len(admission_number) < 6 or len(admission_number) > 8 or not admission_number.isdigit():
            await event.reply(INCORRECT_ADMISSION_ERROR)
        else:
            error, campus_info = await get_student_info(admission_number)
            await event.reply(campus_info)
            await event.reply(JOIN_MSG)
    except:
        logging.warning('Donot know what happened')


if __name__ == '__main__':
    print('Polling...')
    bot.run_until_disconnected()
