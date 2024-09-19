# скрипт, который пройдет по строкам таблицы и поменяет местами ячейки в столбцах ру-фр, если несовпадение
import codecs
from copy import copy
import re

import pymorphy3


def is_russian_letters(my_string):
    rus_letters_count: int = len(re.findall("[А-яё]", my_string))
    return rus_letters_count > len(my_string) / 2


def is_french_letters(my_string):
    fr_letters_count: int = len(re.findall("[A-zàâçéèêëîïôûùüÿñæœ]", my_string))
    return fr_letters_count > len(my_string) / 2


def process_ru_fr_table(filename, res_filename):
    lines = []

    f = open(res_filename, 'w')

    file = codecs.open(filename, "r", "utf-8")
    lines: list = file.readlines()
    file.close()

    for line in lines:
        fields = line.split(";")

        if len(fields) < 6:
            continue

        french_1 = fields[0]
        french_2 = fields[1]
        russian_1 = fields[4]
        russian_2 = fields[5]

        new_fields = copy(fields)

        if ((is_french_letters(russian_1) and (is_russian_letters(french_1) or french_1 == ""))
                or (is_russian_letters(french_1) and (is_french_letters(russian_1) or russian_1 == ""))):
            new_fields[0] = russian_1
            new_fields[4] = french_1

        if ((is_french_letters(russian_2) and (is_russian_letters(french_2) or french_2 == ""))
                or (is_russian_letters(french_2) and (is_french_letters(russian_2) or russian_2 == ""))):
            new_fields[1] = russian_2
            new_fields[5] = french_2

        new_line = ";".join(new_fields)
        try:
            f.write(new_line)
        except UnicodeEncodeError:
            continue
    f.close()


def make_words_dict(csv_filename):
    res_dict: dict = {}

    morph = pymorphy3.MorphAnalyzer()

    file = codecs.open(csv_filename, "r", "cp1251")
    lines: list = file.readlines()[1:]

    for line in lines:
        fields: list = line.strip().split(";")
        if len(fields) < 6:
            continue
        rus_words: list = fields[4].split() + fields[5].split()

        for word in rus_words:
            word_m = morph.parse(word)[0]
            w_type = word_m.tag.POS
            if w_type in res_dict.keys():
                if word_m.normal_form in res_dict[w_type].keys():
                    res_dict[w_type][word_m.normal_form] += 1
                else:
                    res_dict[w_type][word_m.normal_form] = 1
            else:
                res_dict[w_type] = {
                    word_m.word: 1
                }

    return res_dict

old_csv = r"D:\projects\master_progr_2_year\scripts\text_gen\KBM_ALL.csv"
csv_fn = r"D:\projects\master_progr_2_year\scripts\text_gen\new_KBM_ALL.csv"


process_ru_fr_table(old_csv, csv_fn)
make_words_dict(csv_fn)
