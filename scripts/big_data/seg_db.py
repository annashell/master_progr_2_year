import glob
import os
import sqlite3

from scripts.nlp.seg_classes import Seg


# TODO
# Иерархическая БД сегов корпресса
# (tables:
# файлы (id, filename),
# синтагмы (id, filename, unit, from, to) -
# слова (св. с синтагмой),
# ид.транскрипция (cв. со словом),
# реал. транскрипция (cв. со словом),
# аллофоны (cв. со словом)
# чот (связь с аллофоном, границы периода))


def create_init_sql_query():
    query: str = '''CREATE TABLE filenames (
                                id INTEGER PRIMARY KEY,
                                filename TEXT NOT NULL);
                                
                                CREATE TABLE intonation_units (
                                    id INTEGER PRIMARY KEY,
                                    filename TEXT NOT NULL,
                                    unit TEXT NOT NULL,
                                    start INTEGER,
                                    end INTEGER,
                                    seg_index INTEGER,
                                    syntagma_text TEXT NOT NULL);
                                    
                                    CREATE TABLE words_units (
                                    id INTEGER PRIMARY KEY,
                                    filename TEXT NOT NULL,
                                    unit TEXT NOT NULL,
                                    start INTEGER,
                                    end INTEGER,
                                    syntagma_index INTEGER,
                                    seg_index INTEGER);
                                    
                                    CREATE TABLE allophones (
                                    id INTEGER PRIMARY KEY,
                                    filename TEXT NOT NULL,
                                    unit TEXT NOT NULL,
                                    start INTEGER,
                                    end INTEGER,
                                    word_index INTEGER,
                                    seg_index INTEGER);
                                    
                                    CREATE TABLE transcription (
                                    id INTEGER PRIMARY KEY,
                                    filename TEXT NOT NULL,
                                    unit TEXT NOT NULL,
                                    start INTEGER,
                                    end INTEGER,
                                    word_index INTEGER,
                                    seg_index INTEGER);
                                    
                                    CREATE TABLE ideal_transcription (
                                    id INTEGER PRIMARY KEY,
                                    filename TEXT NOT NULL,
                                    unit TEXT NOT NULL,
                                    start INTEGER,
                                    end INTEGER,
                                    word_index INTEGER,
                                    seg_index INTEGER);
                                    
                                    CREATE TABLE f0 (
                                    id INTEGER PRIMARY KEY,
                                    filename TEXT NOT NULL,
                                    unit TEXT NOT NULL,
                                    start INTEGER,
                                    end INTEGER,
                                    allophone_index INTEGER,
                                    seg_index INTEGER);'''.strip()

    with open("sqlite_create_tables.sql", "w", encoding="UTF-8") as wh:
        wh.write(query)


