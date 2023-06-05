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

from faq import *
from telegram_bot_pagination import InlineKeyboardPaginator
import json

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

# admin_id_arr = []


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

main_menu = [
        [InlineKeyboardButton(text = "Speaking", callback_data = "SPEAKING"),
        InlineKeyboardButton(text = "Reading", callback_data = "READING")],
        [InlineKeyboardButton(text = "Writing", callback_data = "WRITING"),
        InlineKeyboardButton(text = "Listening", callback_data = "LISTENING")],
        [InlineKeyboardButton(text = "IELTS", callback_data = "IELTS"),
        InlineKeyboardButton(text = "Grammar", callback_data = "GRAMMAR")],
        [InlineKeyboardButton(text = "Vocabulary", callback_data = "VOCABULARY")],
        [InlineKeyboardButton(text = "FAQ", callback_data = "FAQ"),
        InlineKeyboardButton(text = "Контакты", callback_data = "CONTACTS")],
    ]

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
        
    context.bot.send_message(chat_id = chat_id, text = f"""
Дорогой Uni-student! Наша академия подготовила для тебя ряд полезностей для прокачки всех основных навыков в английском языке.
""", reply_markup = InlineKeyboardMarkup(main_menu))
    
    return "MAIN_MENU_SECTIONS"
    
def menu_generate(update, context, chat_id = None):    
    query = update.callback_query
    chat_id = query.message.chat_id
    
    
    query.edit_message_text(text = f"""
Дорогой Uni-student! Наша академия подготовила для тебя ряд полезностей для прокачки всех основных навыков в английском языке.
""", reply_markup = InlineKeyboardMarkup(main_menu))
    
    return "MAIN_MENU_SECTIONS"
    
 #Speaking
 
def speaking(update: Update, context: CallbackContext):
    
    query = update.callback_query
    query.answer()
    
    speaking_sections = [
        [InlineKeyboardButton(text = "Чек-листы", callback_data="CHECK_LIST")],
        [InlineKeyboardButton(text = "Советы и лайфхаки", callback_data="LIFEHACKS")],
        [InlineKeyboardButton(text = "Идиомы для повседневного разговора", callback_data="IDIOMS")],
        [InlineKeyboardButton(text = "Фильмы и сериалы для улучшения Speaking", callback_data="MOVIES")],
        [InlineKeyboardButton(text = "🔙 Назад", callback_data = "BACK_MAIN")]
    ]
    
            
    message = """
Выбери интересный тебе раздел:
"""
    
    if len(query.message.photo) != 0:
        query.delete_message()
        context.bot.send_message(chat_id = query.message.chat_id, text = message, parse_mode=ParseMode.MARKDOWN, reply_markup= InlineKeyboardMarkup(speaking_sections))
    else:
        query.edit_message_text(text =message, parse_mode=ParseMode.MARKDOWN, reply_markup=InlineKeyboardMarkup(speaking_sections))
  
    return "SPEAKING_SECTION"

def check_list(update: Update, context: CallbackContext):

    query = update.callback_query
    query.answer()
    
    query.delete_message()
    
    context.bot.send_photo(chat_id = query.message.chat_id, caption = f"""
Чек-лист чтобы избавиться от языкового барьера и улучшить говорение.        
""", photo = open("./academy/images/check_list/check_list.png", "rb"), reply_markup = InlineKeyboardMarkup([[back_btn]]))
    
    return "SPEAKING_SECTION"
    
def lifehacks(update: Update, context: CallbackContext):

    query = update.callback_query
    query.answer()
    
    message = """
🟢 <b>Практикуйтесь регулярно:</b> Регулярная практика является ключевым фактором в улучшении разговорных навыков. Постарайтесь разговаривать на английском языке каждый день, будь то 	с носителями языка или даже самим собой. Чем больше вы практикуетесь, тем более уверенно и бегло будет звучать ваша речь.

🟢 <b>Расширяйте словарный запас:</b> Учите новые слова и фразы, которые можно использовать в разговоре. Создайте список слов по тематике, которые вам интересны или которые часто встречаются в повседневной жизни. Постарайтесь использовать эти слова в разговорах, чтобы закрепить их в памяти.

🟢 <b>Слушайте и повторяйте:</b> Слушайте аудиоматериалы на английском языке, такие как аудиокниги, подкасты или речь носителей языка. После прослушивания попробуйте повторить услышанное вслед за диктором, обращая внимание на произношение, интонацию и ритм.

🟢 <b>Изучайте фразовые глаголы и выражения:</b> Фразовые глаголы и выражения являются неотъемлемой частью разговорной речи. Изучение и использование таких выражений помогут сделать вашу речь более естественной и выразительной. Составьте список наиболее распространенных слов и практикуйтесь в их использовании.

🟢 <b>Записывайте и прослушивайте свою речь:</b> Записывайте свою речь на английском языке и послушайте ее внимательно. Обратите внимание на ошибки, произношение, грамматику и попробуйте исправить их. Это поможет вам осознать свои слабые места и работать над ними.
    """
    
    query.edit_message_text(text = message, reply_markup=InlineKeyboardMarkup([[back_btn]]), parse_mode=ParseMode.HTML)
    
    return "SPEAKING_SECTION"

def idioms(update: Update, context: CallbackContext):

    query = update.callback_query
    query.answer()
    
    message = """
<b>"Break a leg"</b> - пожелание удачи, особенно перед выступлением или испытанием. Пример: "Good luck with your presentation! Break a leg!"

<b>"Piece of cake"</b> - что-то очень легкое или простое. Пример: "The exam was a piece of cake. I knew all the answers."

<b>"Hit the nail on the head"</b> - точно сказать или понять что-то. Пример: "You hit the nail on the head with that comment. It perfectly summarizes the issue."

<b>"Bite the bullet"</b> - принять неприятное решение или справиться с трудностями. Пример: "I didn't want to go to the dentist, but I had to bite the bullet and make an appointment."

<b>"Spill the beans"</b> - раскрыть секрет или секретную информацию. Пример: "Come on, spill the beans. What's the surprise party all about?"

<b>"It's raining cats and dogs"</b> - очень сильно идет дождь. Пример: "I can't go out now, it's raining cats and dogs!"

<b>"A piece of cake"</b> - что-то очень легкое или простое. Пример: "Cooking this recipe is a piece of cake. You'll have it ready in no time."

<b>"When pigs fly"</b> - что-то, что никогда не произойдет или невозможно. Пример: "I'll believe it when pigs fly. He said he'll clean his room, but I doubt it."

<b>"Once in a blue moon"</b> - что-то происходит очень редко. Пример: "I don't usually eat dessert, but I'll treat myself to a piece of cake once in a blue moon."

<b>"The ball is in your court"</b> - очередь или ответственность за принятие решения лежит на вас. Пример: "I've given you all the necessary information. Now, the ball is in your court to make a decision."

Надеемся, эти выражения и фразы помогут вам расширить вашу коллекцию выражений для повседневного разговора на английском языке. Помните, что контекст и правильное использование этих выражений имеют важное значение.
    """
    
    query.edit_message_text(text = message, reply_markup=InlineKeyboardMarkup([[back_btn]]), parse_mode=ParseMode.HTML)
    
    return "SPEAKING_SECTION"

