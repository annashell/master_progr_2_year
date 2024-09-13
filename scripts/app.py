# def f(b: str):
#     return b.capitalize()
#
#
# a: str = 'Hello'
#
# print(a)
#
# import sys
# print(sys.executable)


# TODO обработка текста: написать нормализатор словосочетания сущ+прил (менять падеж + число(если можно))
# TODO табличка - сохранить csv через запятые. Написать прогу, которая достанет все русские термины из файла и сохранить в текстовый файл


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