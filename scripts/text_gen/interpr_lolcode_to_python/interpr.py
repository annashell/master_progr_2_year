def translate_lol_program_to_python(lines, param):
    pass


def process_lol_program(filename: str):
    with open(filename, 'r') as file:
        lines = file.readlines()
    lines = [line.lower().strip() for line in lines if line != '\n']

    new_lines = translate_lol_program_to_python(lines, 0)

    print(lines)
    for line in new_lines:
        print(line)

    with open(filename.split(".")[0] + ".py", 'w') as file:
        for line in new_lines:
            file.write(line) + "\n"


process_lol_program('lol_examples/program_perimeter.lol')