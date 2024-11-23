from functools import cache

import whisper
from pprint import pprint


@cache
def load_model(model_type):
    return whisper.load_model(model_type)


# пример базового применения
model = load_model("medium")
result = model.transcribe(r"D:\projects\master_progr_2_year\scripts\nlp\data\cta0003.wav")

pprint(result)
