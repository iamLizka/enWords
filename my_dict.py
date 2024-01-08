import menu
import sqlite3

from PyQt5 import uic
from menu import *
from PyQt5.QtWidgets import QWidget, QInputDialog, QCheckBox, QTableWidgetItem, QMessageBox
from PyQt5 import QtWidgets
from PyQt5.QtGui import *
from gtts import gTTS
from PyQt5 import QtCore, QtMultimedia


"""ошибка в случае, если закончились слова в словаре"""
class RunOutWords(ZeroDivisionError):
    pass


"""словарь пользователя"""
class MyDict(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.filling_my_dict()

    def initUI(self):
        uic.loadUi('Ui/my_dict.ui', self)
        self.setWindowTitle("enWords")
        self.move(430, 160)
        self.setFixedSize(1050, 800)

        self.but_from_dict.clicked.connect(self.exit_to_main_menu)
        self.but_add_random_words.clicked.connect(self.chose_words)
        self.but_delete_all.clicked.connect(self.delete_all)
        self.but_delete_choose.clicked.connect(self.delete_choose)
        self.but_study.clicked.connect(self.studying)
        self.but_add_my_word.clicked.connect(self.check_for_add_my_word)

    """проверка, все ли вписал пользователь"""
    def check_for_add_my_word(self):
        self.check = 1  # если будет check = 1, то можно будет добавить слово в словарь,
        # перед этим проверив есть ли оно уже в словаре, а если будет check = 0, то вывод ошибки,
        # тк какие-то поля незаполнены или что-то не отмечено

        # проверка, заполнены ли строки, куда нужно вписывать слово и перевод
        if (not self.line_word.text()) or (not self.line_translation.text()):
            self.check = 0
            self.show_error_empty_fields()

        # какому языку принадлежит слово в 1 строчке
        if self.rb_rus_1.isChecked():
            self.word_rus = self.line_word.text()
        elif self.rb_eng_1.isChecked():
            self.word_eng = self.line_word.text()
        else:
            self.check = 0
            self.show_error_unselected_language()
            
        # какому языку принадлежит слово во 2 строчке
        if self.rb_rus_2.isChecked():
            self.word_rus = self.line_translation.text()
        elif self.rb_eng_2.isChecked():
            self.word_eng = self.line_translation.text()
        else:
            self.check = 0
            self.show_error_unselected_language()
        if self.check == 1:
            self.addition_my_word()

    """добавление слова, которое написал пользователь, в словарь"""
    def addition_my_word(self):
        # Подключение к БД
        con = sqlite3.connect("bd_dict.db")
        cur = con.cursor()
        # проверка есть ли слово в словаре пользователя
        if [] == cur.execute(f"""SELECT eng_word FROM MyDict WHERE rus_word = ?""", (self.word_rus,)).fetchall():
            # добавление озвучки слова
            tts = gTTS(text=self.word_eng, lang='en')
            save_name = "Sounds/" + self.word_eng + ".mp3"
            tts.save(save_name)

            # добавляем слово в словарь пользователя
            cur.execute("""INSERT INTO MyDict VALUES(?, ?, ?, ?, ?, ?)""",
                        (self.word_eng, self.word_rus,
                         "PyQt5_Project_enWords/not_delete/not_image.jpg",
                         0, save_name, 0))
            con.commit()
        else:
            self.show_information()  # показываем ошибку, если слово есть в словаре пользователя
        con.close()
        self.filling_my_dict()
        self.line_word.setText("")
        self.line_translation.setText("")

    """выход в главное меню"""
    def exit_to_main_menu(self):
        self.hide()
        self.first_window = menu.Menu()
        self.first_window.show()

    """открытие окна с выбором какие рандомные слова будем добавлять"""
    def chose_words(self):
        self.hide()
        self.choose_words = ChooseWords()
        self.choose_words.show()

    """открытие окна добавления рандомных слов"""
    def add_words(self, name_words, quantity):
        try:
            self.add_words_window = AddRandomWords(quantity, name_words)
            self.add_words_window.show()
        except RunOutWords:
            self.hide()

    """заполнение словаря пользователя"""
    def filling_my_dict(self):
        self.tableWidget.setRowCount(0)
        self.tableWidget.setColumnCount(3)
        self.tableWidget.setHorizontalHeaderLabels(["слово", "перевод", "check"])
        self.tableWidget.horizontalHeader().setDefaultSectionSize(255)
        self.tableWidget.setColumnWidth(2, 50)
        self.tableWidget.horizontalHeader().setSectionResizeMode(2, QtWidgets.QHeaderView.Fixed)

        # Подключение к БД
        con = sqlite3.connect("bd_dict.db")
        cur = con.cursor()

        # получение всех слов из таблицы MyDict
        self.eng_words = cur.execute("""SELECT eng_word FROM MyDict""").fetchall()
        self.rus_words = list()
        for eng_word in self.eng_words:
            self.rus_words.append(cur.execute("""SELECT rus_word FROM MyDict WHERE eng_word = ?""",
                                              (eng_word[0],)).fetchall()[0])

        #  заполнение таблицы
        for i in range(len(self.eng_words)):
            self.tableWidget.setRowCount(self.tableWidget.rowCount() + 1)  # добавление строки
            self.tableWidget.setItem(i, 0, QTableWidgetItem(self.rus_words[i][0]))  # добавление русского слова
            self.tableWidget.setItem(i, 1, QTableWidgetItem(self.eng_words[i][0]))  # добавление английского слова
            self.tableWidget.setCellWidget(i, 2, QCheckBox(self))  # добавление QCheckBox

    """очистка всего словаря"""
    def delete_all(self):
        # Подключение к БД
        con = sqlite3.connect("bd_dict.db")
        cur = con.cursor()
        for i in range(self.tableWidget.rowCount()):
            cur.execute("""UPDATE DictAll SET add_my_dict = ? WHERE rus_word = ?""",
                        (0, self.tableWidget.item(i, 0).text()))  # изменяем 0 на 1,
            cur.execute("""UPDATE DictNouns SET add_my_dict = ? WHERE rus_word = ?""",
                        (0, self.tableWidget.item(i, 0).text()))  # изменяем 0 на 1,
            cur.execute("""UPDATE DictVerbs SET add_my_dict = ? WHERE rus_word = ?""",
                        (0, self.tableWidget.item(i, 0).text()))  # изменяем 0 на 1,
            cur.execute("""UPDATE DictAdjectives SET add_my_dict = ? WHERE rus_word = ?""",
                        (0, self.tableWidget.item(i, 0).text()))  # изменяем 0 на 1,
            # потому что слово удалено из словарь пользователя
        cur.execute("""DELETE FROM MyDict""")  # очистка словаря (таблицы в БД)
        con.commit()
        con.close()

        self.tableWidget.clear()  # очистка словаря (таблицы)
        self.tableWidget.setRowCount(0)
        self.tableWidget.setHorizontalHeaderLabels(["слово", "перевод", "check"])

    """выборочное удаление слов"""
    def delete_choose(self):
        # Подключение к БД
        con = sqlite3.connect("bd_dict.db")
        cur = con.cursor()
        for i in range(self.tableWidget.rowCount()):
            if self.tableWidget.cellWidget(i, 2).isChecked():  # проверка, отмечено ли слово
                # удаляем слово из словаря пользователя (таблицы в БД)
                cur.execute("""DELETE FROM MyDict where rus_word = ?""",
                            (self.tableWidget.item(i, 0).text(),))
                # изменяем 0 на 1, потому что слово удалено из словаря
                # изменяем везде, потому что слово могло быть в нескольких словарях и мы не знаем в каких
                cur.execute("""UPDATE DictAll SET add_my_dict = ? WHERE rus_word = ?""",
                            (0, self.tableWidget.item(i, 0).text()))
                cur.execute("""UPDATE DictNouns SET add_my_dict = ? WHERE rus_word = ?""",
                            (0, self.tableWidget.item(i, 0).text()))
                cur.execute("""UPDATE DictVerbs SET add_my_dict = ? WHERE rus_word = ?""",
                            (0, self.tableWidget.item(i, 0).text()))
                cur.execute("""UPDATE DictAdjectives SET add_my_dict = ? WHERE rus_word = ?""",
                            (0, self.tableWidget.item(i, 0).text()))
                con.commit()
        con.close()
        self.filling_my_dict()

    def studying(self):
        self.list_eng = list()
        self.list_rus = list()
        self.list_images = list()

        if self.radioBut_russian.isChecked():
            self.language_first_word = "ru"
            try:
                self.open_window_studying()  # открытие окна заучивания слов
            except RunOutWords:
                self.show()
        elif self.radioBut_english.isChecked():
            self.language_first_word = "en"
            try:
                self.open_window_studying()  # открытие окна заучивания слов
            except RunOutWords:
                pass
        else:
            self.show_error_unselected()

    """открытие окна заучивания слов"""
    def open_window_studying(self):
        self.studying_window = StudyingWords(self.language_first_word)
        self.studying_window.show()
        self.hide()

    """вывод окна с ошибкой, если пользователь не написал слово"""
    def show_error_empty_fields(self):
        self.error = QMessageBox()
        self.error.setWindowTitle("Ошибка")
        self.error.setText("Заполните поля!!!")
        self.error.setIcon(QMessageBox.Information)
        self.error.exec_()

    """вывод окна с информацией, что слово, которое хотел добавить пользователь уже есть в словаре"""
    def show_information(self):
        self.error = QMessageBox()
        self.error.setWindowTitle(" ")
        self.error.setText("Такое слово уже есть в словаре")
        self.error.setIcon(QMessageBox.Information)
        self.error.exec_()

    """вывод окна с ошибкой, если пользователь не выбрал на каком языке будет первое слово в момент заучивания"""
    def show_error_unselected(self):
        self.error = QMessageBox()
        self.error.setWindowTitle("Ошибка")
        self.error.setText("Выберете язык для первого слова!!!")
        self.error.setIcon(QMessageBox.Information)
        self.error.exec_()

    """вывод окна с ошибкой, если перевод не удалось выполнить"""
    def error_translation_dont_work(self):
        self.error = QMessageBox()
        self.error.setWindowTitle("Ошибка")
        self.error.setText("Не удалось выполнить перевод")
        self.error.setIcon(QMessageBox.Information)
        self.error.exec_()

    """вывод окна с ошибкой, если пользователь не отметил язык своего слова"""
    def show_error_unselected_language(self):
        self.error = QMessageBox()
        self.error.setWindowTitle("Ошибка")
        self.error.setText("Выберете язык!!!")
        self.error.setIcon(QMessageBox.Information)
        self.error.exec_()

    """если закрывать окно нажатием на крестик в углу))"""
    def closeEvent(self, event):
        self.hide()
        self.menu_window = menu.Menu()
        self.menu_window.show()



"""добавление в словарь рандомных слов"""
class AddRandomWords(QWidget):
    def __init__(self, quantity, name_words):
        self.quantity = quantity
        self.name_words = name_words
        super().__init__()
        self.initUI()

    def initUI(self):
        uic.loadUi('Ui/add_or_not_word.ui', self)
        self.setWindowTitle("enWords")
        self.move(605, 250)
        self.setFixedSize(700, 500)

        # определение словаря
        if self.name_words == "любые":
            self.dict = "DictAll"
        elif self.name_words == "существительные":
            self.dict = "DictNouns"
        elif self.name_words == "глаголы":
            self.dict = "DictVerbs"
        else:
            self.dict = "DictAdjectives"

        # Подключение к БД
        self.con = sqlite3.connect("bd_dict.db")
        self.cur = self.con.cursor()

        # получение из таблиц слов, озвучек и картинок, которых нет в словаре пользователя
        # и которые он не отвечал правильно
        self.eng_words = [word[0] for word in self.cur.execute(f"""SELECT eng_word FROM {self.dict}
         WHERE add_my_dict = 0 and test = 0""").fetchall() if word]
        self.rus_words = [word[0] for word in self.cur.execute(f"""SELECT rus_word FROM {self.dict}
         WHERE add_my_dict = 0 and test = 0""").fetchall() if word]
        self.images = [image[0] for image in self.cur.execute(f"""SELECT image FROM {self.dict}
         WHERE add_my_dict = 0 and test = 0""").fetchall() if image]
        self.sounds = [sound[0] for sound in self.cur.execute(f"""SELECT sound FROM {self.dict}
         WHERE add_my_dict = 0 and test = 0""").fetchall() if sound]

        self.index = -1  # под этим индексом будут выводиться следующие картинки со словами
        self.count = 0  # отсчитывает сколько слов уже вывелось

        self.next_word()
        self.but_add.clicked.connect(self.add_my_dict)
        self.but_dont_add.clicked.connect(self.next_word)

    """обновление окна с добавлением рандомных слов"""
    def show_words_image(self):
        self.pixmap = QPixmap(QImage(self.images[self.index]))
        self.label_photo.setPixmap(self.pixmap)  # добавление первой картинки

        self.label_eng_word.setText(self.eng_words[self.index])  # добавление первого слова с переводом
        self.label_rus_word.setText(self.rus_words[self.index])
        self.count += 1

    def next_word(self):
        if self.count == self.quantity:  # проверка, было ли это последнее слово, если да, то выход
            self.exit_to_my_dict()
        elif len(self.eng_words) == 0:
            self.show_error_empty_dict()
            raise RunOutWords
        elif self.index == len(self.eng_words) - 1:  # проверка, закончились лт слова в словаре DictAll
            self.show_error_empty_dict()
            self.exit_to_my_dict()
        else:
            self.index += 1
            self.show_words_image()

    """добавление слова в словарь пользователя"""
    def add_my_dict(self):
        # добавляем слово в словарь пользователя
        if [] == self.cur.execute("""SELECT eng_word FROM MyDict
         WHERE rus_word = ?""", (self.rus_words[self.index],)).fetchall():
            self.cur.execute("""INSERT INTO MyDict VALUES(?, ?, ?, ?, ?, ?)""",
                        (self.eng_words[self.index], self.rus_words[self.index],
                         self.images[self.index], 0, self.sounds[self.index], 0))

            self.cur.execute(f"""UPDATE DictAll SET add_my_dict = ? WHERE rus_word = ?""",
                        (1, self.rus_words[self.index]))  # изменяем 0 на 1, потому что слово добавлено в словарь
            self.cur.execute(f"""UPDATE DictNouns SET add_my_dict = ? WHERE rus_word = ?""",
                        (1, self.rus_words[self.index]))  # изменяем 0 на 1, потому что слово добавлено в словарь
            self.cur.execute(f"""UPDATE DICTVerbs SET add_my_dict = ? WHERE rus_word = ?""",
                        (1, self.rus_words[self.index]))  # изменяем 0 на 1, потому что слово добавлено в словарь
            self.cur.execute(f"""UPDATE DictAdjectives SET add_my_dict = ? WHERE rus_word = ?""",
                        (1, self.rus_words[self.index]))  # изменяем 0 на 1, потому что слово добавлено в словарь
            # изменили во всех словарях, потому что слово могло быть в нескольких и мы не знаем в каких, так что так
        self.con.commit()
        self.next_word()

    """вывод окна с ошибкой, если закончились слова в словаре DictAll"""
    def show_error_empty_dict(self):
        self.error = QMessageBox()
        self.error.setWindowTitle("слова закончились")
        self.error.setText("К сожалению словарь с рандомными словами закончился, но скоро мы обновим его,"
                           " и вы сможете пополнить свой словарь!!!")
        self.error.setIcon(QMessageBox.Information)
        self.error.exec_()

    """выход в главное окно словаря пользователя"""
    def exit_to_my_dict(self):
        self.hide()
        self.my_dict_window = MyDict()
        self.my_dict_window.show()

    """если закрывать окно нажатием на крестик в углу))"""
    def closeEvent(self, event):
        self.hide()
        self.my_dict_window = MyDict()
        self.my_dict_window.show()


class StudyingWords(QWidget):
    def __init__(self, language):
        super().__init__()
        self.language = language
        self.initUI()

    def initUI(self):
        uic.loadUi('Ui/studying.ui', self)
        self.setWindowTitle("enWords")
        self.move(605, 250)
        self.setFixedSize(700, 500)

        # Подключение к БД
        self.con = sqlite3.connect("bd_dict.db")
        self.cur = self.con.cursor()

        # помещаем невыученные слова, их озвучки и картинки в списки
        self.eng_words = [word[0] for word in self.cur.execute(f"""SELECT eng_word FROM MyDict
         WHERE studied_not_studied = 0""").fetchall() if word]
        self.rus_words = [word[0] for word in self.cur.execute(f"""SELECT rus_word FROM MyDict
         WHERE studied_not_studied = 0""").fetchall() if word]
        self.images = [image[0] for image in self.cur.execute(f"""SELECT image FROM MyDict
         WHERE studied_not_studied = 0""").fetchall() if image]
        self.sounds = [sound[0] for sound in self.cur.execute(f"""SELECT sound FROM MyDict
         WHERE studied_not_studied = 0""").fetchall() if sound]

        self.player = QtMultimedia.QMediaPlayer()
        self.count = 0  # cчетчик, сколько слов выучено
        self.show_word_image()
        self.but_word_translation.clicked.connect(self.coup_word)
        self.but_know.clicked.connect(self.word_studied)
        self.but_repeat.clicked.connect(self.next_word)
        self.but_start_sound.clicked.connect(self.player.play)

    """загрузка озвучки слова"""
    def load_mp3(self, filename):
        media = QtCore.QUrl.fromLocalFile(filename)
        content = QtMultimedia.QMediaContent(media)
        self.player.setMedia(content)

    """когда пользователь нажимает на кнопку, показывается перевод слова"""
    def coup_word(self):
        if self.language == "ru":
            self.but_word_translation.setText(self.show_eng_word)
            self.language = "en"
        else:
            self.but_word_translation.setText(self.show_rus_word)
            self.language = "ru"

    """показ слов и картинок"""
    def show_word_image(self):
        # проверка, выучил ли пользователь все слова из словаря, если да, то показывается окно с информацией
        if len(self.eng_words) == 0 and self.count != 0:
            self.show_error_all_studied()
            self.open_my_dict()
        elif self.eng_words:
            self.show_eng_word = self.eng_words[0]
            self.show_rus_word = self.rus_words[0]
            self.show_image = self.images[0]
            self.sound = self.sounds[0]

            self.load_mp3(self.sound)  # добавление звука
            self.pixmap = QPixmap(QImage(self.show_image))
            self.label_photo.setPixmap(self.pixmap)  # добавление картинки
            if self.language == "ru":
                self.but_word_translation.setText(self.show_rus_word)  # добавление слова
            else:
                self.but_word_translation.setText(self.show_eng_word)  # добавление слова
        else:
            self.show_error_all_studied()
            raise RunOutWords

    """если пользователь еще хочет повторить слово, то перемещаем его в конец списка заучиваемых слов"""
    def next_word(self):
        self.eng_words.append(self.show_eng_word)
        self.rus_words.append(self.show_rus_word)
        self.images.append(self.show_image)
        self.sounds.append(self.sound)
        self.eng_words.pop(0)
        self.rus_words.pop(0)
        self.images.pop(0)
        self.sounds.pop(0)

        self.show_word_image()

    """если пользователь выучил слово, то удаляем его из списка заучиваемых слов"""
    def word_studied(self):
        self.count += 1
        self.cur.execute("""UPDATE MyDict SET studied_not_studied = ? WHERE eng_word = ?""", (1, self.show_eng_word))
        self.con.commit()
        self.eng_words.pop(0)
        self.rus_words.pop(0)
        self.images.pop(0)
        self.sounds.pop(0)
        self.con.commit()
        self.show_word_image()

    """если закрывать окно нажатием на крестик в углу))"""
    def closeEvent(self, event):
        self.hide()
        self.my_dict_window = MyDict()
        self.my_dict_window.show()

    def open_my_dict(self):
        self.hide()
        self.my_dict_window = MyDict()
        self.my_dict_window.show()

    """вывод окна с информацией, если пользователь выучил все слова слова"""
    def show_error_all_studied(self):
        self.error = QMessageBox()
        self.error.setText("Вы выучили все слова из своего словаря")
        self.error.setIcon(QMessageBox.Information)
        self.error.exec_()


"""выбор словаря, из которого будем добавлять рандомные слова"""
class ChooseWords(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi('Ui/choose_words.ui', self)
        self.setWindowTitle("enWords")
        self.move(605, 250)
        self.setFixedSize(700, 420)

        self.but_random_all.clicked.connect(self.start_choose)
        self.but_random_nouns.clicked.connect(self.start_choose)
        self.but_random_verbs.clicked.connect(self.start_choose)
        self.but_random_adjectives.clicked.connect(self.start_choose)

    """пользователь выбирает сколько слов добавлять"""
    def start_choose(self):
        name_words = self.sender().text()
        quantity, ok_pressed = QInputDialog.getInt(
            self, " ", "Сколько слов добавить?",
            10, 1, 20, 1)
        if ok_pressed:
            self.hide()
            MyDict.add_words(self, name_words, quantity)

    """если закрывать окно нажатием на крестик в углу))"""
    def closeEvent(self, event):
        self.hide()
        self.my_dict_window = MyDict()
        self.my_dict_window.show()