def movies(update: Update, context: CallbackContext):

    query = update.callback_query
    query.answer()
    
    message = """
Список фильмов и сериалов, которые могут быть полезны для изучения английского языка:

Фильмы:
· "Forrest Gump"
· "The Shawshank Redemption"
· "The Social Network"
· "The Pursuit of Happyness"
· "The King's Speech"
· "The Devil Wears Prada"
· "Dead Poets Society"
· "The Intern"
· "The Fault in Our Stars"
· "La La Land"

Сериалы:
· "Friends"
· "Breaking Bad"
· "Stranger Things"
· "Game of Thrones"
· "Sherlock"
· "The Office (US)"
· "How I Met Your Mother"
· "Black Mirror"
· "The Crown"
· "Modern Family"

Эти фильмы и сериалы предлагают разнообразные жанры, от драмы и комедии до приключений и фантастики. Не забывайте делать паузы, пересматривать интересные моменты и практиковать восприятие речи, повторяя за актерами. Это поможет вам улучшить ваше произношение и ритм английского языка. Приятного просмотра и удачи в изучении английского языка!
    """
    
    query.edit_message_text(text = message, reply_markup=InlineKeyboardMarkup([[back_btn]]), parse_mode=ParseMode.HTML)
    
    return "SPEAKING_SECTION"  

#Reading
def reading(update: Update, context: CallbackContext):
    
    query = update.callback_query
    query.answer()
    
    speaking_sections = [
        [InlineKeyboardButton(text = "Учебники для прокачки Reading", callback_data="BOOKS")],
        [InlineKeyboardButton(text = "Мировая литература", callback_data="LITERATURE")],
        [InlineKeyboardButton(text = "Новости и статьи на английском", callback_data="NEWS")],
        # [InlineKeyboardButton(text = "Фильмы и сериалы для улучшения Speaking", callback_data="MOVIES")],
        [InlineKeyboardButton(text = "🔙 Назад", callback_data = "BACK_MAIN")]
    ]
    
            
    message = """
Выбери интересный тебе раздел:
"""
    
    if len(query.message.photo) != 0:
        query.delete_message()
        context.bot.send_message(chat_id = query.message.chat_id, text = message, parse_mode=ParseMode.MARKDOWN, reply_markup= InlineKeyboardMarkup(speaking_sections))
    else:
        query.edit_message_text(text =message, parse_mode=ParseMode.MARKDOWN, reply_markup=InlineKeyboardMarkup(speaking_sections))
  
    return "READING_SECTION"

def books(update: Update, context: CallbackContext):

    query = update.callback_query
    query.answer()
    
    message = """
<b>"English Grammar in Use" by Raymond Murphy</b> - это популярное пособие по грамматике, которое покрывает основные темы английской грамматики. Книга содержит понятные объяснения и множество упражнений для практики.

<b>"Word Power Made Easy" by Norman Lewis</b> - эта книга поможет вам расширить словарный запас и улучшить знание английских слов. Она предлагает интересные и эффективные методы запоминания новых слов.

<b>"The Complete Idiot's Guide to Learning English" by Laurie Rozakis</b> - эта книга предназначена для начинающих и содержит основные правила грамматики, примеры, упражнения и полезные советы по изучению английского языка.

<b>"Oxford Collocations Dictionary"</b> - этот словарь поможет вам улучшить уровень владения английским языком, предлагая наиболее типичные сочетания слов и выражений в контексте.

Выберите книгу, соответствующую вашему уровню владения языком и вашим целям изучения. Помните, что регулярное чтение и практика являются ключевыми для улучшения вашего английского языка.
    """
    
    query.edit_message_text(text = message, reply_markup=InlineKeyboardMarkup([[back_btn]]), parse_mode=ParseMode.HTML)
    
    return "READING_SECTION"

def literature(update: Update, context: CallbackContext):

    query = update.callback_query
    query.answer()
    
    message = """
Вот несколько рекомендаций по лучшим книгам мировой литературы, которые могут быть полезными для изучения английского языка:

<b>"Pride and Prejudice" by Jane Austen</b> - Этот классический роман о любви и социальных обычаях в Англии 19 века является одним из самых известных произведений английской литературы. Он предлагает богатый язык, характерные диалоги и интересные персонажи.

<b>"To Kill a Mockingbird" by Harper Lee</b> - Этот роман рассказывает о расовых проблемах и неравенстве в американском Южном обществе. Он предлагает глубокие темы и замечательный слог, который поможет вам улучшить ваше понимание английского языка.

<b>"1984" by George Orwell</b> - Это дистопическое произведение, описывающее мир полицейского государства и контроля. Он предлагает сложный словарь и интересные темы для обсуждения.

<b>"The Great Gatsby" by F. Scott Fitzgerald</b> - Этот роман о жизни в роскошном Нью-Йорке 1920-х годов предлагает захватывающую историю и яркие описания. Он поможет вам ознакомиться с американскими обычаями и использованием языка.

<b>"Brave New World" by Aldous Huxley</b> - Эта дистопическая книга представляет футуристическое общество, в котором индивидуальность и свобода подавлены. Она предлагает сложную лексику и интересные философские и социальные темы.

<b>"The Catcher in the Rye" by J.D. Salinger</b> - Этот роман о приключениях и размышлениях подростка предлагает непринужденный разговорный стиль и использование повседневного языка.

<b>"Animal Farm" by George Orwell</b> - Это аллегорическое произведение, которое исследует темы политики и власти. Оно предлагает простой и понятный язык, который будет полезным для изучения английского языка.

Эти книги представляют различные стили и темы, которые помогут вам улучшить ваш словарный запас и понимание английского языка.
    """
    
    query.edit_message_text(text = message, reply_markup=InlineKeyboardMarkup([[back_btn]]), parse_mode=ParseMode.HTML)
    
    return "READING_SECTION"

