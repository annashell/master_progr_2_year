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



print(normalize_word_pair("деревьев высоких"))
