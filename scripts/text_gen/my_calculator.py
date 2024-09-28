def parse_string_to_numbers_and_symbols(string_to_calculate):
    number = ""
    numbers = []
    for i in range(len(string_to_calculate)):
        if i == 0:
            if string_to_calculate[i].isdigit():
                number += string_to_calculate[i]
            elif string_to_calculate[i] == "-":
                # первое отрицательное
                number += string_to_calculate[i]
            elif string_to_calculate[i] == "+":
                pass
            else:
                print("ERROR", string_to_calculate[0], " cannot exist as the number")
        else:
            if string_to_calculate[i].isdigit():
                number += string_to_calculate[i]
            elif string_to_calculate[i] in "+-*/)(^":
                numbers.append(int(number))
                numbers.append(string_to_calculate[i])
                number = ""
            else:
                print("ERROR", string_to_calculate[0], " cannot exist as the number")

    if number != "":
        numbers.append(number)

    return numbers


def process_degrees(symbols):
    degree_positions = [pos for pos, symb in enumerate(symbols) if symb == '^']

    # удаляем ^ и показатели степени
    i = 0
    while i < len(degree_positions):
        pos = degree_positions[i] - i * 2
        symbols[pos - 1] = int(symbols[pos - 1]) ** int(symbols[pos + 1])
        symbols.pop(degree_positions[i] - i * 2)  # убираем ^
        symbols.pop(degree_positions[i] - i * 2)  # убираем следующее число
        i += 1
    return symbols


def process_brackets(parsed_symbols):
    opening_brackets_pos = [pos for pos, symb in parsed_symbols if symb == '(']
    closing_brackets_pos = [pos for pos, symb in parsed_symbols if symb == ')']
    if len(opening_brackets_pos) != len(closing_brackets_pos):
        raise Exception("Number of closing brackets is not equal to number of opening brackets")

    return parsed_symbols


def process_multiplication_and_division(symbols):
    positions = []
    for pos, symb in enumerate(symbols):
        if symb in ('*', '/'):
            positions.append(pos)

    i = 0
    while i < len(positions):
        pos = positions[i] - i * 2
        symb = symbols[pos]
        if symb == '*':
            new_number = int(symbols[pos - 1]) * int(symbols[pos + 1])  # заменяем число перед * на результат умножения
            symbols[pos - 1] = new_number
        if symb == '/':
            if int(symbols[pos + 1]) == 0:
                raise Exception("Division by zero!")
            new_number = int(symbols[pos - 1]) / int(symbols[pos + 1])  # заменяем число перед / на результат деления
            symbols[pos - 1] = new_number
        symbols.pop(positions[i] - i * 2)  # убираем * /
        symbols.pop(positions[i] - i * 2)  # убираем следующее число
        i += 1

    return symbols


def calculate_simplified_string(symbols):
    positions = []
    for pos, symb in enumerate(symbols):
        if symb in ('+', '-'):
            positions.append(pos)

    # удаляем + и - и последующее число
    i = 0
    while i < len(positions):
        pos = positions[i] - i * 2
        symb = symbols[pos]
        if symb == '+':
            new_number = int(symbols[pos - 1]) + int(symbols[pos + 1])  # заменяем число перед * на результат умножения
            symbols[pos - 1] = new_number
        if symb == '-':
            new_number = int(symbols[pos - 1]) - int(symbols[pos + 1])  # заменяем число перед / на результат деления
            symbols[pos - 1] = new_number
        symbols.pop(positions[i] - i * 2)  # убираем + -
        symbols.pop(positions[i] - i * 2)  # убираем следующее число
        i += 1

    return symbols


def calculator(string_to_calculate: str):
    parsed_symbols = parse_string_to_numbers_and_symbols(string_to_calculate)
    print(parsed_symbols)

    # parsed_symbols = process_brackets(parsed_symbols)
    parsed_symbols = process_degrees(parsed_symbols)
    print(parsed_symbols)
    parsed_symbols = process_multiplication_and_division(parsed_symbols)
    print(parsed_symbols)
    parsed_symbols = calculate_simplified_string(parsed_symbols)
    print(parsed_symbols)

    return parsed_symbols[0]


print("result: ", calculator("1+2^3^5-15*5/5"))
print(1 + (2 ** 3) ** 5 - 15 * 5 / 5)