def news(update: Update, context: CallbackContext):

    query = update.callback_query
    query.answer()
    
    message = """
[BBC Learning English](https://bbc.co.uk/learningenglish) - Этот сайт предлагает широкий выбор материалов для изучения английского языка, включая новости, статьи, аудио и видео уроки. Вы также можете прочитать новости на английском языке и использовать их для практики чтения и понимания текста.

[The New York Times](https://nytimes.com) - The New York Times является одним из ведущих международных изданий, предлагающих новости и статьи на английском языке. Вы можете прочитать статьи по различным темам, включая политику, экономику, науку и культуру.

[The Guardian](https://theguardian.com) - The Guardian также является популярным источником новостей и статей на английском языке. Сайт предлагает разнообразные материалы, которые помогут вам улучшить навыки чтения и понимания текста.

[Reuters](https://reuters.com) - Reuters является международным информационным агентством, предоставляющим новости и статьи на английском языке. Их материалы охватывают широкий спектр тем, включая политику, экономику, спорт и технологии.

[National Geographic](https://nationalgeographic.com) - National Geographic предлагает интересные статьи и фотографии о природе, науке, истории и культуре. Этот сайт предоставляет возможность изучать английский язык через захватывающие и познавательные материалы.
    """
    
    query.edit_message_text(text = message, reply_markup=InlineKeyboardMarkup([[back_btn]]), parse_mode=ParseMode.MARKDOWN)
    
    return "READING_SECTION"

#Writing

def writing(update: Update, context: CallbackContext):
    
    query = update.callback_query
    query.answer()
    
    speaking_sections = [
        [InlineKeyboardButton(text = "Советы по writing", callback_data="TIPS")],
        [InlineKeyboardButton(text = "Учебники для Writing", callback_data="BOOKS")],
        # [InlineKeyboardButton(text = "Новости и статьи на английском", callback_data="NEWS")],
        # [InlineKeyboardButton(text = "Фильмы и сериалы для улучшения Speaking", callback_data="MOVIES")],
        [InlineKeyboardButton(text = "🔙 Назад", callback_data = "BACK_MAIN")]
    ]
    
            
    message = """
Выбери интересный тебе раздел:
"""
    
    if len(query.message.photo) != 0:
        query.delete_message()
        context.bot.send_message(chat_id = query.message.chat_id, text = message, parse_mode=ParseMode.MARKDOWN, reply_markup= InlineKeyboardMarkup(speaking_sections))
    else:
        query.edit_message_text(text =message, parse_mode=ParseMode.MARKDOWN, reply_markup=InlineKeyboardMarkup(speaking_sections))
  
    return "WRITING_SECTION"

def books_writing(update: Update, context: CallbackContext):

    query = update.callback_query
    query.answer()
    
    message = """
<b>"The Elements of Style" by William Strunk Jr. and E.B. White:</b> Этот классический учебник фокусируется на основах хорошего письма, включая ясность, краткость, правильную пунктуацию и стиль. Он предоставляет множество советов и примеров, которые могут быть полезны при написании на английском языке.

<b>"Writing Tools: 55 Essential Strategies for Every Writer" by Roy Peter Clark:</b> Эта книга предлагает 55 стратегий и инструментов, которые помогут вам улучшить свои навыки письма. Она включает в себя советы по структуре, стиле, использованию языка и другим аспектам письменного процесса.

<b>"On Writing Well" by William Zinsser:</b> Этот учебник сосредоточен на непринужденном и эффективном стиле письма. Он предлагает советы по улучшению языка, организации материала и созданию прочных структур в письменных работах.

<b>"The Norton Field Guide to Writing" by Richard Bullock, Maureen Daly Goggin, and Francine Weinberg:</b> Этот учебник предоставляет широкий спектр информации и ресурсов, связанных с письменным процессом. Он охватывает различные типы письменных работ и предлагает конкретные стратегии и инструменты для развития навыков письма.

<b>"Writing Academic English" by Alice Oshima and Ann Hogue:</b> Этот учебник специально разработан для студентов, которые готовятся к написанию академических текстов на английском языке. Он предлагает практические советы и упражнения для развития навыков письма в академической сфере.

Помните, что эти учебники могут быть полезными, но наибольшая польза будет от их использования в сочетании с активной практикой и обратной связью от носителей языка или опытных преподавателей.
    """
    
    query.edit_message_text(text = message, reply_markup=InlineKeyboardMarkup([[back_btn]]), parse_mode=ParseMode.HTML)
    
    return "WRITING_SECTION"

def tips_writing(update: Update, context: CallbackContext):

    query = update.callback_query
    query.answer()
    
    message = """
<b>Пишите регулярно:</b> Старайтесь писать на английском языке как можно чаще. Это могут быть записи в дневник, эссе, письма или даже комментарии в блогах и форумах.

<b>Изучайте грамматику и пунктуацию:</b> Правильное использование грамматики и пунктуации важно для ясного и грамотного письма. Уделите внимание основным правилам и идиоматическим выражениям, чтобы избежать ошибок.

<b>Запросите обратную связь:</b> Попросите носителя языка или опытного преподавателя английского языка прокомментировать ваши написанные тексты. Обратная связь поможет вам определить свои слабые стороны и сосредоточиться на их улучшении.

<b>Перечитывайте и редактируйте свои тексты:</b> После написания текста отложите его на некоторое время и затем перечитайте его снова. Обратите внимание на грамматические ошибки, неоднозначность выражений и структуру предложений. Вносите необходимые исправления.

<b>Изучайте примеры хорошо написанных текстов:</b> Изучение примеров хорошо написанных эссе, статей или писем поможет вам развить свой стиль письма и сравнить вашу работу с другими.
    """
    
    query.edit_message_text(text = message, reply_markup=InlineKeyboardMarkup([[back_btn]]), parse_mode=ParseMode.HTML)
    
    return "WRITING_SECTION"
    
#Listening
def listening(update: Update, context: CallbackContext):
    
    query = update.callback_query
    query.answer()
    
    speaking_sections = [
        [InlineKeyboardButton(text = "Советы по listening", callback_data="TIPS")],
        [InlineKeyboardButton(text = "Аудиокниги", callback_data="AUDIOBOOKS")],
        [InlineKeyboardButton(text = "Лучшие подкасты для Listening", callback_data="PODCASTS")],
        # [InlineKeyboardButton(text = "Фильмы и сериалы для улучшения Speaking", callback_data="MOVIES")],
        [InlineKeyboardButton(text = "🔙 Назад", callback_data = "BACK_MAIN")]
    ]
    
            
    message = """
Выбери интересный тебе раздел:
"""
    
    if len(query.message.photo) != 0:
        query.delete_message()
        context.bot.send_message(chat_id = query.message.chat_id, text = message, parse_mode=ParseMode.MARKDOWN, reply_markup= InlineKeyboardMarkup(speaking_sections))
    else:
        query.edit_message_text(text =message, parse_mode=ParseMode.MARKDOWN, reply_markup=InlineKeyboardMarkup(speaking_sections))
  
    return "LISTENING_SECTION"

