# week 2
import sys
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QPushButton,
    QToolTip
)
from PyQt6.QtGui import (
    QIcon
)
from PyQt6.QtCore import (
    QCoreApplication
)


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Minimal PyQT6 Window")
        self.resize(400, 300)

        self.setWindowIcon(QIcon("icon.png"))

        btn = QPushButton("Exit", self)
        btn.clicked.connect(QCoreApplication.instance().quit)
        btn.setToolTip("Exit the application.")


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())
