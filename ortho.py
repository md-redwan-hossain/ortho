import sqlite3
import json
from PyQt6 import uic
import sys
import os
import py7zr
import typing as type
from PyQt6 import QtGui
from PyQt6.QtWidgets import (
    QMainWindow,
    QPushButton,
    QLabel,
    QApplication,
    QTextEdit,
    QScrollArea,
)


BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class Main_Ui(QMainWindow):
    UI_FILE = os.path.join(BASE_DIR, "ortho.ui")
    DB_PATH = os.path.join(BASE_DIR, "ortho.db")

    if not os.path.exists(DB_PATH):
        print("Extracting DataBase")
        with py7zr.SevenZipFile("./ortho_db.7z", mode="r") as file:
            file.extractall()
        print("DataBase successfully extracted ")

    DB_CONNECTION: type.Any = ""
    JSON_BN_DB: dict = {}

    def init_db_connection(self):
        self.DB_CONNECTION = sqlite3.connect(self.DB_PATH)

    def init_json_bn_db(self):
        with open("word_db_bangla.json") as json_file:
            self.JSON_BN_DB = json.load(json_file)

    def __init__(self):
        super(Main_Ui, self).__init__()
        # load the Main_Ui
        uic.loadUi(self.UI_FILE, self)
        self.setFixedSize(self.size())

        # load the db
        self.init_db_connection()

        # load the json map for db query
        self.init_json_bn_db()

        # defining widgets
        self.word_search_bar = self.findChild(QTextEdit, "word_search_box")
        self.word_search_btn = self.findChild(QPushButton, "word_search_button")
        self.scrollable = self.findChild(QScrollArea, "scroll_able_area_bn_word")
        self.picture_display_box = self.findChild(QLabel, "bn_word_meaning_box")

        # button click handler
        self.word_search_btn.clicked.connect(self.word_search_button_click_handler)

        # Initially hide the result area
        self.scrollable.hide()
        self.picture_display_box.hide()

    def query_json_bn_db(self, word_search) -> type.Any:
        word_index = self.JSON_BN_DB.get(f"{word_search}")
        return word_index

    def query_db(self, key) -> None:
        cursor: type.Any = self.DB_CONNECTION.cursor()
        cursor.execute(
            f"""SELECT bangla_definition FROM bangla_dictionary WHERE _id = {key};"""
        )
        result = cursor.fetchone()
        image = result[0]
        pixmap = QtGui.QPixmap()
        pixmap.loadFromData(image, "gif")
        pic_width = pixmap.width()
        pic_height = pixmap.height()
        self.picture_display_box.setMinimumSize(pic_width, pic_height)
        self.picture_display_box.setPixmap(pixmap)

    def word_search_button_click_handler(self) -> None:
        word_from_user = str(self.word_search_bar.toPlainText())
        if word_from_user != "":
            word_key = self.query_json_bn_db(word_from_user)
            if word_key:
                self.scrollable.show()
                self.picture_display_box.show()
                self.statusBar().clearMessage()
                self.picture_display_box.clear()
                self.query_db(word_key)
            else:
                self.scrollable.hide()
                self.picture_display_box.hide()
                self.statusBar().showMessage("Word not found.")
                self.statusBar().repaint()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QtGui.QIcon(os.path.join(BASE_DIR, "ortho.svg")))
    window = Main_Ui()
    window.show()
    sys.exit(app.exec())
