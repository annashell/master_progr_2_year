# conditions = any([10 > 5, 7 == 9])
# print(conditions)
#
# cond_1 = all([10 > 5, 7 == 9])
# print(cond_1)
#
# a = '1234'
# ls: list = [int(x) for x in a]
# ls2 = list(map(int, a))
#
# print(ls, ls2)
#
# sp = [("hello", 10), ("nn", 5), ("kkk", 7)]
# sp.sort()
# print(sp)
#
# sp.sort(key=lambda x: x[1])
# print(sp)
#
#
# def f(b):
#     return b[1]
#
#
# sp.sort(key=f)
# print(sp)
import sqlite3
from itertools import groupby

sqlite_connection = sqlite3.connect('corpres_seg.db')
cursor = sqlite_connection.cursor()

cursor.execute('SELECT * FROM intonation_units')
syntagmas = cursor.fetchall()

sqlite_connection.commit()
sqlite_connection.close()

key_func = lambda f: len(f[6].split())
sorted_syntagmas = sorted(syntagmas, key=key_func)
grouped_syntagmas = groupby(sorted_syntagmas, key_func)

print(len(syntagmas))

less_then_3_words_count = sum(len(list(v)) for k, v in grouped_syntagmas if k < 3)
print("lambda: ", less_then_3_words_count)
