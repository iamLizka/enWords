import sqlite3
import menu


from PyQt5 import uic
from menu import *
from PyQt5.QtWidgets import QWidget, QMessageBox
from PyQt5.QtGui import QPixmap, QImage


"""выбор теста"""
class ChoseTest(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        uic.loadUi('Ui/chose_test.ui', self)
        self.setWindowTitle("enWords")
        self.move(605, 250)
        self.setFixedSize(700, 500)
        self.choose_languages.addItems(["Русский", "Английский"])  # варианты языков, на котором будет первое слово
        self.quantity_words.setValue(10)  # стартовое кол-во слов в тесте
        self.name_test = ""

        self.but_of_dict.clicked.connect(self.what_test)
        self.but_nouns.clicked.connect(self.what_test)
        self.but_all.clicked.connect(self.what_test)
        self.but_adjectives.clicked.connect(self.what_test)
        self.but_verbs.clicked.connect(self.what_test)
        self.but_start_test.clicked.connect(self.start_test)
        self.but_to_menu.clicked.connect(self.open_menu)

    """определение по какой категории слов будет тест"""
    def what_test(self):
        self.name_test = self.sender().text()

    """проверки перед запуском теста"""
    def start_test(self):
        if self.name_test != "":  # проверка, выбран ли тест
            # тут мы получаем название словаря, кол-во слов в тесте,
            # язык первого слова, списки с англ., рус. словами, пути к картинкам
            data = self.what_dict()
            # проверка, что пользователь выбрал количество слов меньше или столько же, сколько и есть в словаре
            if len(data[0]) >= int(self.quantity_words.text()):
                # передаем в класс Test кол-во слов в тесте,
                # язык первого слова, списки с англ., рус. словами, пути к картинкам, название словаря
                self.test_window = Test(self.quantity_words.text(),
                                        self.choose_languages.currentText(), data)
                self.test_window.show()
                self.hide()
            else:
                self.show_error_too_many_words()  # ошибка, выбранное кол-во слов больше, чем есть в словаре
        else:
            self.show_error_test_not_selected()  # ошибка, тест не выбран

    """определяение название теблицы в бд и получние данных из нее"""
    def what_dict(self):
        # Подключение к БД
        self.con = sqlite3.connect("bd_dict.db")
        self.cur = self.con.cursor()

        # определение словаря
        if self.name_test == "любым":
            name_dict = "DictAll"
        elif self.name_test == "существительным":
            name_dict = "DictNouns"
        elif self.name_test == "глаголам":
            name_dict = "DictVerbs"
        elif self.name_test == "из словаря":
            name_dict = "MyDict"
        else:
            name_dict = "DictAdjectives"

        # помещаем слова и картинки в списки
        eng_words = [word[0] for word in self.cur.execute(f"""SELECT eng_word FROM {name_dict}
         WHERE test = 0""").fetchall() if word]
        rus_words = [word[0] for word in self.cur.execute(f"""SELECT rus_word FROM {name_dict}
         WHERE test = 0""").fetchall() if word]
        images = [image[0] for image in self.cur.execute(f"""SELECT image FROM {name_dict}
         WHERE test = 0""").fetchall() if image]

        return eng_words, rus_words, images, name_dict

    """вывод окна с ошибкой, если пользователь не выбрал тест"""
    def show_error_test_not_selected(self):
        self.error = QMessageBox()
        self.error.setWindowTitle(" ")
        self.error.setText("Выберете тест!!!")
        self.error.setIcon(QMessageBox.Information)
        self.error.exec_()

    """вывод окна с ошибкой, если пользователь выбрал количество слов большее, чем есть в словаре"""
    def show_error_too_many_words(self):
        self.error = QMessageBox()
        self.error.setWindowTitle(" ")
        self.error.setText("В словаре нет столько слов")
        self.error.setIcon(QMessageBox.Information)
        self.error.exec_()

    """выход в меню"""
    def open_menu(self):
        self.hide()
        self.menu_window = menu.Menu()
        self.menu_window.show()

    """если закрывать окно нажатием на крестик в углу))"""
    def closeEvent(self, event):
        self.hide()
        self.menu_window = menu.Menu()
        self.menu_window.show()


"""Тест"""
class Test(QWidget):
    def __init__(self, quantity_words, language,  data):
        super().__init__()
        self.language = language
        self.quantity_words = quantity_words
        self.eng_words, self.rus_words, self.images, self.name_dict = data
        self.initUI()

    def initUI(self):
        uic.loadUi('Ui/test.ui', self)
        self.setWindowTitle("enWords")
        self.move(605, 250)
        self.setFixedSize(700, 500)
        self.count_wrong = 0  # счетчик правильно отвеченных слов
        self.count_correct = 0  # счетчик неправильно отвеченных слов
        self.index = 0  # под этим индексом будем брать элементы из списков
        self.show_word_image()
        self.but_next_word.clicked.connect(self.next_word)

    """переход к следующему по списку слову"""
    def next_word(self):
        if self.result_by_word():  # если пользователь правильно записал слово
            # Подключение к БД
            con = sqlite3.connect("bd_dict.db")
            cur = con.cursor()
            # отмечаем во все таблицах(словарях), что пользовватель правильно ответил слово,
            # потому что слово могло быть в нескольких и мы не знаем в каких
            # больше оно ему в тесте не попадется
            cur.execute(f"""UPDATE MyDict SET test = ? WHERE eng_word = ?""",
                             (1, self.eng_words[self.index]))
            cur.execute(f"""UPDATE DictAll SET test = ? WHERE eng_word = ?""",
                             (1, self.eng_words[self.index]))
            cur.execute(f"""UPDATE DictNouns SET test = ? WHERE eng_word = ?""",
                             (1, self.eng_words[self.index]))
            cur.execute(f"""UPDATE DictVerbs SET test = ? WHERE eng_word = ?""",
                             (1, self.eng_words[self.index]))
            cur.execute(f"""UPDATE DictAdjectives SET test = ? WHERE eng_word = ?""",
                             (1, self.eng_words[self.index]))
            # удаляем слово из словаря пользователя (таблицы в БД)
            cur.execute("""DELETE FROM MyDict where rus_word = ?""", (self.eng_words[self.index],))
            con.commit()
            self.correct_word()
        else:  # если неправильно
            self.wrong_word()
        self.index += 1
        self.line_second_word.setText("")
        self.show_word_image()

    """определение правильно ли пользователь ответил"""
    def result_by_word(self):
        if self.language == "Русский":
            self.true_word = self.eng_words[self.index]  # правильный ответ
            # проверка, совпадает ли введенное слово с правильным переводом слова
            if self.eng_words[self.index].lower() == self.line_second_word.text().lower():
                self.count_correct += 1
                return True
        else:
            self.true_word = self.rus_words[self.index]  # правильный ответ
            # проверка, совпадает ли введенное слово с правильным переводом слова
            if self.rus_words[self.index].lower() == self.line_second_word.text().lower():
                self.count_correct += 1
                return True
        self.count_wrong += 1
        return False

    """вывод сообщения, если пользователь правильно ответил"""
    def correct_word(self):
        self.result = QMessageBox()
        self.result.setWindowTitle("Верно")
        self.result.setText("   Молодец!!!  \n  Все верно")
        self.result.setIconPixmap(QPixmap("not_delete/good_work.png").scaled(100, 100))
        self.result.setStyleSheet("""
            QMessageBox {
                background: #77d496;
                font: 12pt "Yu Gothic UI Semilight";
            }         
            """)
        self.result.exec_()

    """вывод сообщения, если пользователь неправильно ответил"""
    def wrong_word(self):
        self.result = QMessageBox()
        self.result.setWindowTitle("Ошибка")
        self.result.setText(f"правильный вариант:\n{self.true_word}")
        self.result.setIconPixmap(QPixmap("not_delete/bad_work.png").scaled(100, 100))
        self.result.setStyleSheet("""
            QMessageBox {
                background: #ff5349;
                font: 12pt "Yu Gothic UI Semilight";
            }         
            """)
        self.result.exec_()

    """вывод слов и картинок"""
    def show_word_image(self):
        if self.index == int(self.quantity_words):  # проверка, последнее ли это слово, если да, то выводим результат
            self.hide()
            # передаем в TestResult кол-во всех слов, кол-во правильно и неправильно отвеченных слов
            self.your_result = TestResult(self.quantity_words, self.count_correct, self.count_wrong)
            self.your_result.show()
        else:
            self.pixmap = QPixmap(QImage(self.images[self.index]))
            self.label_photo.setPixmap(self.pixmap)  # добавление картинки
            self.label_count.setText(f"{self.index + 1}/{self.quantity_words}")  # какое слово выводиться из всех слов
            if self.language == "Русский":
                self.label_first_word.setText(self.rus_words[self.index])  # добавление слова
            else:
                self.label_first_word.setText(self.eng_words[self.index])  # добавление слова

    """если закрывать окно нажатием на крестик в углу))"""
    def closeEvent(self, event):
        self.hide()
        self.menu_window = menu.Menu()
        self.menu_window.show()

    """выход в меню"""
    def open_menu(self):
        self.hide()
        self.menu_window = menu.Menu()
        self.menu_window.show()


"""результат теста"""
class TestResult(QWidget):
    def __init__(self, total_words, count_correct_words, count_wrong_words):
        super().__init__()
        self.total_words = total_words
        self.count_correct_words = count_correct_words
        self.count_wrong_words = count_wrong_words
        self.initUI()

    def initUI(self):
        global count_words, weekday
        uic.loadUi('Ui/result.ui', self)
        self.move(620, 240)
        self.setFixedSize(550, 620)

        # вывод результата
        self.label_total.setText(str(self.total_words))
        self.label_count_correct.setText(str(self.count_correct_words))
        self.label_count_wrong.setText(str(self.count_wrong_words))

        # смотря какой результат, выводим мемчик и надпись
        if self.count_correct_words * 100 // int(self.total_words) >= 60:
            self.pixmap = QPixmap(QImage("memes/well_done.jpg"))
            self.label_grade.setText("Отличный результат!!!")
        elif 25 < self.count_correct_words * 100 // int(self.total_words) < 60:
            self.pixmap = QPixmap(QImage("memes/normal.jpg"))
            self.label_grade.setText("Неплохо, хорошая работа!!!")
        else:
            self.pixmap = QPixmap(QImage("memes/bad.jpg"))
            self.label_grade.setText("В следующий раз будет лучше!")
        self.label_meme.setPixmap(self.pixmap)  # добавление мемчика

        self.but_menu.clicked.connect(self.open_menu)
        self.but_my_progress.clicked.connect(self.my_progress)

    """выход в меню"""
    def open_menu(self):
        self.hide()
        self.menu_window = menu.Menu()
        self.menu_window.show()

    """открытие прогресса пользователя"""
    def my_progress(self):
        self.hide()
        self.progress_window = menu.MyProgress()
        self.progress_window.show()

    """если закрывать окно нажатием на крестик в углу))"""
    def closeEvent(self, event):
        self.hide()
        self.menu_window = menu.Menu()
        self.menu_window.show()




