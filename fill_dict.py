import _sqlite3
import parse


"""заполнение бд"""
db = _sqlite3.connect('bd_dict.db')
sql = db.cursor()

options = ["все", "глаголы", "существительные", "прилагательные"]

sql.execute("""CREATE TABLE "MyDict" (
"eng_word"	TEXT,
"rus_word"	TEXT UNIQUE,
"image"	TEXT,
"studied_not_studied"	INTEGER,
"sound"	TEXT,
"test"	INTEGER
)""")

sql.execute("""CREATE TABLE "DictAll" (
    "eng_word"	TEXT,
    "rus_word"	TEXT UNIQUE,
    "image"	TEXT,
    "add_my_dict"	INTEGER,
    "sound"	TEXT,
    "test"	INTEGER
    )""")

sql.execute("""CREATE TABLE "DictNouns" (
"eng_word"	TEXT,
"rus_word"	TEXT UNIQUE,
"image"	TEXT,
"add_my_dict"	INTEGER,
"sound"	TEXT,
"test"	INTEGE
)""")

sql.execute("""CREATE TABLE "DictVerbs" (
"eng_word"	TEXT,
"rus_word"	TEXT UNIQUE,
"image"	TEXT,
"add_my_dict"	INTEGER,
"sound"	TEXT,
"test"	INTEGER
)""")

sql.execute("""CREATE TABLE "DictAdjectives" (
"eng_word"	TEXT,
"rus_word"	TEXT UNIQUE,
"image"	TEXT,
"add_my_dict"	INTEGER,
"sound"	TEXT,
"test"	INTEGER
)""")

db.commit()

for _ in range(4):
    for word in options:
        print("загрузка")
        x = parse.GetEnglishWords()
        if word == "все":
            eng, rus, images, sounds = x.run('https://kreekly.com/random/')
            for i in range(len(eng)):
                if not sql.execute("""SELECT rus_word FROM DictAll WHERE rus_word = ?""",
                                   (rus[i],)).fetchall():  # проверка есть ли слово в бд
                    sql.execute("""INSERT INTO DictAll VALUES(?, ?, ?, ?, ?, ?)""",
                                (eng[i], rus[i], images[i], 0, sounds[i], 0))  # добавление слов в бд
                    db.commit()
        elif word == "существительные":
            eng, rus, images, sounds = x.run("https://kreekly.com/random/noun/")
            for i in range(len(eng)):
                if not sql.execute("""SELECT rus_word FROM DictNouns WHERE rus_word = ?""",
                                   (rus[i],)).fetchall():  # проверка есть ли слово в бд
                    sql.execute("""INSERT INTO DictNouns VALUES(?, ?, ?, ?, ?, ?)""",
                                (eng[i], rus[i], images[i], 0, sounds[i], 0))  # добавление существительных в бд
                    db.commit()
        elif word == "глаголы":
            eng, rus, images, sounds = x.run("https://kreekly.com/random/verb/")
            for i in range(len(eng)):
                if not sql.execute("""SELECT rus_word FROM DictVerbs WHERE rus_word = ?""",
                                   (rus[i],)).fetchall():  # проверка есть ли слово в бд
                    sql.execute("""INSERT INTO DictVerbs VALUES(?, ?, ?, ?, ?, ?)""",
                                (eng[i], rus[i], images[i], 0, sounds[i], 0))  # добавление глаголов в бд
                    db.commit()
        elif word == "прилагательные":
            eng, rus, images, sounds = x.run("https://kreekly.com/random/adjective/")
            for i in range(len(eng)):
                if not sql.execute("""SELECT rus_word FROM DictAdjectives WHERE rus_word = ?""",
                                   (rus[i],)).fetchall():  # проверка есть ли слово в бд
                    sql.execute("""INSERT INTO DictAdjectives VALUES(?, ?, ?, ?, ?, ?)""",
                                (eng[i], rus[i], images[i], 0, sounds[i], 0))  # добавление прилагательных в бд
                    db.commit()

db.close()
