#!/usr/bin/python
# -*- coding: utf-8 -*-
import telebot

from config import conf, help_msg
from direct_request import get_student_info

# error text when invalid admission number format is given
INCORRECT_ADMISSION_ERROR = \
    "Incorrect admission number. \n" \
    "Please, use appropriate admission number which is 6 digits."

bot = telebot.TeleBot(conf['telegram_token'])


#
# this function will catch the help command
# this command will print a little help to screen
# so users know what commands are available
#
@bot.message_handler(commands=['help', 'start'])
def send_welcome(message):
    bot.send_message(message.chat.id, help_msg, parse_mode='Markdown')


@bot.message_handler(commands=['campus'])
def show_campus_info(message):
    # remove '/campus' and get clean argument
    admission_number = message.text.strip()[7:].strip()

    # validate admission number (must be 6 digits)
    if len(admission_number) != 6 or not admission_number.isdigit():
        bot.reply_to(message, INCORRECT_ADMISSION_ERROR)
    else:
        error, campus_info = get_student_info(admission_number)
        bot.reply_to(message, campus_info)


if __name__ == '__main__':
    print('Polling...')
    bot.polling()