def tips_listening(update: Update, context: CallbackContext):

    query = update.callback_query
    query.answer()
    
    message = """
Улучшение навыков слушания в английском языке требует регулярной практики и использования разнообразных ресурсов. Вот несколько советов, которые помогут вам улучшить слушание на английском:

<b>Слушайте разнообразные материалы:</b> Слушайте различные типы аудио, такие как аудиокниги, подкасты, новости, речи и музыку. Это поможет вам привыкнуть к различным акцентам, скорости речи и стилям высказываний. Чем чаще вы слушаете, тем лучше вы разовьете свой слух и понимание английской речи.

<b>Используйте аудиоматериалы с текстами:</b> Ищите аудиоматериалы, которые сопровождаются текстами, такими как аудиокниги с электронными книгами или подкасты с транскриптами. 

<b>Слушайте на разных уровнях сложности:</b> Начните со слушания материалов на вашем текущем уровне владения языком, затем постепенно переходите к более сложным материалам. Используйте ресурсы, специально созданные для изучающих язык, которые предлагают материалы на разных уровнях сложности.

<b>Используйте приложения и онлайн-ресурсы:</b> Существуют много приложений и онлайн-ресурсов, которые предлагают аудиоматериалы для изучения английского языка. Некоторые из них включают Duolingo, FluentU, ESLPod, и BBC Learning English.

Помните, что улучшение навыков слушания требует времени и терпения. Постепенно расширяйте свой словарный запас и работайте над пониманием различных стилей речи. 
    """
    
    query.edit_message_text(text = message, reply_markup=InlineKeyboardMarkup([[back_btn]]), parse_mode=ParseMode.HTML)
    
    return "LISTENING_SECTION"

def audiobooks(update: Update, context: CallbackContext):

    query = update.callback_query
    query.answer()
    
    message = """
Вот несколько рекомендаций по лучшим аудиокнигам для изучения английского языка:

<b>"Harry Potter" series by J.K. Rowling</b> - Серия книг о Гарри Поттере предлагает увлекательную историю, а аудиокниги, читаемые профессиональными актерами, помогут вам улучшить навыки английского языка.

<b>"The Great Gatsby" by F. Scott Fitzgerald</b> - Этот классический роман о жизни в роскошном Нью-Йорке 1920-х годов является популярным выбором для изучения английского языка. Вы можете прослушать аудиокнигу и следить за текстом одновременно, чтобы лучше понять и запомнить новые слова и выражения.

<b>"1984" by George Orwell</b> - Этот дистопический роман о контроле и тоталитаризме предлагает захватывающий сюжет и интересные темы для обсуждения. Слушая аудиокнигу, вы сможете погрузиться в атмосферу книги и расширить свой словарный запас.

<b>"The Catcher in the Rye" by J.D. Salinger</b> - Эта книга, рассказанная от первого лица, описывает приключения и размышления подростка. Аудиокнига поможет вам понять разговорный стиль речи и использование повседневного языка.

<b>"To Kill a Mockingbird" by Harper Lee</b> - Этот классический роман об американском Южном обществе и расовых проблемах может быть интересным выбором для изучения английского языка. Аудиокнига поможет вам услышать автентичное произношение и интонации.

<b>"Pride and Prejudice" by Jane Austen</b> - Этот роман о любви и социальных обычаях является одним из самых известных произведений английской литературы. Слушая аудиокнигу, вы сможете насладиться языком и стилем автора.

<b>"The Hobbit" by J.R.R. Tolkien</b> - Эта фэнтезийная книга о приключениях хоббита Бильбо Бэггинса предлагает интересный сюжет и богатый язык. 
"""
    
    query.edit_message_text(text = message, reply_markup=InlineKeyboardMarkup([[back_btn]]), parse_mode=ParseMode.HTML)
    
    return "LISTENING_SECTION"

def podcasts(update: Update, context: CallbackContext):

    query = update.callback_query
    query.answer()
    
    message = """
<b>6 Minute English BBC</b> 
Каждый эпизод ориентирован на повседневную лексику и содержит диалог между двумя людьми. В дополнение к аудио, вы также можете найти транскрипции диалогов, словарь и вопрос недели. У вас недостаточно времени? С 6-минутными уроками от 6-Minute English у вас больше не найдется отговорок. 

<b>Easy Stories in English</b> 
В среднем аудиофайлы длятся около получаса. Истории имеют разные уровни сложности. В основном диктор читает сказки, которые направлены на изучения лексики по какой-либо теме (флора, фауна, профессии и т. д.). 

<b>Luke’s English Podcast </b>
Если вы владеете английским на уровне Intermediate, то с легкостью сможете слушать этот развлекательный подкаст. Особенностью подкаста является гости. В основном, помогают Люку его же родственники и друзья. Они долго дискутируют в формате дружеской беседы на совершенно разные темы. Иногда ведущий импровизирует. 

<b>Espresso English Podcast</b> 
Подкаст направлен на практику разговорной и письменной речи. Диктор Шаяна Оливьера — излагает материал в формате coffee-talk. Вы легко и ненавязчиво изучите различные идиомы, фразовые глаголы, интересные выражения, сленг.
"""
    
    query.edit_message_text(text = message, reply_markup=InlineKeyboardMarkup([[back_btn]]), parse_mode=ParseMode.HTML)
    
    return "LISTENING_SECTION"

#IELTS
def ielts(update: Update, context: CallbackContext):
    
    query = update.callback_query
    query.answer()
    
    speaking_sections = [
        [InlineKeyboardButton(text = "Полезные советы по сдаче IELTS", url = "https://drive.google.com/drive/u/0/folders/1l2Yg4ZeJhk1vd2p_gFP4IzVZnBUmXFVY")],
        [InlineKeyboardButton(text = "IELTS practice tests/пробные тесты", callback_data="MOCK_TESTS")],
        [InlineKeyboardButton(text = "Подкасты", callback_data="PODCASTS")],
        [InlineKeyboardButton(text = "Книги", callback_data="BOOKS")],
        [InlineKeyboardButton(text = "Ютуб каналы", callback_data="YOUTUBE")],
        # [InlineKeyboardButton(text = "Фильмы и сериалы для улучшения Speaking", callback_data="MOVIES")],
        [InlineKeyboardButton(text = "🔙 Назад", callback_data = "BACK_MAIN")]
    ]
    
            
    message = """
Выбери интересный тебе раздел:
"""
    
    if len(query.message.photo) != 0:
        query.delete_message()
        context.bot.send_message(chat_id = query.message.chat_id, text = message, parse_mode=ParseMode.MARKDOWN, reply_markup= InlineKeyboardMarkup(speaking_sections))
    else:
        query.edit_message_text(text =message, parse_mode=ParseMode.MARKDOWN, reply_markup=InlineKeyboardMarkup(speaking_sections))
  
    return "IELTS_SECTION"