def fill_tables(connection, folder_name):
    seg_list_B1 = glob.glob(f"{folder_name}/*/*.seg_B1", recursive=True)
    seg_list_B2 = glob.glob(f"{folder_name}/*/*.seg_B2", recursive=True)
    seg_list_Y1 = glob.glob(f"{folder_name}/*/*.seg_Y1", recursive=True)
    seg_list_G1 = glob.glob(f"{folder_name}/*/*.seg_G1", recursive=True)
    seg_list_R2 = glob.glob(f"{folder_name}/*/*.seg_R2", recursive=True)

    all_segs: list = seg_list_Y1 + seg_list_B1 + seg_list_B2 + seg_list_G1 + seg_list_R2

    for file_unique_index, seg_file in enumerate(all_segs):
        head, tail = os.path.split(seg_file)
        fill_filenames_table(connection, tail, file_unique_index)
        wav_filename = tail.split(".")[0] + ".wav"

        if seg_file in seg_list_R2:
            seg_R2 = Seg(seg_file)
            seg_R2.read_seg()

            seg_filename_Y1 = seg_file.split(".")[0] + ".seg_Y1"
            seg_Y1 = Seg(seg_filename_Y1)
            seg_Y1.read_seg()
            words_poses = seg_Y1.poses

            seg_filename_B1 = seg_file.split(".")[0] + ".seg_B1"
            seg_B1 = Seg(seg_filename_B1)
            seg_B1.read_seg()
            alloph_poses = seg_B1.poses

            seg_filename_B2 = seg_file.split(".")[0] + ".seg_B2"
            seg_B2 = Seg(seg_filename_B2)
            seg_B2.read_seg()
            id_alloph_poses = seg_B2.poses

            seg_filename_G1 = seg_file.split(".")[0] + ".seg_G1"
            seg_G1 = Seg(seg_filename_G1)
            seg_G1.read_seg()
            f0_poses = seg_G1.poses

            syntagmas: list = seg_R2.labels
            for i_synt, syntagma in enumerate(syntagmas):
                if syntagma.startswith("p") or len(syntagma) == 0:  # если это пауза или какая-то ерунда
                    continue
                syntagma_unique_index = int(str(file_unique_index) + "00" + str(i_synt))
                synt_start = seg_R2.poses[i_synt]
                try:
                    synt_end = seg_R2.poses[i_synt + 1]
                except IndexError:  # мало ли что
                    print("err in: ", syntagma, seg_filename_Y1)
                    continue
                syntagma_text = ""

                for word_start, word_end in zip(words_poses, words_poses[1:]):
                    if synt_start <= word_start < synt_end:
                        transcription = ""
                        ideal_transcription = ""

                        # TODO некрасивое
                        seg_index_word = file_unique_index - 400
                        i_word = words_poses.index(word_start)
                        word_unique_index = int(str(syntagma_unique_index) + str(i_word))
                        word = seg_Y1.labels[i_word]
                        syntagma_text += word + " "
                        fill_words_units_table(connection, wav_filename, word, syntagma_unique_index,
                                               word_start, word_end, word_unique_index, seg_index_word)

                        for alloph_start, alloph_end in zip(alloph_poses, alloph_poses[1:]):
                            if word_start <= alloph_start < word_end:
                                seg_index_alloph = file_unique_index - 300
                                i_alloph = alloph_poses.index(alloph_start)
                                allophone_unique_index = int(str(syntagma_unique_index) + str(i_word) + str(i_alloph))
                                alloph_name = seg_B1.labels[i_alloph]
                                fill_allophones_table(connection, wav_filename, alloph_name,
                                                      word_unique_index,
                                                      alloph_start, alloph_end, allophone_unique_index,
                                                      seg_index_alloph)
                                transcription += alloph_name

                                for f0_period_start, f0_period_end in zip(f0_poses, f0_poses[1:]):
                                    if alloph_start <= f0_period_start < alloph_end:
                                        seg_index_f0 = file_unique_index - 100
                                        i_f0 = f0_poses.index(f0_period_start)
                                        f0_unique_index = int(
                                            str(syntagma_unique_index) + str(i_word) + str(i_alloph) + str(i_f0))
                                        p = seg_G1.params
                                        f0_freq = (
                                                          f0_period_end - f0_period_start) / p.samplerate / p.sampwidth * p.samplerate
                                        fill_f0_table(connection, wav_filename, f0_freq,
                                                      allophone_unique_index,
                                                      f0_period_start, f0_period_end, f0_unique_index,
                                                      seg_index_f0)

                        for id_alloph_start, id_alloph_end in zip(id_alloph_poses, id_alloph_poses[1:]):
                            if word_start <= id_alloph_start < word_end:
                                i_alloph = id_alloph_poses.index(id_alloph_start)
                                ideal_transcription += seg_B2.labels[i_alloph]

                        seg_index_tr = file_unique_index - 300
                        seg_index_ideal_tr = file_unique_index - 200
                        transcription_unique_index = word_unique_index
                        ideal_transcription_unique_index = str(int(word_unique_index) + int("00"))
                        fill_transcription_table(connection, wav_filename, transcription,
                                                 word_unique_index,
                                                 word_start, word_end, transcription_unique_index,
                                                 seg_index_tr, False)

                        fill_transcription_table(connection, wav_filename, ideal_transcription,
                                                 word_unique_index,
                                                 word_start, word_end, ideal_transcription_unique_index,
                                                 seg_index_ideal_tr, True)

                fill_intonation_units_table(connection, wav_filename, file_unique_index, syntagma_unique_index,
                                            syntagma, synt_start, synt_end, syntagma_text)

            print("Seg-file " + seg_file + " added to the database")


def fill_filenames_table(connection, filename, index):
    cursor = connection.cursor()
    sqlite_insert_query = f"""INSERT INTO filenames (id, filename)  VALUES  (?, ?)"""

    data = [
        (index, filename)
    ]

    cursor.executemany(sqlite_insert_query, data)
    connection.commit()
    cursor.close()


