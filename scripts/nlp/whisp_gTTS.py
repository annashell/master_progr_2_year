# Основной интерфейс для перевода текста в аудио
from gtts import gTTS

from functools import cache

import whisper
from pprint import pprint

text = "Когда‑то все это дергало, мучило Дмитриева. Из‑за матери у него бывали жестокие перепалки с женой, он доходил до дикого озлобления из‑за какого‑нибудь ехидного словца, сказанного Леной; из‑за жены пускался в тягостные «выяснения отношений» с матерью, после чего мать не разговаривала с ним по нескольку дней. Он упрямо пытался сводить, мирить, селил вместе на даче, однажды купил обеим путевки на Рижское взморье, но ничего путного из всего этого не выходило. Какая‑то преграда стояла между двумя женщинами, и преодолеть ее они не могли. Почему так было, он не понимал, хотя раньше задумывался часто. Почему две интеллигентные, всеми уважаемые женщины – Ксения Федоровна работала старшим библиографом одной крупной академической библиотеки, а Лена занималась переводами английских технических текстов и, как говорили, была отличной переводчицей, даже участвовала в составлении какого‑то специального учебника по переводу, – почему две хорошие женщины, горячо любившие Дмитриева, тоже хорошего человека, и его дочь Наташку, упорно лелеяли в себе твердевшую с годами взаимную неприязнь?"
new_audio_name = 'obmen2.mp3'

# Преобразовываем текст в аудио
tts = gTTS(text, lang='ru')

# Сохраняем в формате мр3
tts.save(new_audio_name)


@cache
def load_model(model_type):
    return whisper.load_model(model_type)


# пример базового применения
model = load_model("medium")
result = model.transcribe(new_audio_name)

pprint(result)