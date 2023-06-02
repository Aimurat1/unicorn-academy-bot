#!/usr/bin/env python
# pylint: disable=C0116,W0613
# This program is dedicated to the public domain under the CC0 license.

"""
Simple Bot to send timed Telegram messages.

This Bot uses the Updater class to handle the bot and the JobQueue to send
timed messages.

First, a few handler functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.

Usage:
Basic Alarm Bot example, sends a message after a set time.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import logging

from telegram import ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup, Update, ForceReply, KeyboardButton, ReplyKeyboardMarkup,InputMediaPhoto, ParseMode
from telegram.ext import Defaults, InvalidCallbackData, PicklePersistence, CallbackQueryHandler, Updater, CommandHandler, MessageHandler, Filters, CallbackContext, ConversationHandler
from ptbcontrib.ptb_sqlalchemy_jobstore import PTBSQLAlchemyJobStore
import datetime
import pytz

from faq import question_answers
from telegram_bot_pagination import InlineKeyboardPaginator

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

def split_array(array, k, context: CallbackContext):
    context.user_data['splitted_array']:list = []
    # self.splitted_array.clear()
    for i in range(0, len(array), k):
        context.user_data['splitted_array'].append(array[i:i+k])
        # self.splitted_array.append(array[i:i+k])
    # return self.splitted_array

def generate_page(page_number: int, context: CallbackContext):
    # pages = self.splitted_array
    pages = context.user_data['splitted_array']
    message = ""
    # keyboard = [[]]
    for i, question in enumerate(pages[page_number-1]):
        new_line = '\n'
        
        message += f"❓ <b>{question['question']}</b>\n"
        message += f"   {question['answer']}\n"
        
    return message

back_btn = InlineKeyboardButton(text = "🔙 Назад", callback_data="BACK")

# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
# Best practice would be to replace context with an underscore,
# since context is an unused local variable.
# This being an example and not having context present confusing beginners,
# we decided to have it present as context.
def start(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id
    
    links = [
        [InlineKeyboardButton(text = "Наш сайт", url = "https://unicornacademy.su")],
        [InlineKeyboardButton(text = "Наш Instagram", url = "https://www.instagram.com/unicorn.englishacademy")],
        [InlineKeyboardButton(text = "Наш Telegram канал", url = "https://t.me/unicornacademyy")],
        [InlineKeyboardButton(text = "Наш WhatsApp", url = "https://t.me/unicornacademyy")],
    ]
    
    context.bot.send_message(chat_id = update.message.chat_id, text = f"""
Доброго времени суток, {update.message.from_user.username}. Я бот команды Unicorn Academy, наиболее эффективная и результативная академия по курсам английского языка. 
                             """, reply_markup = InlineKeyboardMarkup(links))
    
    menu = [
        [InlineKeyboardButton(text = "FAQ", callback_data = "FAQ")],
        [InlineKeyboardButton(text = "Контакты", callback_data = "CONTACTS")],
    ]
    
    context.bot.send_message(chat_id = chat_id, text = f"""
Дорогой Unicornik! Ты можешь прямо сейчас оставить заявку и пройти бесплатный пробный урок. Наши специалисты свяжутся с тобой в скором времени!
""", reply_markup = InlineKeyboardMarkup(menu))
    
def menu_generate(update, context, chat_id = None):    
    query = update.callback_query
    
    menu = [
        [InlineKeyboardButton(text = "FAQ", callback_data = "FAQ")],
        [InlineKeyboardButton(text = "Контакты", callback_data = "CONTACTS")],
    ]
    
    query.edit_message_text(text = f"""
Дорогой Unicornik! Ты можешь прямо сейчас оставить заявку и пройти бесплатный пробный урок. Наши специалисты свяжутся с тобой в скором времени!
""", reply_markup = InlineKeyboardMarkup(menu))
    
    
def faq(update: Update, context: CallbackContext):
    
    query = update.callback_query
    
    questions_per_page = 5
        
    split_array(question_answers, questions_per_page, context)

    paginator = InlineKeyboardPaginator(
        # len(self.splitted_array),
        len(context.user_data['splitted_array']),
        data_pattern='character#{page}'
    )
    
    paginator.add_after(back_btn)
    
    
    context.user_data['page'] = 1

    text = generate_page(1, context)
    query.edit_message_text(
        text=text,
        reply_markup=paginator.markup(),
        parse_mode=ParseMode.HTML
    )
    
def faq_page(update: Update, context: CallbackContext):
    query = update.callback_query

    query.answer()

    page = int(query.data.split('#')[1])
    

    paginator = InlineKeyboardPaginator(
        # len(self.splitted_array),
        len(context.user_data['splitted_array']),
        current_page=page,
        data_pattern='character#{page}'
    )
    
    paginator.add_after(back_btn)
    
    
    context.user_data['page'] = page
    
    
    text = generate_page(page, context)
    
    query.edit_message_text(
        text=text,
        reply_markup=paginator.markup(),
        parse_mode=ParseMode.HTML
    )

def contact(update: Update, context: CallbackContext):
    
    query = update.callback_query
    
    query.edit_message_text(text ="""
🔵 [Записаться на пробный урок](https://unicornacademy.su/minervaquiz)

🔵 Связаться с нами: [+77071063303](tel:+77071063303)

                            """, parse_mode=ParseMode.MARKDOWN, reply_markup=InlineKeyboardMarkup([[back_btn]]))

def main() -> None:

    """Run bot."""
    # Create the Updater and pass it your bot's token.
    persistence = PicklePersistence(filename='persistence_file', store_callback_data=True)
    
    updater = Updater("6197471756:AAGzg6mHwG4vyunZNwN_hH6sel1vLIgycRM", persistence=persistence)
    
    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CallbackQueryHandler(faq, pattern='FAQ'))
    dispatcher.add_handler(CallbackQueryHandler(contact, pattern='CONTACTS'))
    dispatcher.add_handler(CallbackQueryHandler(faq_page, pattern='^character#'))
    dispatcher.add_handler(CallbackQueryHandler(menu_generate, pattern='^' + 'BACK'))
    # dispatcher.add_handler(CommandHandler("help", start))
    # dispatcher.add_handler(CommandHandler("set", set_timer))
    # dispatcher.add_handler(CommandHandler("unset", unset))

    # Start the Bot
    updater.start_polling()

    # Block until you press Ctrl-C or the process receives SIGINT, SIGTERM or
    # SIGABRT. This should be used most of the time, since start_polling() is
    # non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()