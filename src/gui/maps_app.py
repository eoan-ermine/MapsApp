import os

from PyQt5.QtWidgets import QMainWindow, qApp

import requests
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QWidget, QLabel


SCREEN_SIZE = [600, 450]


class MapsApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Maps App')

        self.map_file = None
        self.pixmap = None
        self.image = None

        self.coord = ["37.530887", "55.70311"]
        self.scale = 1.0

        self.get_image()
        self.init_ui()

    def get_image(self):
        map_request = f"http://static-maps.yandex.ru/1.x/?ll={','.join(self.coord)}&spn=0.002,0.002&" \
                      f"scale={self.scale}&l=map"
        response = requests.get(map_request)

        if not response:
            print("Ошибка выполнения запроса:")
            print(map_request)
            print("Http статус:", response.status_code, "(", response.reason, ")")
            qApp.exit(1)
        self.map_file = "map.png"
        with open(self.map_file, "wb") as file:
            file.write(response.content)

    def init_ui(self):
        self.setGeometry(100, 100, *SCREEN_SIZE)
        self.pixmap = QPixmap(self.map_file)
        self.image = QLabel(self)
        self.image.move(0, 0)
        self.image.resize(600, 450)
        self.image.setPixmap(self.pixmap)

    def closeEvent(self, event):
        os.remove(self.map_file)