def fill_intonation_units_table(connection, wav_filename, seg_unique_index, syntagma_unique_index, syntagma_mark, start,
                                end, syntagma_text):
    cursor = connection.cursor()
    sqlite_insert_query = f"""INSERT INTO intonation_units (id, filename, unit, start, end, seg_index, syntagma_text)  VALUES  (?, ?, ?, ?, ?, ?, ?)"""

    data = [
        (syntagma_unique_index, wav_filename, syntagma_mark, start, end, seg_unique_index, syntagma_text)
    ]
    try:
        cursor.executemany(sqlite_insert_query, data)
    except sqlite3.Error:
        print(data)
    connection.commit()
    cursor.close()


def fill_words_units_table(connection, wav_filename, word, syntagma_index, start, end, word_unique_index,
                           seg_index_word):
    cursor = connection.cursor()
    sqlite_insert_query = f"""INSERT INTO words_units (id, filename, unit, start, end, syntagma_index, seg_index)  VALUES  (?, ?, ?, ?, ?, ?, ?)"""

    data = [
        (word_unique_index, wav_filename, word, start, end, syntagma_index, seg_index_word)
    ]
    try:
        cursor.executemany(sqlite_insert_query, data)
    except sqlite3.Error:
        print(data)
    connection.commit()
    cursor.close()


def fill_transcription_table(connection, wav_filename, transcription, word_index, start, end,
                             transcription_unique_index,
                             seg_index_alloph, is_ideal):
    cursor = connection.cursor()
    if is_ideal:
        sqlite_insert_query = f"""INSERT INTO ideal_transcription (id, filename, unit, start, end, word_index, seg_index)  VALUES  (?, ?, ?, ?, ?, ?, ?)"""
    else:
        sqlite_insert_query = f"""INSERT INTO transcription (id, filename, unit, start, end, word_index, seg_index)  VALUES  (?, ?, ?, ?, ?, ?, ?)"""

    data = [
        (transcription_unique_index, wav_filename, transcription, start, end, word_index, seg_index_alloph)
    ]
    try:
        cursor.executemany(sqlite_insert_query, data)
    except sqlite3.Error:
        print(data)
    connection.commit()
    cursor.close()


def fill_allophones_table(connection, wav_filename, allophone, word_index, start, end, alloph_unique_index,
                          seg_index_alloph):
    cursor = connection.cursor()
    sqlite_insert_query = f"""INSERT INTO allophones (id, filename, unit, start, end, word_index, seg_index)  VALUES  (?, ?, ?, ?, ?, ?, ?)"""

    data = [
        (alloph_unique_index, wav_filename, allophone, start, end, word_index, seg_index_alloph)
    ]
    try:
        cursor.executemany(sqlite_insert_query, data)
    except sqlite3.Error:
        print(data)
    connection.commit()
    cursor.close()


def fill_f0_table(connection, wav_filename, f0_freq,
                  allophone_index,
                  start, end, f0_unique_index,
                  seg_index_f0):
    cursor = connection.cursor()
    sqlite_insert_query = f"""INSERT INTO f0 (id, filename, unit, start, end, allophone_index, seg_index)  VALUES  (?, ?, ?, ?, ?, ?, ?)"""

    data = [
        (f0_unique_index, wav_filename, f0_freq, start, end, allophone_index, seg_index_f0)
    ]
    try:
        cursor.executemany(sqlite_insert_query, data)
    except sqlite3.Error:
        print(data)
    connection.commit()
    cursor.close()


def main_script(folder_name):
    """"
    Creates and fills seg db from all segs in folder folder_name
    """
    try:
        sqlite_connection = sqlite3.connect('corpres_seg.db')
        cursor = sqlite_connection.cursor()
        print("База данных подключена к SQLite")

        create_init_sql_query()

        with open('sqlite_create_tables.sql', 'r') as sqlite_file:
            sql_script = sqlite_file.read()

        cursor.executescript(sql_script)
        sqlite_connection.commit()
        cursor.close()
        fill_tables(sqlite_connection, folder_name)
        print("Скрипт SQLite успешно выполнен")

    except sqlite3.Error as error:
        print("Ошибка при подключении к sqlite", error)
    finally:
        if (sqlite_connection):
            sqlite_connection.close()
            print("Соединение с SQLite закрыто")


main_script(r"D:\corpres\cta")
