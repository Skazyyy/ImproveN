import telebot
from telebot import types
import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from config import API_TOKEN

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)

spreadsheet_id = "1JBjn6w1df2gBc2jhpDF2ppSTAug822hSNRls2fC0DpE"
spreadsheet = client.open_by_key(spreadsheet_id)

bot = telebot.TeleBot(API_TOKEN)

user_data = {}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    segments = ["Русский язык", "Математика", "Информатика", "Физика", "История", "Обществознание", "Английский язык",
                "Биология", "Химия", "Digital Skills"]
    for segment in segments:
        markup.add(segment)
    msg = bot.reply_to(message, "Привет! Выберите сегмент:", reply_markup=markup)
    bot.register_next_step_handler(msg, process_segment_step)


def process_segment_step(message):
    try:
        chat_id = message.chat.id
        user_data[chat_id] = {'segment': message.text, 'date': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                              'sender': message.from_user.username}

        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        if message.text == "Digital Skills":
            courses = ["Программирование", "Графический дизайн", "Маркетинг"]
        else:
            courses = ["8 класс", "9 класс", "10 класс", "11 класс"]
        for course in courses:
            markup.add(course)
        msg = bot.reply_to(message, "Выберите курс:", reply_markup=markup)
        bot.register_next_step_handler(msg, process_course_step)
    except Exception as e:
        bot.reply_to(message, 'Ошибка: ' + str(e))


def process_course_step(message):
    try:
        chat_id = message.chat.id
        user_data[chat_id]['course'] = message.text

        msg = bot.reply_to(message, 'Введите текст опечатки:')
        bot.register_next_step_handler(msg, process_typo_step)
    except Exception as e:
        bot.reply_to(message, 'Ошибка: ' + str(e))


def process_typo_step(message):
    try:
        chat_id = message.chat.id
        user_data[chat_id]['typo'] = message.text

        save_typo(chat_id)

        bot.reply_to(message, 'Спасибо! Ваша опечатка сохранена.')
    except Exception as e:
        bot.reply_to(message, 'Ошибка: ' + str(e))


def save_typo(chat_id):
    data = user_data[chat_id]

    with open("typos.txt", "a") as file:
        file.write(f"{data['date']}, {data['sender']}, {data['segment']}, {data['course']}, {data['typo']}\n")

    try:
        worksheet = spreadsheet.worksheet(data['segment'])
    except gspread.exceptions.WorksheetNotFound:
        worksheet = spreadsheet.add_worksheet(title=data['segment'], rows="100", cols="20")

    worksheet.append_row([data['date'], data['sender'], data['segment'], data['course'], data['typo']])


if __name__ == '__main__':
    bot.polling(none_stop=True)
