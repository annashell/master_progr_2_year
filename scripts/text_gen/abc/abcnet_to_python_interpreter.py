import re

text = 'print(10, 5)'


# print(10, 5, end=' ')


def print_interpreter(i, line):
    new_line = ""
    if not line.endswith(";"):
        print(f"Error: line {i} should end with ;")
        return

    closing_brackets = [i for i, char in enumerate(line) if char == ')']
    dollar_signs = [i for i, char in enumerate(line) if char == '$']

    for index in dollar_signs:
        if line[:index] == "print(" or line[:index] == "println(":
            line = line[:index] + 'f' + line[index + 1:]

    if line.startswith("print("):
        new_line = line[:closing_brackets[-1]] + ", end=' ')"
    if line.startswith("println("):
        new_line = line[:5] + line[7: closing_brackets[-1]] + " + '\n', end=' ')"

    return new_line


def println_interpreter():
    pass


def main_block_interpreter():
    pass


def function_interpreter():
    pass


def process_abcnet_program(filename: str):
    with open(filename, 'r') as file:
        lines = file.readlines()

    lines = [line.lower() for line in lines if line != '\n']

    new_lines = ["" for i in lines]

    if "end." not in lines:
        print("Error: program doesn't have a proper ending")
        return

    begin_lines_indexes = [i for i, line in enumerate(lines) if line.strip().startswith("begin")]
    end_lines_indexes = [i for i, line in enumerate(lines) if line.strip().startswith("end")]

    if len(begin_lines_indexes) != len(end_lines_indexes):
        print("Error: number of begin lines is not equal to number of end; lines")
        return

    begin_main_index = 0
    end_main_index = lines.index("end.")

    for index in begin_lines_indexes:
        if index != 0 and not lines[index - 1].startswith("function"):
            begin_main_index = index

    function_lines_indexes = [i for i, line in enumerate(lines) if line.strip().startswith("function")]
    print_lines_indexes = [i for i, line in enumerate(lines) if line.strip().startswith("print")]

    for i in print_lines_indexes:
        new_lines[i] = print_interpreter(i, lines[i].strip())

    print(lines)
    print(new_lines)
    print(begin_main_index)
    print(end_main_index)


process_abcnet_program('program.pas')
