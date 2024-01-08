import sys
import my_dict
import test


from my_dict import *
from test import *
from PyQt5 import uic
from PyQt5.QtWidgets import QWidget, QApplication


"""главное окно"""
class Menu(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        uic.loadUi('Ui/menu.ui', self)
        self.setWindowTitle("enWords")
        self.move(605, 250)
        self.setFixedSize(700, 500)

        self.but_my_dict.clicked.connect(self.open_my_dict)
        self.but_test.clicked.connect(self.choose_test)
        self.but_my_progress.clicked.connect(self.open_my_progress)

    """открытие словаря пользователя"""
    def open_my_dict(self):
        self.my_dict_window = my_dict.MyDict()
        self.my_dict_window.show()
        self.hide()

    """открытие окна с выбором теста"""
    def choose_test(self):
        self.test_window = test.ChoseTest()
        self.test_window.show()
        self.hide()

    """открытие прогресса пользователя"""
    def open_my_progress(self):
        self.progress_window = MyProgress()
        self.progress_window.show()
        self.hide()


class MyProgress(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        uic.loadUi('Ui/my_progress.ui', self)
        self.setWindowTitle("enWords")
        self.move(670, 240)
        self.setFixedSize(550, 600)

        # Подключение к БД
        con = sqlite3.connect("bd_dict.db")
        cur = con.cursor()
        # тут и далее получаем кол-во всех слов и слов, которые пользователь ответил верно, из словаря
        # затем помещает в label, это будет прогресс пользователя, сколько слов он верно ответил из все слов словаря
        all_words_in_dict = cur.execute(f"""SELECT rus_word FROM MyDict""").fetchall()
        correct_words = cur.execute(f"""SELECT rus_word FROM MyDict WHERE test = 1""").fetchall()
        self.label_my_dict.setText(f"{len(correct_words)}/{len(all_words_in_dict)}")

        all_words_in_dict = cur.execute(f"""SELECT rus_word FROM DictVerbs""").fetchall()
        correct_words = cur.execute(f"""SELECT rus_word FROM DictVerbs WHERE test = 1""").fetchall()
        self.label_verbs.setText(f"{len(correct_words)}/{len(all_words_in_dict)}")

        all_words_in_dict = cur.execute(f"""SELECT rus_word FROM DictNouns""").fetchall()
        correct_words = cur.execute(f"""SELECT rus_word FROM DictNouns WHERE test = 1""").fetchall()
        self.label_nouns.setText(f"{len(correct_words)}/{len(all_words_in_dict)}")

        all_words_in_dict = cur.execute(f"""SELECT rus_word FROM DictAdjectives""").fetchall()
        correct_words = cur.execute(f"""SELECT rus_word FROM DictAdjectives WHERE test = 1""").fetchall()
        self.label_adjectives.setText(f"{len(correct_words)}/{len(all_words_in_dict)}")

        all_words_in_dict = cur.execute(f"""SELECT rus_word FROM DictAll""").fetchall()
        correct_words = cur.execute(f"""SELECT rus_word FROM DictAll WHERE test = 1""").fetchall()
        self.label_all.setText(f"{len(correct_words)}/{len(all_words_in_dict)}")

        self.but_to_menu.clicked.connect(self.open_menu)

    """выход в меню"""
    def open_menu(self):
        self.hide()
        self.menu_window = menu.Menu()
        self.menu_window.show()

    """если закрывать окно нажатием на крестик в углу))"""
    def closeEvent(self, event):
        self.hide()
        self.menu_window = Menu()
        self.menu_window.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Menu()
    ex.show()
    sys.exit(app.exec_())


