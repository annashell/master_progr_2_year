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
        new_line = line[:5] + line[7: closing_brackets[-1]] + ", '\n', end=' ')"

    return new_line


def var_assignment_interpreter(i, line):
    if not line.endswith(";"):
        print(f"Error: line {i} should end with ;")
        return

    # TODO Readln(i1, s1, i2, s2, i3);

    line = line.replace("var ", "")
    line = line.replace(":=", "=")
    line = line.replace("readinteger();", "int(input())")
    line = line.replace("readreal();", "float(input())")
    line = line.replace("readlninteger();", "int(input())")
    line = line.replace("readlnreal();", "float(input())")
    line = line.replace("readlnstring();", "input()")
    line = line.replace("readstring();", "input()")
    return line


def main_block_interpreter():
    pass


def function_interpreter(lines):
    new_lines = []
    func_name = lines[0].split("function ")[1].strip().split("(")[0]
    op_bracket = lines[0].index("(")
    cl_bracket = lines[0].index(")")
    arguments = (lines[0][op_bracket: cl_bracket + 1]
                 .replace("integer", "int")
                 .replace("real", "float"))
    new_lines.append(f"def {func_name}({arguments}):")
    for line in lines[1:]:
        if line != "begin" and line != "end;":
            new_lines.append("\t" + line)
    return new_lines


def translate_abcnet_program(lines: list, proc_count: int):

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

    for i in function_lines_indexes:
        if not lines[i + 1] == "begin":
            print(f"Error: format of a function starting at line {i} is invalid")

        for ind in end_lines_indexes:
            if ind > i + 1:
                func_end_index = ind
                break

        func_lines = function_interpreter(lines[i: func_end_index + 1])
        for j in range(len(func_lines) + 2):
            if j > len(func_lines) - 1:
                lines[i + j] = ""
            else:
                lines[i + j] = func_lines[j]
        translate_abcnet_program(lines, proc_count + 1)

    print_lines_indexes = [i for i, line in enumerate(lines) if proc_count == 0 and line.strip().startswith("print")]
    var_assignment_lines_indexes = [i for i, line in enumerate(lines) if ":=" in line.strip()]

    for i in print_lines_indexes:
        lines[i] = print_interpreter(i, lines[i])

    for i in var_assignment_lines_indexes:
        lines[i] = var_assignment_interpreter(i, lines[i])
    return lines


def process_abcnet_program(filename: str):
    with open(filename, 'r') as file:
        lines = file.readlines()
    lines = [line.lower().strip() for line in lines if line != '\n']

    new_lines = translate_abcnet_program(lines, 0)

    print(lines)
    for line in new_lines:
        print(line)


process_abcnet_program('program.pas')
