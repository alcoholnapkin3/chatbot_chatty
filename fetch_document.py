#! python3
# fetch_document.py - Логический адаптер вывода содержимого документов.
# Адаптер взаимодействует с базой данных, находящейся по адресу DOCUMENTS_DATABASE. База состоит из таблицы documents с двумя колонками:
# - Колонка document с названием документа.
# - Колонка text с содержимым документа.
# Изначально в БД записаны .yml-файлы содержащие реплики для диалога ботом на русском языке: conversations.yml, food.yml и money.yml. 
# Содержимое базы данных не имеет отношения к работоспособности бота.

from chatterbot.logic import LogicAdapter
from chatterbot.conversation import Statement
import sqlite3

DOCUMENTS_DATABASE = 'documents.sqlite3'

class FetchDocument(LogicAdapter):
	# Инициалицащия адаптера - создает подключение
    def __init__(self, chatbot, **kwargs):
        super().__init__(chatbot, **kwargs) 
        self.connection = sqlite3.connect(DOCUMENTS_DATABASE, check_same_thread=False)
        self.cursor = self.connection.cursor()
        
	# Проверка того, должен ли адаптер давать свой ответ на поступившее сообщение.
	# Первая функция вызываемая в адаптере при поступлении боту нового сообщения.
	# По умолчанию адаптер проверяет текст сообщения на наличие имен документов.
	# Каждое найденное имя сохраняется в documents_found.
    def can_process(self, statement):
        self.documents_found = []
        
        self.cursor.execute('SELECT document FROM documents')
        answer = self.cursor.fetchall()
        
        for ans in answer:
            if ans[0] in statement.text:
                self.documents_found.append(ans[0])
        
        if not self.documents_found == []:
            return True
        else: return False
	
	# Функция вызывается, если can_process вернул True.
	# Выбирает названия упомянутых документов, их тексты и собирает из них ответ.
    def process(self, input_statement, additional_response_selection_parameters):
        
        selected_statement = ''
        
        for document in self.documents_found:
            selected_statement += f"Документ {document}: \n"
        
            self.cursor.execute(f'''SELECT text 
                FROM documents
                WHERE document="{document}"''')
            
            selected_statement += self.cursor.fetchall()[0][0] + '\n\n'
        
        selected_statement += "Конец выборки. Скажите, нашли ли вы то, что искали?"
        
        selected_statement = Statement(text = selected_statement)
        selected_statement.confidence = 1
        
        return selected_statement
