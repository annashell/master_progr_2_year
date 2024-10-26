import datetime
import random

import numpy as np
import tensorflow as tf
from matplotlib import pyplot as plt
from tensorflow.keras import utils

learningRate = 0.5
epochs = 10
batchSize = 100


def data_mnist():
    (X_train, y_train), (X_test, y_test) = tf.keras.datasets.mnist.load_data()

        # как может быть вх слой 500, если это не квадрат
    X_train = X_train.reshape(-1, 784)
    X_test = X_test.reshape(-1, 784)

    X_train = X_train.astype('float32')
    X_test = X_test.astype('float32')
    X_train /= 255
    X_test /= 255

    print('Форма x_train:', X_train.shape)
    print(X_train.shape[0], 'обучающих примеров')
    print(X_test.shape[0], 'проверочных примеров')

    y_train = utils.to_categorical(y_train, 10).astype(np.float32)
    y_test = utils.to_categorical(y_test, 10).astype(np.float32)

    return X_train, y_train, X_test, y_test  # Возвращаем датасет


x_train, y_train, x_test, y_test = data_mnist()

trainableParams = []
trainableParams.append(tf.Variable(tf.random.normal([784, 200], stddev=0.03), name='W1'))

trainableParams.append(tf.Variable(tf.random.normal([200], stddev=0.03), name='b1'))

trainableParams.append(tf.Variable(tf.random.normal([200, 10], stddev=0.03), name='W2'))
trainableParams.append(tf.Variable(tf.random.normal([10]), name='b2'))


def loss(pred, target):
    return tf.losses.categorical_crossentropy(target, pred)


def base(x, params):
    W1 = params[0]
    b1 = params[1]
    W2 = params[2]
    b2 = params[3]

    hiddenOut = tf.nn.relu(x @ W1 + b1)
    y = tf.nn.softmax(hiddenOut @ W2 + b2)
    return y


def model(x):
    y = base(x, trainableParams)
    return y


def print_log(current, amount, params):
    bar_len = 30
    percent = int(current * bar_len / amount)
    progressbar = ''

    for i in range(bar_len):
        if i < percent:
            progressbar += '='
        elif i == percent:
            progressbar += '>'
        else:
            progressbar += '-'

    message = "\r" + str(current) + '/' + str(amount) + ' [' + progressbar + ']  '
    for key in params:
        message += key + str(params[key]) + '. '

    print(message, end='')


optimizer = tf.keras.optimizers.SGD(learning_rate=learningRate)
m = tf.keras.metrics.Accuracy()


def train(model, inputs, outputs):
    with tf.GradientTape() as tape:
        current_loss = tf.reduce_mean(loss(model(inputs), outputs))
        grads = tape.gradient(current_loss, trainableParams)  # гр спуск
        optimizer.apply_gradients(zip(grads, trainableParams))
        m.update_state(np.argmax(outputs, axis=1), np.argmax(model(inputs), axis=1))
    return current_loss, m.result().numpy()


amount_bathces = int(len(x_train) / batchSize)  # Считаем число батчей для каждой эпохи. Понадобится для вывода

for epoch in range(1, epochs + 1):  # Проходим по каждой эпохе
    learningEpochStartTime = datetime.datetime.now()  # Запоминаем время начала эпохи
    print('Эпоха', epoch, '/', epochs)  # Пишем текущую эпоху и общее число эпох
    avg_loss = 0  # Задаем среднюю ошибку

    for batch in range(0, len(x_train), batchSize):  # Проходим по x_train с шагом batchSize
        current_loss, accuracy = train(model, x_train[batch: batch + batchSize], y_train[
                                                                                 batch: batch + batchSize])  # Тренируем сеть и получаем значение ошибки
        avg_loss += current_loss  # Считаем среднюю ошибку

        # Задаем параметры, которые будем выводить
        params = {'Время обучения на эпохе: ': datetime.datetime.now() - learningEpochStartTime,
                  # Считаем время обучения на данной эпохе и добавляем в словарь
                  'loss: ': round(current_loss.numpy(), 4),  # Переводим ошибку в Numpy и добавляем в словарь
                  'accuracy: ': round(accuracy, 4)}  # Добавляем точность в словарь
        if (batch >= len(x_train) - batchSize):  # На последнем батче
            params['loss: '] = round((avg_loss / amount_bathces).numpy(), 4)  # Выводим среднюю ошибку на всей эпохе

        current_batch = int(batch / batchSize) + 1  # Считаем номер текущего батча
        print_log(current_batch, amount_bathces, params)  # Выводим всю нужную информацию

    tf.summary.scalar("avg_loss", avg_loss, step=epoch)  # Сохраняем данные для Tensorboard
    tf.summary.scalar("accuracy", accuracy, step=epoch)  # Сохраняем данные для Tensorboard
    print()  # Вручную переносим каретку на следующую строку, чтобы не стирать финальные значения сети на эпохе

print('Сеть распознала цифры: ')
fig, axs = plt.subplots(1, 10, figsize=(25, 3))  # Создаем полотно из 10 графиков
for i in range(10):  # Проходим по классам от 0 до 9
    label_indexes = np.where(np.argmax(y_test, axis=1) == i)[0]  # Получаем список из индексов положений класса i в y_test
    index = random.choice(label_indexes)  # Случайным образом выбираем из списка индекс
    img = x_test[index]  # Выбираем из x_train нужное изображение
    axs[i].imshow(img.reshape(28, 28), cmap='gray')  # Отображаем изображение i-ым графиков
    print(np.argmax(model([img])), end=' ')
plt.show()  # Показываем изображения
