#! python3
# bulbapedia.py - Выдает статью на Bulbapedia если она существует

from chatterbot.logic import LogicAdapter
from chatterbot.conversation import Statement
import requests

class Bulbapedia(LogicAdapter):
	# Инициалицащия адаптера - создает подключение
    def __init__(self, chatbot, **kwargs):
        super().__init__(chatbot, **kwargs) 
        
	# Проверка того, должен ли адаптер давать свой ответ на поступившее сообщение.
    def can_process(self, statement):
        res = requests.get(f'https://bulbapedia.bulbagarden.net/wiki/{statement.text}')

        if res.status_code == 200:
            return True
        else: return False
	
	# Функция вызывается, если can_process вернул True.
    def process(self, input_statement, additional_response_selection_parameters):
        selected_statement = Statement(text = f"Вот ссылка: \nhttps://bulbapedia.bulbagarden.net/wiki/{input_statement.text}")
        selected_statement.confidence = 1
        
        return selected_statement
