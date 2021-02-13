import os

from PyQt5 import QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMainWindow, qApp, QVBoxLayout, QHBoxLayout

import requests
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QCheckBox, QWidget, QLabel, QPushButton, QLineEdit

SCREEN_SIZE = [600, 450]


class MapsApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.map_file = "map.png"
        self.pixmap = QPixmap()
        self.image = QLabel()

        self.coord = ["37.530887", "55.70311"]
        self.scale = 1.0

        self.point = ""
        self.layer = "map"

        self.show_postal = False
        self.toponym = None

        self.get_image()
        self.init_ui()
        self.change_image()

    def get_image(self):
        map_request = f"http://static-maps.yandex.ru/1.x/?ll={','.join(self.coord)}&spn=0.002,0.002&" \
                      f"scale={self.scale}&l={self.layer}&pt={self.point}"
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

        self.image.resize(600, 450)

        main_layout = QVBoxLayout()

        # Search layout

        search_layout = QHBoxLayout()

        search_btn = QPushButton('Принять')
        search_btn.setFocusPolicy(Qt.NoFocus)
        search_btn.clicked.connect(self.place_find)

        self.text = QLineEdit()
        self.text.setFocusPolicy(Qt.ClickFocus)

        flush_btn = QPushButton("Сброс поискового результата")
        flush_btn.setFocusPolicy(Qt.NoFocus)
        flush_btn.clicked.connect(self.flush_result)

        search_layout.addWidget(self.text)
        search_layout.addWidget(search_btn)
        search_layout.addWidget(flush_btn)

        # Select view layout

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

        # Address layout

        address_layout = QHBoxLayout()

        address_layout.addWidget(QLabel("Адрес: "))
        self.address_edit = QLineEdit()
        self.address_edit.setFocusPolicy(Qt.NoFocus)

        show_postal = QCheckBox("Показать почтовый индекс")
        show_postal.stateChanged.connect(self.set_show_postal)

        address_layout.addWidget(self.address_edit)
        address_layout.addWidget(show_postal)

        # Compose it all in main_layout

        main_layout.addLayout(select_view_layout)
        main_layout.addWidget(self.image)
        main_layout.addLayout(search_layout)
        main_layout.addLayout(address_layout)

        main_widget.setLayout(main_layout)
        self.setWindowTitle('Maps App')
        self.show()

    def set_show_postal(self, state):
        self.show_postal = state
        if self.toponym:
            self.update_address_edit(self.toponym)

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

    def update_address_edit(self, toponym):
        address = toponym["metaDataProperty"]["GeocoderMetaData"]["text"]
        postal_code = ": " + toponym["metaDataProperty"]["GeocoderMetaData"]["Address"].get("postal_code", "") \
            if self.show_postal else ""

        self.address_edit.setText(address + postal_code)

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
        self.toponym = json_response["response"]["GeoObjectCollection"][
            "featureMember"][0]["GeoObject"]
        toponym_coodrinates = self.toponym["Point"]["pos"]

        self.coord = toponym_coodrinates.split()
        self.scale = 1.0
        self.point = toponym_coodrinates.replace(' ', ',')

        self.update_address_edit(self.toponym)

        self.get_image()
        self.change_image()

    def flush_result(self):
        self.point = ""
        self.address_edit.clear()
