import os

from PyQt5 import QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMainWindow, qApp, QVBoxLayout, QHBoxLayout, QPushButton

import requests
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QWidget, QLabel


SCREEN_SIZE = [600, 450]


class MapsApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.map_file = "map.png"
        self.pixmap = QPixmap()
        self.image = QLabel()

        self.coord = ["37.530887", "55.70311"]
        self.scale = 1.0

        self.layer = "map"

        self.get_image()
        self.init_ui()
        self.change_image()

    def get_image(self):
        map_request = f"http://static-maps.yandex.ru/1.x/?ll={','.join(self.coord)}&spn=0.002,0.002&" \
                      f"scale={self.scale}&l={self.layer}"
        response = requests.get(map_request)

        if not response:
            print("Ошибка выполнения запроса:")
            print(map_request)
            print("Http статус:", response.status_code, "(", response.reason, ")")
            qApp.exit(1)
        with open(self.map_file, "wb") as file:
            file.write(response.content)

    def set_layer(self, layer_name):
        self.layer = layer_name
        self.get_image()
        self.change_image()

    def init_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        main_layout = QVBoxLayout()

        select_view_layout = QHBoxLayout()
        select_view_layout.addWidget(QLabel("Выбрать слой: "))

        self.scheme_btn = QPushButton("Схема")
        self.scheme_btn.clicked.connect(lambda e: self.set_layer("map"))
        self.scheme_btn.setFocusPolicy(Qt.NoFocus)

        self.satellite_btn = QPushButton("Спутник")
        self.satellite_btn.clicked.connect(lambda e: self.set_layer("sat"))
        self.satellite_btn.setFocusPolicy(Qt.NoFocus)

        self.hybrid_btn = QPushButton("Гибрид")
        self.hybrid_btn.clicked.connect(lambda e: self.set_layer("sat,skl"))
        self.hybrid_btn.setFocusPolicy(Qt.NoFocus)

        select_view_layout.addWidget(self.scheme_btn)
        select_view_layout.addWidget(self.satellite_btn)
        select_view_layout.addWidget(self.hybrid_btn)

        self.setGeometry(100, 100, *SCREEN_SIZE)
        self.image.resize(600, 450)

        main_layout.addLayout(select_view_layout)
        main_layout.addWidget(self.image)

        main_widget.setLayout(main_layout)
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