def practice_tests(update: Update, context: CallbackContext):

    query = update.callback_query
    query.answer()
    
    message = """
Пробные тесты по IELTS:
    """
    
    keyboard = [
        [InlineKeyboardButton(text = "MOCK 1", url = "https://docs.google.com/document/d/1i49-TmGyjXcE9zg1lS8toQRylBv44fk7Pd635k-c4h4/edit?usp=drive_link")],
        [InlineKeyboardButton(text = "MOCK 2", url = "https://docs.google.com/document/d/1gtwEzwJiZccQr8SrGuPmsLGewVfzfFIaaIbtGrwl4to/edit?usp=drive_link")],
        [back_btn]
    ]
    query.edit_message_text(text = message, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode=ParseMode.HTML)
    
    return "IELTS_SECTION"

def books_ielts(update: Update, context: CallbackContext):

    query = update.callback_query
    query.answer()
    
    message = """
<b>"The Official Cambridge Guide to IELTS" by Cambridge English Language Assessment</b>
Это официальное руководство, разработанное самими создателями экзамена IELTS. Оно содержит подробные объяснения формата экзамена, стратегии выполнения заданий, а также примеры заданий и модели ответов.

<b>"IELTS Practice Tests Plus" by Morgan Terry and Judith Wilson</b>
Эта книга предлагает серию практических тестов, которые помогут вам оценить свой уровень подготовки и привыкнуть к формату и стилю заданий IELTS. Книга также содержит подробные разъяснения ответов и советы по стратегии выполнения заданий.
 
<b>"IELTS Trainer: Six Practice Tests with Answers" by Louise Hashemi and Barbara Thomas</b>
Эта книга предлагает шесть полноценных практических тестов с подробными разъяснениями ответов и стратегиями. Она поможет вам развить навыки, необходимые для успешного выполнения заданий в каждом из разделов экзамена IELTS.

<b>"Barron's IELTS Superpack" by Lin Lougheed</b>
Этот суперпакет включает в себя книгу с подробными объяснениями, практическими тестами и модельными ответами, а также два аудио-CD с записями для разделов Listening и Speaking. Он предлагает полное покрытие всех разделов экзамена IELTS и поможет вам подготовиться к каждому из них.

<b>"Target Band 7: IELTS Academic Module - How to Maximize Your Score" by Simone Braverman</b>
Эта книга сфокусирована на разделе Writing и Reading экзамена IELTS. Она предлагает стратегии, советы и примеры заданий, которые помогут вам повысить свой балл и достичь желаемого результата.

Эти книги предлагают разнообразные материалы для подготовки к экзамену IELTS, включая практические тесты, модели ответов, советы по стратегии и подробные объяснения. Рекомендуется использовать их в сочетании с другими ресурсами, такими как онлайн-курсы и практические задания, для достижения наилучших результатов.
"""
    
    query.edit_message_text(text = message, reply_markup=InlineKeyboardMarkup([[back_btn]]), parse_mode=ParseMode.HTML)
    
    return "IELTS_SECTION"

def podcasts_ielts(update: Update, context: CallbackContext):

    query = update.callback_query
    query.answer()
    
    message = """
<b>"IELTS Podcast" by Ben Worthington:</b> Этот подкаст предлагает уроки и советы по каждому из разделов IELTS. В подкасте вы найдете разнообразные аудиоматериалы и практические задания, которые помогут вам улучшить ваши навыки.

<b>"IELTS Energy English Podcast" by All Ears English:</b> В этом подкасте ведущие обсуждают стратегии и техники, которые помогут вам успешно справиться с экзаменом.

<b>"BBC Learning English - 6 Minute English":</b> Этот подкаст от BBC предлагает шестьминутные эпизоды на различные темы, которые помогут вам улучшить ваше понимание на слух и расширить словарный запас.

<b>"TED Talks":</b> TED Talks предлагает широкий выбор выступлений на различные темы. Вы можете выбрать темы, которые вас интересуют, и слушать выступления, чтобы улучшить свои навыки восприятия на слух и развить лексику и понимание различных тематик.
"""
    
    query.edit_message_text(text = message, reply_markup=InlineKeyboardMarkup([[back_btn]]), parse_mode=ParseMode.HTML)
    
    return "IELTS_SECTION"

def youtube_ielts(update: Update, context: CallbackContext):

    query = update.callback_query
    query.answer()
    
    message = """
["IELTS Liz"](https://www.youtube.com/user/ieltsliz)
Канал, ведомый Лизой, предлагает множество видеоуроков, советов и стратегий по каждому из разделов IELTS. Она объясняет основные понятия, дает примеры заданий и модельные ответы, а также предлагает полезные советы по подготовке и стратегиям выполнения заданий.

["IELTS Ryan"](https://www.youtube.com/user/IELTSryan)
Райан, опытный преподаватель IELTS, предлагает на своем канале множество видеоуроков и советов по подготовке к экзамену. Он демонстрирует стратегии, объясняет особенности каждого раздела и предоставляет полезные ресурсы для улучшения ваших навыков.

["IELTS Advantage"](https://www.youtube.com/c/IELTSadvantage)
Канал IELTS Advantage предлагает широкий выбор видеоуроков, советов и стратегий для всех разделов экзамена IELTS. Здесь вы найдете полезные советы по аудированию, чтению, письму и разговорной речи, а также модельные ответы и обратную связь от опытных преподавателей.

["IELTS Official"](https://www.youtube.com/c/IELTSOfficial)
Официальный YouTube-канал IELTS предоставляет официальные видеоуроки и советы от экспертов по подготовке к экзамену. Здесь вы найдете полезные материалы, примеры заданий, объяснения оценок и многое другое, что поможет вам лучше понять формат и требования IELTS.

["IELTS Speaking"](https://www.youtube.com/c/IELTSSpeaking)
Этот канал специализируется на разделе Speaking в экзамене IELTS. Он предлагает видеоуроки, примеры заданий, модельные ответы и советы по подготовке к разговорной части экзамена.

У этих каналов есть множество полезных видеоматериалов, которые помогут вам развить навыки, понять требования экзамена и получить ценные советы для успешной подготовки к IELTS.
"""
    
    query.edit_message_text(text = message, reply_markup=InlineKeyboardMarkup([[back_btn]]), parse_mode=ParseMode.MARKDOWN)
    
    return "IELTS_SECTION"

#Grammar

def grammar(update: Update, context: CallbackContext):
    
    query = update.callback_query
    query.answer()
    
    speaking_sections = [
        [InlineKeyboardButton(text = "Основные темы", callback_data="MAIN_TOPICS")],
        [InlineKeyboardButton(text = "Советы по грамматике", callback_data="TIPS")],
        [InlineKeyboardButton(text = "Лучшие учебники", callback_data="BOOKS")],
        # [InlineKeyboardButton(text = "Фильмы и сериалы для улучшения Speaking", callback_data="MOVIES")],
        [InlineKeyboardButton(text = "🔙 Назад", callback_data = "BACK_MAIN")]
    ]
    
            
    message = """
Выбери интересный тебе раздел:
"""
    
    if len(query.message.photo) != 0:
        query.delete_message()
        context.bot.send_message(chat_id = query.message.chat_id, text = message, parse_mode=ParseMode.MARKDOWN, reply_markup= InlineKeyboardMarkup(speaking_sections))
    else:
        query.edit_message_text(text =message, parse_mode=ParseMode.MARKDOWN, reply_markup=InlineKeyboardMarkup(speaking_sections))
  
    return "GRAMMAR_SECTION"

