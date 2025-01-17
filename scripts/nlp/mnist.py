from tensorflow.keras.models import Sequential  # Подлючаем класс создания модели Sequential
from tensorflow.keras.layers import Dense  # Подключаем класс Dense - полносвязный слой
import numpy as np  # Подключаем библиотеку numpy

model = Sequential()  # Создаем пустую модель нейронной сети
model.add(Dense(2, input_dim=2, use_bias=False,
                name='my_layer'))  # Добавляем полносвязный слой с 2мя нейронами (указываем, что на вход принимаем вектор из двух элементв) и отключаем использование нейрона смещения
model.add(Dense(1,
                use_bias=False))  # Добавляем полносвязный слой с 1 нейроном (выходной слой нашей модели), здесь уже не требуется указывать размерность входных данных, и также отключаем использование нейрона смещения

model.summary()

weights = model.get_weights()  # Получим веса нашей модели (генерируются случайным образом)
print(weights)  # Отбразим сгенерированные веса

w1 = 0.42  # Зададим коэф. w1 вручную
w2 = 0.15  # Зададим коэф. w2 вручную
w3 = -0.56  # Зададим коэф. w3 вручную
w4 = 0.83  # Зададим коэф. w4 вручную
w5 = 0.93  # Зададим коэф. w5 вручную
w6 = 0.02  # Зададим коэф. w6 вручную
new_weight = [np.array([[w1, w3], [w2, w4]]), np.array([[w5], [w6]])]  # Сформируем список весов
print(new_weight)  # Отобразим сформированный список весов
model.set_weights(new_weight)  # Устанавливаем модели свои собственные веса

weights = model.get_weights()  # Получим веса нашей модели (генерируются случайным образом)
print(weights)  # Отбразим сгенерированные веса

x1 = 7.2  # Установим значение x1
x2 = -5.8  # Установим значение x2
x_train = np.expand_dims(np.array([x1, x2]), 0)  # Создадим набор данных для последующего обучения нейронной сети
print(x_train.shape)

k = np.array([x1, x2])
print(k.shape)

y_linear = model.predict(x_train)  # Получим значение выхода сети, передав на вход вектор из двух элементов [x1, x2]
print(y_linear)  # Выведем результат работы сети

H1 = x1 * w1 + x2 * w2  # Получим значение скрытого нейрона H1
H2 = x1 * w3 + x2 * w4  # Получим значение скрытого нейрона H2
print(H1)  # Выведем значение нейрона H1
print(H2)  # Выведем значение нейрона H2

Y_linear = H1 * w5 + H2 * w6  # Считаем выход сети
print(Y_linear)  # Отобразим вывод сети, посчитанный вручную

print('Значение предикта модели:', round(y_linear[0][0], 6))
print('Значение посчитанное вручную:', round(Y_linear, 6))
