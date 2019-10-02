#!/usr/bin/python
# -*- coding: utf-8 -*-
from telethon import TelegramClient, events

from config import conf, help_msg
from direct_request import get_student_info
import logging


logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',
                    level=logging.WARNING)

# error text when invalid admission number format is given
INCORRECT_ADMISSION_ERROR = \
    "Incorrect admission number. \n" \
    "Please, use appropriate admission number which is 6 digits."

# bot = telebot.TeleBot(conf['telegram_token'])
bot = TelegramClient('bot',conf['api_id'], conf['api_hash']).start(bot_token=conf['telegram_token'])

#
# this function will catch the help command
# this command will print a little help to screen
# so users know what commands are available
#
@bot.on(events.NewMessage(pattern='/start'))
async def send_welcome(event):
    await event.reply(help_msg)


@bot.on(events.NewMessage)
async def show_campus_info(event):
    # remove '/campus' and get clean argument
    # i have to check event.text with "await event.text()"
    admission_number =  event.text
    # validate admission number (must be 6 digits)
    if len(admission_number) != 6 or not admission_number.isdigit():
        await event.reply(INCORRECT_ADMISSION_ERROR)
    else:
        error, campus_info = get_student_info(admission_number)
        await event.reply(campus_info)


if __name__ == '__main__':
    print('Polling...')
    bot.run_until_disconnected()