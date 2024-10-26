import datetime
import random

import numpy as np
import tensorflow as tf
from matplotlib import pyplot as plt
from tensorflow.keras import utils


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


padding = "SAME"
num_output_classes = 10
batchSize = 256
epochs = 10
learningRate = 0.001

leaky_relu_alpha = 0.2
dropout_rate = 0.5


def data_cifar():
    (X_train, y_train), (X_test, y_test) = tf.keras.datasets.cifar10.load_data()

    X_train = X_train.astype('float32')
    X_test = X_test.astype('float32')
    X_train /= 255
    X_test /= 255

    print('Форма x_train:', X_train.shape)
    print(X_train.shape[0], 'обучающих примеров')
    print(X_test.shape[0], 'проверочных примеров')

    y_train = utils.to_categorical(y_train, num_output_classes).astype(np.float32)
    y_test = utils.to_categorical(y_test, num_output_classes).astype(np.float32)

    return X_train, y_train, X_test, y_test  # Возвращаем датасет


x_train, y_train, x_test, y_test = data_cifar()


def conv2d(inputs, filters, stride_size):  # Слой для создания сверточного слоя
    out = tf.nn.conv2d(inputs, filters, strides=[1, stride_size, stride_size, 1], padding=padding)
    return tf.nn.leaky_relu(out, alpha=leaky_relu_alpha)


def maxpool(inputs, pool_size, stride_size):  # Слой для применения maxpooling
    return tf.nn.max_pool2d(inputs, ksize=[1, pool_size, pool_size, 1], padding='VALID',
                            strides=[1, stride_size, stride_size, 1])


def dense(inputs, weights):  # Слой для создания полносвязного слоя
    x = tf.nn.leaky_relu(inputs @ weights, alpha=leaky_relu_alpha)
    return tf.nn.dropout(x, rate=dropout_rate)


initializer = tf.initializers.glorot_uniform()  # Инициализатор переменных по форме


def get_weight(shape, name):  # Функция для получения весов
    return tf.Variable(initializer(shape), name=name, trainable=True, dtype=tf.float32)


# Формы слоев
shapes = [
    [1, 3, 3, 3],
    [2, 3, 3, 3],
    [2, 3, 3, 3],
    [2, 3, 3, 3],
    [2, 3, 3, 3],
    [2, 3, 3, 3],
    [48, 32],
    [32, num_output_classes],
]

# Создание весов
weights = []
for i in range(len(shapes)):
    weights.append(get_weight(shapes[i], 'weight{}'.format(i)))


# Модель
def model(x):
    x = tf.cast(x, dtype=tf.float32)
    c1 = conv2d(x, weights[0], stride_size=1)
    c1 = conv2d(c1, weights[1], stride_size=1)
    p1 = maxpool(c1, pool_size=2, stride_size=2)

    c2 = conv2d(p1, weights[2], stride_size=1)
    c2 = conv2d(c2, weights[3], stride_size=1)
    p2 = maxpool(c2, pool_size=2, stride_size=2)

    c3 = conv2d(p2, weights[4], stride_size=1)
    c3 = conv2d(c3, weights[5], stride_size=1)
    p3 = maxpool(c3, pool_size=2, stride_size=2)
    flatten = tf.reshape(p3, shape=(tf.shape(p3)[0], -1))

    d1 = dense(flatten, weights[6])
    logits = tf.matmul(d1, weights[7])

    return tf.nn.softmax(logits)


def loss(pred, target):  # Функция подсчета ошибки
    return tf.losses.categorical_crossentropy(target, pred)


optimizer = tf.optimizers.Adam(learningRate)


def train(model, inputs, outputs):
    m = tf.keras.metrics.Accuracy()  # Задаем метрику
    with tf.GradientTape() as tape:
        current_loss = loss(model(inputs), outputs)
        # Градиентный спуск. Инициализируем через learning rate
        # Функция реализует градиентный спуск и обратное распространение ошибки.
    grads = tape.gradient(current_loss, weights)
    # Применение градиентного спуска
    optimizer.apply_gradients(zip(grads, weights))
    # Подсчет точности сети
    m.update_state(np.argmax(outputs, axis=1), np.argmax(model(inputs), axis=1))
    return tf.reduce_mean(current_loss), m.result().numpy()


amount_bathces = int(len(x_train) / batchSize)  # Считаем число батчей для каждой эпохи. Понадобится для вывода

for epoch in range(1, epochs + 1):
    learningEpochStartTime = datetime.datetime.now()  # Запоминаем время начала эпохи
    print('Эпоха', epoch, '/', epochs)  # Пишем текущую эпоху и общее число эпох
    avg_loss = 0  # Задаем среднюю ошибку
    for batch in range(0, len(x_train), batchSize):
        current_loss, accuracy = train(model, x_train[batch:batch + batchSize], y_train[batch:batch + batchSize])
        avg_loss += current_loss

        params = {'Длительность обучения на эпохе: ': datetime.datetime.now() - learningEpochStartTime,
                  # Считаем время обучения на данной эпохе и добавляем в словарь
                  'loss: ': current_loss.numpy(),  # Переводим ошибку в Numpy и добавляем в словарь
                  'accuracy: ': accuracy}  # Добавляем точность в словарь
        if (batch >= len(x_train) - batchSize):  # На последнем батче
            params['loss: '] = (avg_loss / amount_bathces).numpy()  # Выводим среднюю ошибку на всей эпохе
        current_batch = int(batch / batchSize) + 1  # Считаем номер текущего батча
        print_log(current_batch, amount_bathces, params)
    tf.summary.scalar("avg_loss", avg_loss, step=epoch)  # Сохраняем данные для Tensorboard
    tf.summary.scalar("accuracy", accuracy, step=epoch)  # Сохраняем данные для Tensorboard
    print()  # Вручную переносим каретку на следующую строку, чтобы не стирать финальные значения сети на эпохе

print('Сеть распознала классы: ')
fig, axs = plt.subplots(1, 10, figsize=(25, 3))  # Создаем полотно из 10 графиков
for i in range(10):  # Проходим по классам от 0 до 9
    label_indexes = np.where(np.argmax(y_test, axis=1) == i)[
        0]  # Получаем список из индексов положений класса i в y_test
    index = random.choice(label_indexes)  # Случайным образом выбираем из списка индекс
    img = x_test[index]  # Выбираем из x_train нужное изображение
    axs[i].imshow(img, cmap='gray')  # Отображаем изображение i-ым графиков
    print(np.argmax(model([img])), end=' ')
plt.show()  # Показываем изображения


