import sqlite3

import numpy as np
from tensorflow.python.keras.models import Model
from keras.src.preprocessing.text import Tokenizer
from keras.src.utils import pad_sequences
from tensorflow.python.keras import Input
from tensorflow.python.keras.layers import Embedding, LSTM, Dense
from tensorflow.python.keras.optimizer_v1 import RMSprop


def get_word_transcription_pairs(db_path):
    questions = []
    answers = []

    sqlite_connection = sqlite3.connect(db_path)
    cursor = sqlite_connection.cursor()

    cursor.execute('select word_units.unit, ideal_transcription.unit from ideal_transcription inner join word_units on ideal_transcription.word_index = word_units.word_id')
    rows = cursor.fetchall()
    for row in rows:
        questions.append(" ".join(list(row[0])))
        answers.append(" ".join(list(row[1])))

    return questions, answers


questions, answers = get_word_transcription_pairs(r'D:\projects\master_progr_2_year\scripts\big_data\corpres_seg.db')

tokenizer = Tokenizer(filters='"#$%&()*+-/;<=>@[\\]^_`{|}~\t\n')
tokenizer.fit_on_texts(questions + answers)

# Список с cодержимым словаря
vocabularyItems = list(tokenizer.word_index.items())

# Размер словаря
vocabularySize = len(vocabularyItems) + 1

# Выведем фрагмент и размер словаря
print('Фрагмент словаря : {}'.format(vocabularyItems[:50]))
print('Размер словаря : {}'.format(vocabularySize))

# Выведем фрагмент и размер словаря
print('Фрагмент словаря : {}'.format(vocabularyItems[:50]))
print('Размер словаря : {}'.format(vocabularySize))

# Разбиваем текст входных фраз на последовательности индексов
tokenizedQuestions = tokenizer.texts_to_sequences(questions)

# Уточняем длину самой длинной фразы
maxLenQuestions = max([len(x) for x in tokenizedQuestions])

# Делаем последовательности одной длины, заполняя нулями более короткие фразы
paddedQuestions = pad_sequences(tokenizedQuestions, maxlen=maxLenQuestions, padding='post')

# Предподготавливаем данные для входа в сеть, переводим в numpy массив
encoderForInput = np.array(paddedQuestions)

# Выведем на экран
print('Пример входной фразы                         : {}'.format(questions[100]))
print('Пример кодированной входной фразы            : {}'.format(encoderForInput[100]))
print('Размеры закодированного массива входных фраз : {}'.format(encoderForInput.shape))
print('Установленная длина входных фраз             : {}'.format(maxLenQuestions))


# Разбиваем текст ответных фраз на последовательности индексов
tokenizedAnswers = tokenizer.texts_to_sequences(answers)

# Уточняем длину самого длинного ответа
maxLenAnswers = max([len(x) for x in tokenizedAnswers])

# Делаем последовательности одной длины, заполняя нулями более ответы
paddedAnswers = pad_sequences(tokenizedAnswers, maxlen=maxLenAnswers, padding='post')

# Предподготавливаем данные для входа в сеть, переводим в numpy массив
decoderForInput = np.array(paddedAnswers)

# Выведем на экран
print('Пример оригинального ответа на вход: {}'.format(answers[100]))
print('Пример кодированного ответа на вход : {}'.format(decoderForInput[100][:30]))
print('Размеры кодированного массива ответов на вход : {}'.format(decoderForInput.shape))
print('Установленная длина ответов на вход : {}'.format(maxLenAnswers))


# Разбиваем текст ответов на последовательности индексов
tokenizedAnswers = tokenizer.texts_to_sequences(answers)

# Делаем последовательности одной длины, заполняя нулями более короткие ответы
paddedAnswers = pad_sequences(tokenizedAnswers, maxlen=maxLenAnswers, padding='post')

# И сохраняем в виде массива numpy
decoderForOutput = np.array(paddedAnswers)

# Создадим энкодер

encoderInputs = Input(shape=(None,))  # Добавим входной слой
encoderEmbedding = Embedding(vocabularySize, 200, mask_zero=True)(encoderInputs)  # Добавим эмбеддинг
encoderOutputs, state_h, state_c = LSTM(200, return_state=True)(encoderEmbedding)  # Добавим LSTM
encoderStates = [state_h, state_c]  # Соберем выходы lstm  в список


# Создадим декодер

