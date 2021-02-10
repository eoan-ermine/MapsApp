import os

from PyQt5 import QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMainWindow, qApp, QVBoxLayout

import requests
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QLineEdit


SCREEN_SIZE = [600, 500]


class MapsApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.map_file = "map.png"
        self.pixmap = QPixmap()
        self.image = QLabel(self)

        self.coord = ["37.530887", "55.70311"]
        self.scale = 1.0

        self.point = ""

        self.get_image()
        self.init_ui()
        self.change_image()

    def get_image(self):
        map_request = f"http://static-maps.yandex.ru/1.x/?ll={','.join(self.coord)}&spn=0.002,0.002&" \
                      f"scale={self.scale}&l=map&pt={self.point}"
        self.response = requests.get(map_request)

        if not self.response:
            print("Ошибка выполнения запроса:")
            print(map_request)
            print("Http статус:", self.response.status_code, "(", self.response.reason, ")")
            qApp.exit(1)
        with open(self.map_file, "wb") as file:
            file.write(self.response.content)

    def init_ui(self):
        main_layout = QVBoxLayout()

        self.setGeometry(100, 100, *SCREEN_SIZE)
        self.image.resize(600, 450)

        self.btn = QPushButton('Принять', self)
        self.btn.setFocusPolicy(Qt.NoFocus)

        self.btn.resize(100, 25)
        self.btn.move(500, 462)
        self.btn.clicked.connect(self.place_find)

        self.text = QLineEdit(self)
        self.text.setFocusPolicy(Qt.ClickFocus)

        self.text.resize(350, 25)
        self.text.move(0, 462)

        main_layout.addWidget(self.image)
        main_layout.addWidget(self.btn)

        self.setLayout(main_layout)
        self.setWindowTitle('Maps App')
        self.show()

    def change_image(self):
        self.pixmap.load(self.map_file)
        self.image.setPixmap(self.pixmap)

    def closeEvent(self, event):
        os.remove(self.map_file)

    def keyPressEvent(self, event):
        key = event.key()
        if key == Qt.Key_Left:
            self.coord[0] = str(float(self.coord[0]) - 0.001)
        elif key == Qt.Key_Right:
            self.coord[0] = str(float(self.coord[0]) + 0.001)
        if key == Qt.Key_Up:
            self.coord[1] = str(float(self.coord[1]) + 0.001)
        elif key == Qt.Key_Down:
            self.coord[1] = str(float(self.coord[1]) - 0.001)
        elif key == Qt.Key_PageUp:
            if self.scale < 4:
                self.scale += 0.1
        elif key == Qt.Key_PageDown:
            if self.scale > 1:
                self.scale -= 0.1

        self.get_image()
        self.change_image()

    def place_find(self):
        self.image.setFocus()

        toponym_to_find = self.text.text()
        geocoder_api_server = "http://geocode-maps.yandex.ru/1.x/"
        geocoder_params = {
            "apikey": "40d1649f-0493-4b70-98ba-98533de7710b",
            "geocode": toponym_to_find,
            "format": "json"}
        response = requests.get(geocoder_api_server, params=geocoder_params)
        json_response = response.json()
        toponym = json_response["response"]["GeoObjectCollection"][
            "featureMember"][0]["GeoObject"]
        toponym_coodrinates = toponym["Point"]["pos"]

        self.coord = toponym_coodrinates.split()
        self.scale = 1.0
        self.point = toponym_coodrinates.replace(' ', ',')
        self.get_image()
        self.change_image()
