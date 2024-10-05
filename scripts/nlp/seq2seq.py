# Подключим модуль numpy для работы с массивами
import numpy as np

# Подгрузим модели кераса
from tensorflow.keras.models import Model, load_model

# Подключим нужные слои
from tensorflow.keras.layers import Dense, Embedding, LSTM, Input

# Поключим оптимайзеры
from tensorflow.keras.optimizers import RMSprop, Adadelta

# Подключим метод ограничения последовательности заданной длиной
from tensorflow.keras.preprocessing.sequence import pad_sequences

# Подключим токенайзер
from tensorflow.keras.preprocessing.text import Tokenizer

conversations = []  # Заготовим список для пар фраз

with open(r".\.\data\rus.txt", 'r', encoding='utf-8') as f:
    lines = f.read().split('\n')  # Читаем весь файл, режем на строки

# Цикл по строкам
for i, line in enumerate(lines):

    if i > 50000:  # Нам нужно только 50000 первых строк
        break  # Заканчиваем цикл
    try:
        input_text, target_text, _ = line.split("\t")  # Берем очередную строку, режем по символу табуляции
        conversations.append([input_text, target_text])  # Заполняем список пар фраз
    except:
        continue


def my_replacer(s):
    ''' Функция для удаления пробелов перед знаками препинания

        Args: строка или список строк

        Returns: строка или список строк
    '''

    if isinstance(s, str):  # Если получили строку

        # Убираем перед знаками препинания пробел и возвращаем
        return s.replace(' .', '.').replace(' ,', ',').replace(' !', '!').replace(' ?', '?')

    if isinstance(s, list):  # Если получили список
        ou = []  # Заготовим пустой список

        for l in s:  # Цикл по строкам из списка
            ou.append(l.replace(' .', '.').replace(' ,', ',').replace(' !', '!').replace(' ?',
                                                                                         '?'))  # Убираем перед знаками препинания пробел и возвращаем

        # Вернем список строк
        return ou


# Собираем вопросы и ответы в списки

questions = []  # Переменная для списка входных фраз
answers = []  # Переменная для списка ответных фраз

# Цикл по всем парам фраз
for con in conversations:

    if len(con) > 1:  # Если ответная фраза содержит более одно двух предложений
        questions.append(my_replacer(con[0]))  # То первую в списке фразу отправляем в список входных фраз
        replies = my_replacer(con[1:])  # А ответную составляем из последующих строк
        ans = ' '.join(replies)  # Здесь соберем ответ
        answers.append(ans)  # Добавим в список ответов
    else:
        continue  # Иначе идем на новой парой фраз

# Добавим в каждую ответную фразу теги  <START> и <END>
answers = ['<START> ' + s + ' <END>' for s in answers]

# Выведем обновленные данные на экран
print('Вопрос : {}'.format(questions[111]))  # Пример входной фразы
print('Ответ : {}'.format(answers[111]))  # Пример ответной фразы

# Создадим токенайзер
tokenizer = Tokenizer(filters='"#$%&()*+-/;<=>@[\\]^_`{|}~\t\n', split=' ')

# Загружаем в токенизатор список фраз для сборки словаря частотности
tokenizer.fit_on_texts(questions + answers)

# Список с cодержимым словаря
vocabularyItems = list(tokenizer.word_index.items())

# Размер словаря
vocabularySize = len(vocabularyItems) + 1

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
print('Пример кодированной входной фразу            : {}'.format(encoderForInput[100]))
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

for i in range(len(tokenizedAnswers)):  # Для разбитых на последовательности ответов
    tokenizedAnswers[i] = tokenizedAnswers[i][1:]  # Избавляемся от тега <START>

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
model.fit([encoderForInput, decoderForInput], decoderForOutput, batch_size=256, epochs=3)

# Сохраним модель на диске
model.save('content/model_30epochs(rms).h5')


def strToTokens(sentence: str):
    """ Функция для удаления пробелов перед знаками препинания

        Args: фраза

        Returns: список токенов
    """

    # Почистим фразу
    tmp_sent = my_replacer(sentence)

    # Приведем предложение к нижнему регистру и разбирает на слова
    words = tmp_sent.lower().split()

    # Создадим список для последовательности токенов/индексов
    tokensList = list()

    # Для каждого слова в предложении
    for word in words:

        try:
            tokensList.append(tokenizer.word_index[word])  # Определяем токенайзером индекс и добавляем в список
        except:
            pass  # Слова нет - просто игнорируем его

    # Вернёт входную фразу в виде последовательности индексов
    if tokensList:
        return pad_sequences([tokensList], maxlen=maxLenQuestions, padding='post')

    # Фраза из незнакомых слов - вернем None
    return None


emptyTargetSeq = np.zeros((1, 1))
emptyTargetSeq[0, 0] = 5


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
for _ in range(2):
    # подготовка
    qua = strToTokens(input('Исходное предложение на английском: '))
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

        # Если выбранным словом оказывается 'end' либо если сгенерированный ответ превышает заданную максимальную длину ответа
        if sampledWord == 'end' or len(decodedTranslation.split()) > maxLenAnswers:
            stopCondition = True  # Срабатывает стоп-условие и прекращаем генерацию

        # Создаем пустой массив
        emptyTargetSeq = np.zeros((1, 1))

        # Заносим в него индекс выбранного слова
        emptyTargetSeq[0, 0] = sampledWordIndex

        # Записываем состояния, обновленные декодером
        statesValues = [h, c]

        # И продолжаем цикл с обновленными параметрами

    # Выводим ответ сгенерированный декодером
    print("Перевод: ", decodedTranslation)
