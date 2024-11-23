import glob
import sqlite3

import numpy as np
import tf_keras.losses
from tf_keras import Input, Model
from tf_keras.src.layers import Embedding, LSTM, Dense
from tf_keras.src.optimizers import RMSprop, Adam

from tf_keras.src.preprocessing.text import Tokenizer
from tf_keras.src.utils import pad_sequences

from scripts.nlp.seg_classes import Seg


# слово в виде букв на вход


def get_word_transcription_pairs_from_db(db_path):
    questions = []
    answers = []

    sqlite_connection = sqlite3.connect(db_path)
    cursor = sqlite_connection.cursor()

    cursor.execute(
        'select word_units.unit, ideal_transcription.unit from ideal_transcription inner join word_units on ideal_transcription.word_index = word_units.word_id')
    rows = cursor.fetchall()
    for row in rows:
        questions.append(" ".join(list(row[0])))
        answers.append(" ".join(list(row[1])))

    return questions, answers


# # TODO
# def get_word_transcription_pairs_from_fld(folder_name):
#     questions = []
#     answers = []
#
#     seg_list_B1 = glob.glob(f"{folder_name}/*/*.seg_B1", recursive=True)
#     seg_list_Y1 = glob.glob(f"{folder_name}/*/*.seg_Y1", recursive=True)
#
#     if seg_file in seg_list_Y1:
#         seg_R2 = Seg(seg_file)
#         seg_R2.read_seg()
#
#     return questions, answers


def match_words_to_sounds(filename_upper: str, filename_lower: str) -> list:
    """
    Возвращает элементы словаря на основе пары seg-файлов
    """
    seg_upper = Seg(filename_upper)
    seg_lower = Seg(filename_lower)
    seg_upper.read_seg_file()
    seg_lower.read_seg_file()

    # params, labels_upper = read_seg_file(filename_upper, encoding="cp1251")
    # _, labels_lower = read_seg_file(filename_lower)
    res = []
    ctr = 0
    for start, end in zip(seg_upper.labels, seg_upper.labels[1:]):
        if not start["name"]:
            continue
        labels = []
        for label in seg_lower.labels[ctr:]:
            if start["position"] <= label["position"] < end["position"]:
                ctr += 1
                labels.append(label)
            elif end["position"] <= label["position"]:
                break
        label_names = [i["name"] for i in labels if i["name"]]
        word = " ".join(list(start['name']))
        res.append(f"{word}\t" + " ".join(label_names) + "\n")
    return res


def get_segs_pairs(fld_name: str) -> list:
    """
    Возвращает пары seg-файлов, соответствующие одному wav-файлу
    """
    seg_list_B1 = glob.glob(f"{fld_name}/*.seg_B1", recursive=True)
    return [(seg_b, seg_b[:-3] + "_Y1") for seg_b in seg_list_B1]


def remove_duplicates(lst: list) -> list:
    return list(set(lst))


def get_word_dictionary(fld_name: str, res_filename="dict.txt") -> None:
    """
    Возвращает словарь на основе всех seg-файлов из указанной папки
    """
    seg_pairs = get_segs_pairs(fld_name)
    words_to_sounds = [match_words_to_sounds(seg_y, seg_b) for (seg_b, seg_y) in seg_pairs]
    words_to_sounds_merged_ = [element for each_list in words_to_sounds for element in
                               each_list]  # объединяем списки в один
    words_to_sounds_merged = [s[5:] if s.startswith("[") else s for s in
                              words_to_sounds_merged_]  # удаляем [+] и [-] в начале строк
    words_to_sounds_merged_sorted = sorted(remove_duplicates(words_to_sounds_merged),
                                           key=str.lower)  # удаляем одинаковые строки и сортируем без учета регистра
    with open(res_filename, "w") as f:
        f.writelines(words_to_sounds_merged_sorted)

    return


get_word_dictionary(r"D:\corpres\cta_seg")


def get_word_pairs_from_dict(dict_filename):
    with open(dict_filename, 'r') as f:
        lines = f.readlines()

    questions = []
    answers = []
    for line in lines:
        word = line.split("\t")[0]
        transcription = line.split("\t")[1][:-1]
        if word not in questions:
            questions.append(word)
            answers.append(transcription)

    answers = ['<START> ' + s + ' <END>' for s in answers]

    return questions, answers


questions, answers = get_word_pairs_from_dict(
    r'D:\projects\master_progr_2_year\scripts\nlp\dict.txt')

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

model.compile(optimizer=Adam(), loss=tf_keras.losses.SparseCategoricalCrossentropy(), metrics="accuracy")

print(model.summary())

# Запустим обучение
model.fit([encoderForInput, decoderForInput], decoderForOutput, batch_size=32, epochs=50)

# Сохраним модель на диске
model.save('content/model_50epochs_transcriptor.h5')


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


def strToTokens(word: str):
    '''
        Args: фраза

        Returns: список токенов
    '''

    # Приведем слово к нижнему регистру и разберем на буквы
    letters = list(word.lower())

    # Создадим список для последовательности токенов/индексов
    tokensList = list()

    # Для каждого слова в предложении
    for letter in letters:

        try:
            tokensList.append(tokenizer.word_index[letter])  # Определяем токенайзером индекс и добавляем в список
        except:
            pass  # Слова нет - просто игнорируем его

    # Вернёт входную фразу в виде последовательности индексов
    if tokensList:
        return pad_sequences([tokensList], maxlen=maxLenQuestions, padding='post')

    # Фраза из незнакомых слов - вернем None
    return None


encModel, decModel = makeInferenceModels()

# Цикл по количеству входных фраз - их 6
for _ in range(3):
    # подготовка
    qua = strToTokens(input('Слово: '))
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