def tips_grammar(update: Update, context: CallbackContext):

    query = update.callback_query
    query.answer()
    
    message = """
Изучение английской грамматики может быть вызовом, но с правильным подходом и некоторыми полезными советами вы сможете сделать этот процесс более эффективным. Вот несколько советов, которые помогут вам изучать английскую грамматику:

<b>Разбейте грамматику на части:</b> Английская грамматика включает различные аспекты, такие как времена, модальные глаголы, пассивный залог и многое другое. Разделите грамматику на более мелкие части и изучайте их поочередно, чтобы не перегружать себя информацией.

<b>Используйте учебники и онлайн ресурсы:</b> Имейте под рукой учебники, грамматические справочники и онлайн ресурсы, которые объясняют правила и приводят примеры использования. Они помогут вам понять концепции и применить их на практике.

<b>Практикуйте с помощью упражнений:</b> Решайте упражнения, которые проверяют ваше понимание и применение грамматических правил. Это могут быть задания в учебнике, онлайн тесты или приложения для изучения языка. Практика поможет закрепить материал и отработать навыки.

<b>Читайте и слушайте на английском:</b> Чтение и прослушивание материалов на английском языке, таких как книги, статьи, аудиокниги, подкасты или видео, помогут вам увидеть грамматические конструкции в контексте и улучшить понимание.

<b>Общайтесь на английском:</b> Активно общайтесь на английском языке с носителями языка или другими изучающими язык. Регулярные разговоры помогут вам применять грамматические правила в реальном времени и совершенствовать их использование.

<b>Обратите внимание на ошибки:</b> Заметьте типичные ошибки, которые вы делаете при использовании грамматических конструкций, и работайте над их исправлением.
    """
    
    query.edit_message_text(text = message, reply_markup=InlineKeyboardMarkup([[back_btn]]), parse_mode=ParseMode.HTML)
    
    return "GRAMMAR_SECTION"

def main_topics(update: Update, context: CallbackContext):

    query = update.callback_query
    query.answer()
    
    message = """
В грамматике английского языка есть несколько важных тем, которые необходимо изучить для хорошего владения языком. Вот некоторые из них:

<b>Глагольные времена (Verb Tenses):</b> Времена глаголов, такие как Present Simple, Present Continuous, Past Simple, Past Continuous, Future Simple, являются основой для образования предложений и выражения временных отношений. Изучение глагольных времен поможет вам грамотно описывать события в прошлом, настоящем и будущем.

<b>Условные предложения (Conditional Sentences):</b> Условные предложения используются для выражения возможных условий и их следствий. Они помогают описывать события, которые могли бы произойти, если бы были выполнены определенные условия. 

<b>Сравнительные и превосходные степени (Comparatives and Superlatives):</b> Изучение сравнительных и превосходных степеней позволит вам описывать различия между объектами или людьми и сравнивать их характеристики.

<b>Модальные глаголы (Modal Verbs):</b> Модальные глаголы, такие как can, could, may, might, must, should, будут использоваться для выражения возможности, разрешения, совета, необходимости и других модально-значимых оттенков. Изучение модальных глаголов поможет вам уметь выражать свои намерения, возможности, обязанности и предпочтения.

<b>Пассивный залог (Passive Voice):</b> Пассивный залог используется для перевода активных предложений, в которых субъект выполняет действие, в предложения, в которых субъект подвергается действию. Изучение пассивного залога позволит вам лучше понимать и использовать его в разных контекстах.

<b>Относительные местоимения (Relative Pronouns):</b> Относительные местоимения, такие как who, whom, whose, which, that, используются для связывания придаточных предложений с главным предложением. Изучение относительных местоимений поможет вам строить сложные предложения и более точно выражать отношения между различными элементами предложения.

<b>Предлоги (Prepositions):</b> Предлоги используются для выражения места, направления, времени и других отношений. Изучение предлогов поможет вам правильно использовать их в предложениях и связывать слова и фразы с соответствующими контекстами.

Это лишь некоторые из важных тем в грамматике английского языка. Каждая тема имеет свои особенности и подтемы, и изучение их постепенно и систематически поможет вам лучше овладеть грамматикой и улучшить свои навыки в английском языке.
"""
    
    query.edit_message_text(text = message, reply_markup=InlineKeyboardMarkup([[back_btn]]), parse_mode=ParseMode.HTML)
    
    return "GRAMMAR_SECTION"

def books_grammar(update: Update, context: CallbackContext):

    query = update.callback_query
    query.answer()
    
    message = """
<b>"English Grammar in Use" by Raymond Murphy:</b> Этот учебник является одним из самых популярных и широко используемых пособий по грамматике английского языка. Он доступно объясняет основные грамматические темы и предлагает множество практических упражнений.

<b>"Understanding and Using English Grammar" by Betty Schrampfer Azar:</b> Этот учебник является всеобъемлющим ресурсом, который покрывает различные аспекты грамматики английского языка. Он предлагает ясные объяснения и многочисленные упражнения для отработки навыков.

<b>"Practical English Usage" by Michael Swan:</b> Эта книга представляет собой исчерпывающий справочник по грамматике английского языка. Она содержит объяснения грамматических правил, а также примеры и комментарии по их использованию.

<b>"Grammar in Use" by William R. Smalzer:</b> Этот учебник предназначен для студентов на разных уровнях владения английским языком. Он предлагает простые объяснения и понятные примеры, чтобы помочь студентам освоить основы грамматики.

<b>"The Grammar Book" by Diane Larsen-Freeman:</b> Эта книга является исчерпывающим исследованием грамматических явлений в английском языке. Она предлагает глубокие объяснения и анализирует сложные аспекты грамматики.

Помните, что выбор учебника зависит от ваших индивидуальных потребностей и предпочтений. Рекомендуется использовать учебник в сочетании с другими ресурсами, такими как онлайн материалы, упражнения и практика в реальных ситуациях общения.
"""
    
    query.edit_message_text(text = message, reply_markup=InlineKeyboardMarkup([[back_btn]]), parse_mode=ParseMode.HTML)
    
    return "GRAMMAR_SECTION"