decoderInputs = Input(shape=(None,))  # Добавим входной слой
decoderEmbedding = Embedding(vocabularySize, 200, mask_zero=True)(decoderInputs)  # Добавим эмбеддинг
decoderLSTM = LSTM(200, return_state=True, return_sequences=True)  # Создадим LSTM слой
decoderOutputs, _, _ = decoderLSTM(decoderEmbedding, initial_state=encoderStates)  # Прогоним выход embedding через LSTM
decoderDense = Dense(vocabularySize, activation='softmax')  # Создадим dense слой
output = decoderDense(decoderOutputs)  # Прогоним  выход LSTM через DENSE

model = Model([encoderInputs, decoderInputs], output)

model.compile(optimizer=RMSprop(), loss='sparse_categorical_crossentropy')

print(model.summary())

# Запустим обучение
model.fit([encoderForInput, decoderForInput], decoderForOutput, batch_size=256, epochs=20)

# Сохраним модель на диске
model.save('content/model_20epochs_transcriptor.h5')


def makeInferenceModels():
    """ Функция сборки сети для перевода фраз из уже обученных слов
        Args: -
        Returns: модели энкодера и декодера
    """
    # Создадим модель кодера, на входе далее будут закодированные вопросы, на выходе состояния state_h, state_c
    encoderModel = Model(encoderInputs, encoderStates)
    # Создадим модель декодера
    decoderStateInput_h = Input(shape=(200,))  # Добавим входной слой для state_h
    decoderStateInput_c = Input(shape=(200,))  # Добавим входной слой для state_c
    # Соберем оба inputs вместе и запишем в decoderStatesInputs
    decoderStatesInputs = [decoderStateInput_h, decoderStateInput_c]
    # Берём ответы, прошедшие через эмбединг, вместе с состояниями и подаём LSTM cлою
    decoderOutputs, state_h, state_c = decoderLSTM(decoderEmbedding, initial_state=decoderStatesInputs)

    # LSTM даст нам новые состояния
    decoderStates = [state_h, state_c]

    # И ответы, которые мы пропустим через полносвязный слой с софтмаксом
    decoderOutputs = decoderDense(decoderOutputs)
    # Определим модель декодера, на входе далее будут раскодированные ответы (decoderForInputs) и состояния
    # на выходе предсказываемый ответ и новые состояния
    decoderModel = Model([decoderInputs] + decoderStatesInputs, [decoderOutputs] + decoderStates)
    # Вернем рабочие модели энкодера и декодера
    return encoderModel, decoderModel


encModel, decModel = makeInferenceModels()

# Цикл по количеству входных фраз - их 6
for _ in range(3):
    # подготовка
    qua = input('Слово: ')
    if qua is None:
        print("а вот спросите меня о чем-нить полезном: ")  # Выдадим дежурную фразу
        continue  # Пойдем за следущей фразой

    emptyTargetSeq = np.zeros((1, 1))
    emptyTargetSeq[0, 0] = tokenizer.word_index['start']
    stopCondition = False
    decodedTranslation = ''
    statesValues = encModel.predict(qua)

    # пока не сработало стоп-условие
    while not stopCondition:

        # В модель декодера подадим пустую последовательность со словом 'start' и состояния
        decOutputs, h, c = decModel.predict([emptyTargetSeq] + statesValues)
        # Получим индекс предсказанного слова.
        sampledWordIndex = np.argmax(decOutputs[0, 0, :])
        # Создаем переменную для преобразованных на естественный язык слов
        sampledWord = None

        # Переберем в цикле все индексы токенайзера
        for word, index in tokenizer.word_index.items():

            # Если индекс выбранного слова соответствует какому-то индексу из словаря
            if sampledWordIndex == index:
                # Слово, идущее под этим индексом в словаре, добавляется в итоговый ответ
                decodedTranslation += ' {}'.format(word)
                # Выбранное слово фиксируем в переменную sampledWord
                sampledWord = word

        # если сгенерированный ответ превышает заданную максимальную длину ответа
        if len(decodedTranslation.split()) > maxLenAnswers:
            stopCondition = True  # Срабатывает стоп-условие и прекращаем генерацию

        # Создаем пустой массив
        emptyTargetSeq = np.zeros((1, 1))

        # Заносим в него индекс выбранного слова
        emptyTargetSeq[0, 0] = sampledWordIndex

        # Записываем состояния, обновленные декодером
        statesValues = [h, c]

        # И продолжаем цикл с обновленными параметрами

    # Выводим ответ сгенерированный декодером
    print("Транскрипция: ", decodedTranslation)





