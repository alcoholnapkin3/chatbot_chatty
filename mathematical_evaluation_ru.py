#! python3
# mathematical_evaluation.py - Логический адаптер арифметики исправленный для поддержки русского языка
from chatterbot.logic import LogicAdapter
from chatterbot.conversation import Statement
from chatterbot import languages


class MathematicalEvaluation(LogicAdapter):
    """
    The MathematicalEvaluation logic adapter parses input to determine
    whether the user is asking a question that requires math to be done.
    If so, the equation is extracted from the input and returned with
    the evaluated result.

    For example:
        User: 'What is three plus five?'
        Bot: 'Three plus five equals eight'

    :kwargs:
        * *language* (``object``) --
          The language is set to ``chatterbot.languages.ENG`` for English by default.
    """

    def __init__(self, chatbot, **kwargs):
        super().__init__(chatbot, **kwargs)

        self.language = languages.ENG # Оставляем английский, он надёжнее
        self.cache = {}
        
        self.replacer = { # Замена русскоязычных фраз на цифры и знаки для большей сталибьности
               'плюс': '+',
            'разделить на': '/',
            'деленное на': '/',
            'делить на': '/',
            'минус': '-',
            'вычесть': '-',
            'отнять': '-',
            'умножить': '*',
            'умножить на': '*',
            'умноженное на': '*',
            'квадрат': '^ 2',
            'в квадрате': '^ 2',
            'возведенный в куб': '^ 3',
            'в кубе': '^ 3',
            'степень': '^',
            'в степени': '^',

            'один': 1,
            'два': 2,
            'три': 3,
            'четыре': 4,
            'пять': 5,
            'шесть': 6,
            'семь': 7,
            'восемь': 8,
            'девять': 9,
            'десять': 10,
            'одинадцать': 11,
            'двенадцать': 12,
            'тринадцать': 13,
            'четырнадцать': 14,
            'пятнадцать': 15,
            'шестнадцать': 16,
            'семнадцать': 17,
            'восемнадцать': 18,
            'девятнадцать': 19,
            'двадцать': 20,
            'тридцать': 30,
            'сорок': 40,
            'пятьдесят': 50,
            'шестьдесят': 60,
            'семьдесят': 70,
            'восемьдесят': 80,
            'девяносто': 90,

            'сто': 100,
            'тысяч': 1000,
            'миллион': 1000000,
            'миллиард': 1000000000,
            'триллион': 1000000000000
            }
            
        self.keys = list(self.replacer.keys())
        self.keys.reverse()

    def can_process(self, statement):
        """
        Determines whether it is appropriate for this
        adapter to respond to the user input.
        """
        response = self.process(statement)
        
        self.cache[statement.text] = response
        return response.confidence == 1 

    def process(self, statement, additional_response_selection_parameters=None):
        """
        Takes a statement string.
        Returns the equation from the statement with the mathematical terms solved.
        """
        from mathparse import mathparse

        input_text = statement.text.lower()

        # Use the result cached by the process method if it exists
        if input_text in self.cache:
            cached_result = self.cache[input_text]
            self.cache = {}
            return cached_result
        
        # Корректировка
        
        
        #print(self.replacer.keys())
        #print(list(self.replacer.keys()))
        #print(list(self.replacer.keys()).reverse())
        
        
        for key in self.keys:
            input_text = input_text.replace(key, str(self.replacer[key]))
        
        print(input_text)
        
        # Getting the mathematical terms within the input statement
        expression = mathparse.extract_expression(input_text, language=self.language.ISO_639.upper())

        response = Statement(text=expression.capitalize()) #

        try:
            response.text += ' = ' + str(
                mathparse.parse(expression, language=self.language.ISO_639.upper())
            )

            # The confidence is 1 if the expression could be evaluated
            response.confidence = 1
        except mathparse.PostfixTokenEvaluationException:
            response.confidence = 0

        return response
