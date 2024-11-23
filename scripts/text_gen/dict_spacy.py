# TODO
# частотно-алфавитный словарь NOUN, NOUN+...
# вытащить предложения в разных временах из текста
# найти все имена
import re

import spacy

text_fn = r"D:\projects\master_progr_2_year\scripts\text_gen\alice_in_wonderland.txt"


def get_freq_dict(text_fn):
    sp_dict = {}

    with open(text_fn, 'r', encoding="utf-8") as f:
        text = f.read()

    nlp = spacy.load('en_core_web_md')
    text = nlp(text.strip())

    for token in text:
        if token.tag_ in sp_dict.keys():
            if token.lemma_ in sp_dict[token.tag_].keys():
                sp_dict[token.tag_][token.lemma_] += 1
            else:
                sp_dict[token.tag_][token.lemma_] = 1
        else:
            sp_dict[token.tag_] = {
                token.lemma_: 1
            }
    return sp_dict

# print(get_freq_dict(doc))

