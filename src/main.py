import sys

from src.gui.maps_app import MapsApp
from PyQt5.QtWidgets import QApplication

if __name__ == "__main__":
    app = QApplication(sys.argv)

    maps_app = MapsApp()
    maps_app.show()

    sys.exit(app.exec_())
