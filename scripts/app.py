# TODO
#  интерпретатор паскаля ABCNet - породить код на питоне (циклы, функции) - конечный автомат
# калькулятор
# 1. Пусть нет скобок, только цифры, числа, пробелы (replace) и знаки препинания
# 2. Если что-то не так - ошибка
# 3. Все мат операции, любое число скобок, модули(*)
# 4. два подряд одинаковых знака - игнорируем второй, разных - ошибка


#TODO Tensorflow-2 на сайте
# seq2seq разбить на обучение и интерфейс для использования


# TODO Юнит тесты калькулятора, введение в современное программирование Осипов










def mydecorator(f):
    mydict: dict = {}

    def wrapper(n: int):
        if n in mydict:
            return mydict[n]
        result = f(n)
        mydict[n] = result
        return result

    return wrapper


@mydecorator
def factorial(n: int):
    if n == 1:
        return 1
    return n * factorial(n - 1)


# factorial = mydecorator(factorial)

print(factorial(100) // factorial(90))


a: str = "a"
print(ord(a), chr(97))
for i in range (ord('a'), ord('z') + 1):
    print(chr(i), end=" ")

for i in range (ord('а'), ord('я') + 1):
    print(chr(i), end=" ")

letter = 'э'
if ord('а') <= ord(letter) <= ord('я') or letter == 'ё':
    print("Русский")