#Vocabulary
def vocabulary(update: Update, context: CallbackContext):
    
    query = update.callback_query
    query.answer()
    
    speaking_sections = [
        [InlineKeyboardButton(text = "Советы по увеличению словарного запаса", callback_data="TIPS")],
        [InlineKeyboardButton(text = "Приложения", callback_data="APPS")],
        # [InlineKeyboardButton(text = "Фильмы и сериалы для улучшения Speaking", callback_data="MOVIES")],
        [InlineKeyboardButton(text = "🔙 Назад", callback_data = "BACK_MAIN")]
    ]
    
            
    message = """
Выбери интересный тебе раздел:
"""
    
    if len(query.message.photo) != 0:
        query.delete_message()
        context.bot.send_message(chat_id = query.message.chat_id, text = message, parse_mode=ParseMode.MARKDOWN, reply_markup= InlineKeyboardMarkup(speaking_sections))
    else:
        query.edit_message_text(text =message, parse_mode=ParseMode.MARKDOWN, reply_markup=InlineKeyboardMarkup(speaking_sections))
  
    return "VOCABULARY_SECTION"

def tips_vocabulary(update: Update, context: CallbackContext):

    query = update.callback_query
    query.answer()
    
    message = """
<b>Читайте широкий спектр материалов:</b> Читайте книги, статьи, блоги, газеты и другие тексты на английском языке. Разнообразность материалов поможет вам пополнить словарный запас различными темами и контекстами.

<b>Используйте словарь:</b> Во время чтения или изучения новых слов используйте словарь, чтобы узнать и запомнить их значения. Записывайте новые слова, их определения и примеры использования для последующего повторения.

<b>Создайте карточки:</b> Запишите новые слова на карточки — одна сторона слово, другая сторона определение. Просмотрите их регулярно, повторяя и запоминая новые слова.

<b>Используйте слова в контексте:</b> Применяйте новые слова в речи и письме, чтобы закрепить их в памяти. Постарайтесь использовать их в различных контекстах и предложениях, чтобы лучше понять и запомнить их значения.

<b>Смотрите фильмы и сериалы на английском:</b> Просмотр фильмов и сериалов на английском языке поможет вам расширить словарный запас, выучить новые выражения и фразы, а также познакомиться с аутентичным языком и произношением.

<b>Слушайте аудио-и подкасты:</b> Слушайте аудиокниги, подкасты и радиопередачи на английском языке. Это поможет вам улучшить навыки восприятия на слух и расширить словарный запас.

<b>Используйте мобильные приложения и онлайн-ресурсы:</b> Существует множество мобильных приложений и онлайн-ресурсов, предлагающих интерактивные задания, игры и упражнения для изучения новых слов и их использования в контексте.

<b>Постоянно практикуйтесь:</b> Постоянное повторение и применение новых слов помогут вам закрепить их в памяти. Регулярно повторяйте изученные слова, используйте их в своей речи и письме, чтобы они стали 
    """
    
    query.edit_message_text(text = message, reply_markup=InlineKeyboardMarkup([[back_btn]]), parse_mode=ParseMode.HTML)
    
    return "VOCABULARY_SECTION"

def apps_vocabulary(update: Update, context: CallbackContext):

    query = update.callback_query
    query.answer()
    
    message = """
Вот несколько приложений, которые помогут вам улучшить словарный запас и расширить вашу лексику в английском языке:

<b>Duolingo (iOS, Android)</b> - Duolingo предлагает интерактивные уроки по изучению языков, включая английский. В разделе "Words" вы можете практиковать новые слова с помощью упражнений и игр.

<b>Memrise (iOS, Android)</b> - Memrise предлагает обширную библиотеку курсов по различным языкам. Вы можете выбрать курс по расширению словарного запаса и повторять слова с помощью карт и упражнений.

<b>Quizlet (iOS, Android)</b> - Quizlet позволяет создавать собственные наборы карточек с новыми словами и определениями. Вы можете повторять слова с помощью интерактивных игр и тестов.

<b>Magoosh Vocabulary Builder (iOS, Android)</b> - Это приложение предлагает дневные слова и определения для изучения. Вы можете просматривать слова, повторять их с помощью упражнений и отслеживать свой прогресс.

<b>WordUp! Vocabulary (iOS, Android)</b> - WordUp! Vocabulary предлагает игровой подход к изучению новых слов. Вы можете проходить уровни, угадывать значения слов и повторять их с помощью интерактивных заданий.

<b>Anki (iOS, Android)</b> - Anki является мощным инструментом для создания собственных наборов карточек с новыми словами. Вы можете повторять слова с помощью системы повторения на основе интервалов.

<b>Merriam-Webster Dictionary (iOS, Android)</b> - Это официальное приложение словаря Merriam-Webster, которое предлагает определения, примеры использования и произношение слов. Вы можете исследовать новые слова и добавлять их в свой словарный запас.
 
Эти приложения предлагают различные методы и упражнения для изучения и повторения новых слов. Выберите приложение, которое наиболее подходит вам по стилю обучения и начните регулярную практику для улучшения вашего словарного запаса.
"""
    
    query.edit_message_text(text = message, reply_markup=InlineKeyboardMarkup([[back_btn]]), parse_mode=ParseMode.HTML)
    
    return "VOCABULARY_SECTION"

