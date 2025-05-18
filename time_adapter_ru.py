#! python3
# time_adapter.py - Логический адаптер вывода времени исправленный для поддержки русского языка

from datetime import datetime
from chatterbot.logic import LogicAdapter
from chatterbot.conversation import Statement


class TimeLogicAdapter(LogicAdapter):
    """
    The TimeLogicAdapter returns the current time.

    :kwargs:
        * *positive* (``list``) --
          The time-related questions used to identify time questions.
          Defaults to a list of English sentences.
        * *negative* (``list``) --
          The non-time-related questions used to identify time questions.
          Defaults to a list of English sentences.
    """

    def __init__(self, chatbot, **kwargs):
        super().__init__(chatbot, **kwargs)
        from nltk import NaiveBayesClassifier
        
        self.positive = ['сколько сейчас время', 'сколько время сейчас', 'время', 'часы', 'текущее время', 'время сейчас', 'какое время сейчас', 'какое сейчас время', 'ты знаешь какое сейчас время', 'можешь сказать мне время, пожалуйста', 'ты мне скажешь время', 'скажи мне время', 'время пожалуйста', 'покажи мне время', 'какое время', 'что на часах', 'покажи мне часы', 'что на часах', 'сколько на часах', 'который час'] #
        
        self.negative = ['что ты делаешь', 'когда время', 'ты', 'какой', 'ты мне', 'скажи мне', 'покажи', 'покажешь', 'покажи', 'скажи', 'мне', 'можешь', 'что', 'какое', 'у меня время', 'кто', 'зимнее время', 'летнее время', 'когда', 'сколько', 'как'] #
        
        '''
        self.positive = kwargs.get('positive', [
            'what time is it',
            'hey what time is it',
            'do you have the time',
            'do you know the time',
            'do you know what time it is',
            'what is the time'
        ])

        self.negative = kwargs.get('negative', [
            'it is time to go to sleep',
            'what is your favorite color',
            'i had a great time',
            'thyme is my favorite herb',
            'do you have time to look at my essay',
            'how do you have the time to do all this'
            'what is it'
        ])
        '''
        labeled_data = (
            [
                (name, 0) for name in self.negative
            ] + [
                (name, 1) for name in self.positive
            ]
        )

        train_set = [
            (self.time_question_features(text), n) for (text, n) in labeled_data
        ]

        self.classifier = NaiveBayesClassifier.train(train_set)
        
    def can_process(self, statement): #
        if "час" in statement.text.lower() or \
            "время" in statement.text.lower():
            return True
        return False

    def time_question_features(self, text):
        """
        Provide an analysis of significant features in the string.
        """
        features = {}

        # A list of all words from the known sentences
        all_words = " ".join(self.positive + self.negative).split()

        # A list of the first word in each of the known sentence
        all_first_words = []
        for sentence in self.positive + self.negative:
            all_first_words.append(
                sentence.split(' ', 1)[0]
            )

        for word in text.split():
            features['first_word({})'.format(word)] = (word in all_first_words)

        for word in text.split():
            features['contains({})'.format(word)] = (word in all_words)

        for letter in 'абвгдеёжзийклмнопрстуфхцчшщьыъэюя': #
            features['count({})'.format(letter)] = text.lower().count(letter)
            features['has({})'.format(letter)] = (letter in text.lower())
        

        return features

    def process(self, statement, additional_response_selection_parameters=None):
        now = datetime.now()

        time_features = self.time_question_features(statement.text.lower())
        confidence = self.classifier.classify(time_features)
        
        print(time_features)
        print(confidence)
        
        response = Statement(text='Текущее время: ' + now.strftime('%I:%M %p')) #

        response.confidence = confidence
        
        return response
