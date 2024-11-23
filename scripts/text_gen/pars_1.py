import re
import pymorphy3


# привести словосочетание сущ+прилаг к нормальной форме
def normalize_word_pair(word_pair: str):
    pair: list = word_pair.split(" ")

    morph = pymorphy3.MorphAnalyzer()

    noun = morph.parse(pair[0])[0]  # Первое - существительное
    adjective = morph.parse(pair[1])[0]  # Второе - прилагательное

    noun_norm: str = noun.inflect({'nomn', 'sing'})
    adjective_norm: str = adjective.inflect({'nomn', 'sing', 'masc'} if noun.tag.gender == 'masc' else
                                            {'nomn', 'sing', 'femn'} if noun.tag.gender == 'femn' else
                                            {'nomn', 'sing', 'neut'})

    res_str = noun_norm.word + " " + adjective_norm.word
    return res_str


# print(normalize_word_pair("деревьев высоких"))


def get_all_word_combinations_dict(text_fn, max_N):
    comb_dict = {}
    with open(text_fn, 'r', encoding="utf-8") as f:
        text = f.read()

    text = text.replace("\n", "")

    text_arr = re.sub("[.,:;!?,()]", " ", text.strip().lower()).split(" ")
    text_arr_filtered = list(filter(lambda el: el != "", text_arr))
    result = [text_arr_filtered[i:i + j] for i in range(len(text_arr)) for j in range(1, max_N + 1)]

    morph = pymorphy3.MorphAnalyzer()

    for comb in result:
        comb_type = ""
        for word in comb:
            comb_type += morph.parse(word)[0].tag.POS
            comb_type += "+"
        comb_type = comb_type[:-1]
        if comb_type in comb_dict.keys():
            comb_dict[comb_type].append(comb)
        else:
            comb_dict[comb_type] = [comb]

    return comb_dict


templates: dict = {
    # модель; проверка, что род, число, падеж одинаковы; что нужно сделать, чтобы привести в норм форму
    "ADJF+NOUN": [["2=gender,case,number", ""], ["2.case+number", "nom+sing"]],
}


def normalize_word_pair(pair_str):
    word1, word2 = pair_str.split(" ")

    morph = pymorphy3.MorphAnalyzer()

    word1_pm = morph.parse(word1)[0]
    word1_pm_class = word1_pm.tag.POS

    word2_pm = morph.parse(word2)[0]
    word2_pm_class = word2_pm.tag.POS

    template = word1_pm_class + "+" + word2_pm_class
    check_cases, norm_rules = templates[template]


# normalize_word_pair("высоких деревьев")

get_all_word_combinations_dict(r"D:\projects\master_progr_2_year\scripts\nlp_transcriptor_app\alice_in_wonderland.txt", 3)