def faq_ver2(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    chat_id = query.message.chat_id
    
    question_answers = get_faq()
    
    questions_keyboard = [
        [InlineKeyboardButton(text = "🔙 Назад", callback_data="BACK_MAIN")]
    ]
    for i, question in enumerate(question_answers):
        questions_keyboard.insert(i, [InlineKeyboardButton(text = question['question'], callback_data=f"QUESTION | {i}")])

    if str(chat_id) in get_admin_arr():
        questions_keyboard.insert(len(questions_keyboard)-1, [InlineKeyboardButton(text = "➕ Добавить вопрос", callback_data="ADD_QUESTION")])

    query.edit_message_text(text = "Часто задаваемые вопросы:", reply_markup=InlineKeyboardMarkup(questions_keyboard))

    return "FAQ_SECTION"

def faq_ver2_display_question(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    
    chat_id = query.message.chat_id
    
    question_answers = get_faq()
    
    question_number = int(query.data.split(" | ")[1])
    
    message = f"""
❓ <b>{question_answers[question_number]['question']}</b>

{question_answers[question_number]['answer']}
    """
    
    keyboard = [
        [back_btn]
    ]
    
    if str(chat_id) in get_admin_arr():
        keyboard.insert(0, [InlineKeyboardButton(text = "❌ Удалить вопрос", callback_data=f"DELETE_QUESTION | {question_number}")])

    
    query.edit_message_text(text = message, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode=ParseMode.HTML)

    return "FAQ_SECTION"

def faq_ver2_delete_question(update: Update, context: CallbackContext):
    index = update.callback_query.data.split(" | ")[1]
    
    delete_question(index)
    
    return faq_ver2(update, context)
    
    # return "ADD_FAQ_QUESTION"

def faq_ver2_add_question(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    
    query.edit_message_text(text = f"Введите вопрос", parse_mode=ParseMode.HTML)

    return "ADD_FAQ_QUESTION"

def faq_ver2_get_question(update: Update, context: CallbackContext):
    question = update.message.text_html_urled
    
    context.user_data['faq_question'] = question
    
    context.bot.send_message(chat_id = update.message.chat_id, text = "Введите ответ")

    return "ADD_FAQ_ANSWER"

def faq_ver2_get_answer(update: Update, context: CallbackContext):
    answer = update.message.text_html_urled
    
    context.user_data['faq_answer'] = answer
    
    add_question(context.user_data['faq_question'], context.user_data['faq_answer'])

    return start(update, context)
    

def faq(update: Update, context: CallbackContext):
    
    query = update.callback_query
    
    questions_per_page = 5
    
    question_answers = get_faq()
        
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
    
    return "FAQ_SECTION"
    
    
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
    
    return "FAQ_SECTION"

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
    # dispatcher.add_handler(CommandHandler("start", start))
    # dispatcher.add_handler()
    # dispatcher.add_handler()
    # dispatcher.add_handler()
    # dispatcher.add_handler(CallbackQueryHandler(menu_generate, pattern='^' + 'BACK'))
    
    main_conversation = ConversationHandler(
        entry_points= [CommandHandler("start", start)],
        states={
            "MAIN_MENU_SECTIONS": [
                # CallbackQueryHandler(faq, pattern='FAQ'),
                CallbackQueryHandler(faq_ver2, pattern='FAQ'),
                CallbackQueryHandler(contact, pattern='CONTACTS'),
                CallbackQueryHandler(speaking, pattern='SPEAKING'),
                CallbackQueryHandler(reading, pattern='READING'),
                CallbackQueryHandler(writing, pattern='WRITING'),
                CallbackQueryHandler(listening, pattern='LISTENING'),
                CallbackQueryHandler(ielts, pattern='IELTS'),
                CallbackQueryHandler(grammar, pattern='GRAMMAR'),
                CallbackQueryHandler(vocabulary, pattern='VOCABULARY'),
                CallbackQueryHandler(menu_generate, pattern='^' + 'BACK')
            ],
            "FAQ_SECTION": [
                # CallbackQueryHandler(faq_page, pattern='^character#'),
                # CallbackQueryHandler(menu_generate, pattern='^' + 'BACK')
                
                CallbackQueryHandler(faq_ver2_display_question, pattern='^' + 'QUESTION'),
                CallbackQueryHandler(faq_ver2_add_question, pattern='^' + 'ADD_QUESTION'),
                CallbackQueryHandler(faq_ver2_delete_question, pattern='^' + 'DELETE_QUESTION'),
                CallbackQueryHandler(menu_generate, pattern='^' + 'BACK_MAIN'),
                CallbackQueryHandler(faq_ver2, pattern='^' + 'BACK')
                
                
            ],
            "ADD_FAQ_QUESTION": [
                MessageHandler(Filters.text, faq_ver2_get_question)
            ],
            "ADD_FAQ_ANSWER": [
                MessageHandler(Filters.text, faq_ver2_get_answer)
            ],
            "SPEAKING_SECTION": [
                CallbackQueryHandler(check_list, pattern='^' + 'CHECK_LIST'),
                CallbackQueryHandler(lifehacks, pattern='^' + 'LIFEHACKS'),
                CallbackQueryHandler(idioms, pattern='^' + 'IDIOMS'),
                CallbackQueryHandler(movies, pattern='^' + 'MOVIES'),
                CallbackQueryHandler(menu_generate, pattern='^' + 'BACK_MAIN$'),
                CallbackQueryHandler(speaking, pattern='^' + 'BACK$'),
            ],
            "READING_SECTION": [
                
                CallbackQueryHandler(books, pattern='^' + 'BOOKS'),
                CallbackQueryHandler(literature, pattern='^' + 'LITERATURE'),
                CallbackQueryHandler(news, pattern='^' + 'NEWS'),
                CallbackQueryHandler(menu_generate, pattern='^' + 'BACK_MAIN$'),
                CallbackQueryHandler(reading, pattern='^' + 'BACK$'),
                
            ],
            "WRITING_SECTION": [
                
                CallbackQueryHandler(books_writing, pattern='^' + 'BOOKS'),
                CallbackQueryHandler(tips_writing, pattern='^' + 'TIPS'),
                CallbackQueryHandler(menu_generate, pattern='^' + 'BACK_MAIN$'),
                CallbackQueryHandler(writing, pattern='^' + 'BACK$'),
                
            ],
            "LISTENING_SECTION": [
                
                CallbackQueryHandler(audiobooks, pattern='^' + 'AUDIOBOOKS'),
                CallbackQueryHandler(tips_listening, pattern='^' + 'TIPS'),
                CallbackQueryHandler(podcasts, pattern='^' + 'PODCASTS'),
                CallbackQueryHandler(menu_generate, pattern='^' + 'BACK_MAIN$'),
                CallbackQueryHandler(listening, pattern='^' + 'BACK$'),
                
            ],
            "IELTS_SECTION": [
                
                CallbackQueryHandler(practice_tests, pattern='^' + 'MOCK_TESTS'),
                CallbackQueryHandler(podcasts_ielts, pattern='^' + 'PODCASTS'),
                CallbackQueryHandler(books_ielts, pattern='^' + 'BOOKS'),
                CallbackQueryHandler(youtube_ielts, pattern='^' + 'YOUTUBE'),
                CallbackQueryHandler(menu_generate, pattern='^' + 'BACK_MAIN$'),
                CallbackQueryHandler(ielts, pattern='^' + 'BACK$'),
                
            ],
            "GRAMMAR_SECTION": [
                
                CallbackQueryHandler(main_topics, pattern='^' + 'MAIN_TOPICS'),
                CallbackQueryHandler(tips_grammar, pattern='^' + 'TIPS'),
                CallbackQueryHandler(books_grammar, pattern='^' + 'BOOKS'),
                CallbackQueryHandler(menu_generate, pattern='^' + 'BACK_MAIN$'),
                CallbackQueryHandler(grammar, pattern='^' + 'BACK$'),
                
            ],
            "VOCABULARY_SECTION": [
                
                CallbackQueryHandler(tips_vocabulary, pattern='^' + 'TIPS'),
                CallbackQueryHandler(apps_vocabulary, pattern='^' + 'APPS'),
                CallbackQueryHandler(menu_generate, pattern='^' + 'BACK_MAIN$'),
                CallbackQueryHandler(vocabulary, pattern='^' + 'BACK$'),
                
            ]
            
            
            
        },
        fallbacks=[
            CommandHandler("start", start)
            # CallbackQueryHandler(guest_payment_cash_payment, pattern='^' + "BACK_ADMIN_HELP"),
                
        ],
        allow_reentry = True,
        persistent=True,
        name = "main_conversation"
    )
    
    dispatcher.add_handler(main_conversation)

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