#! python3
# chatty.py - Telegram-бот
# Требования: chatterbot, chatterbot-corpus, pyTelegramBotApi
import telebot, sqlite3
from chatterbot import ChatBot # Основа бота
from chatterbot.trainers import ListTrainer # Тренер
from chatterbot.trainers import ChatterBotCorpusTrainer # Тренер

# Запишите в переменную TOKEN ключ бота 
TOKEN = ""
# И предпочитаемое имя бота
NAME = "Чатти"

# Логгирование работы бота
import logging
logging.basicConfig(level=logging.INFO)

from chatterbot.comparisons import JaccardSimilarity
from chatterbot.response_selection import get_random_response


# БЭКЕНД БОТА
bot_backend = ChatBot(
	# Имя бота
	NAME,
	# Адаптер базы данных на сервере для хранения реплик						
	storage_adapter="chatterbot.storage.SQLStorageAdapter",
	# Ссылка на БД
	database_uri='sqlite:///database.sqlite3',
	# Обработчики ввода
	preprocessors = [
		'chatterbot.preprocessors.clean_whitespace'
	],
	
	# Логические адаптеры: что бот способен делать
	logic_adapters=[
		# Разговор
		{
			'import_path': 'chatterbot.logic.BestMatch',
			'statement_comparison_function': JaccardSimilarity,
            'response_selection_method': get_random_response,
            'maximum_similarity_threshold': 0.75,
            'default_response': 'Простите, я не понимаю. Попробуйте спросить о чём-то другом.'
        },
        # Арифметика
		{
			'import_path': 'mathematical_evaluation_ru.MathematicalEvaluation',
		},
        # Вывод текущего времени
        {
        	'import_path': 'time_adapter_ru.TimeLogicAdapter',
        },
        # Определённый ответ на определённый запрос
        {
        	'import_path': 'specific_response_fix.SpecificResponseAdapter',
        	'input_text': 'THAT_DAMN_SQLITE3_PROGRAMMING_ERROR',
        	'output_text': 'Ой, у мен возникла внутренняя ошибка! Попробуйте ещё раз.'
        },
        # Поиск документов
        {
        	'import_path': 'fetch_document.FetchDocument'
        },
        # Открой мне статью про покемона
        {
        	'import_path': 'bulbapedia.Bulbapedia'
        }
	],
)


# Тренер обучает бота диалогам на РУССКОМ языке
trainer = ChatterBotCorpusTrainer(bot_backend)
trainer.train("chatterbot.corpus.russian")

trainer = ListTrainer(bot_backend)
trainer.train([
	"Конец выборки. Скажите, нашли ли вы то, что искали?",
	"Да",
	"Рад помочь вам!"
])
trainer.train([
	"Конец выборки. Скажите, нашли ли вы то, что искали?",
	"Нет",
	"Мне жаль. Чем ещё я могу помочь вам?"
])

# ФРОНТЭНД БОТА
bot_frontend = telebot.TeleBot(token = TOKEN)


# Обработчик команды /start
@bot_frontend.message_handler(commands = ['start'])
def start(message):
	bot_frontend.reply_to(message, f"Добрый день, меня зовут {NAME}")


# Обработчик сообщений - генерирует ответ с помощью бэкенда
@bot_frontend.message_handler()
def echo_message(message):
	try:
		response = bot_backend.get_response(message.text)
	except sqlite3.ProgrammingError:
		response = bot_backend.get_response("THAT_DAMN_SQLITE3_PROGRAMMING_ERROR")
	finally:
		bot_frontend.reply_to(message, response)


# Запускается прослушивание чата
print("Bot is online!")
bot_frontend.polling()
