import sys
from PySide6 import QtWidgets
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QToolBar, QVBoxLayout
from src.disc.widget import FreeSpaceDiscWidget, AllDiscTable, DiscStatistic
import tkinter


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        """Инициализация главного окна"""
        super().__init__()
        self.setWindowTitle("My Awesome App")
        self.layout = QVBoxLayout()
        toolbar = QToolBar("My main toolbar")
        self.addToolBar(toolbar)

        self.free_disc_space_action = QAction("Свободное место на диске", self)
        self.disc_health_action = QAction("SMART", self)

        self.disc_health_action.triggered.connect(self.disc_health_info_button)
        self.disc_health_action.setCheckable(True)

        self.free_disc_space_action.triggered.connect(self.free_disc_space_button)
        self.free_disc_space_action.setCheckable(True)

        toolbar.addAction(self.free_disc_space_action)
        toolbar.addAction(self.disc_health_action)
        self.table = AllDiscTable()
        self.setCentralWidget(self.table)

    def free_disc_space_button(self):
        """Вызов виджета расчета свободного места на диске"""
        disc_widget = FreeSpaceDiscWidget()
        if self.disc_health_action.isChecked() is True and self.free_disc_space_action.isChecked() is True:
            self.centralWidget().deleteLater()
            self.disc_health_action.toggle()
            self.setCentralWidget(disc_widget)
        elif self.free_disc_space_action.isChecked() is True:
            self.centralWidget().deleteLater()
            self.setCentralWidget(disc_widget)
        else:
            self.centralWidget().deleteLater()
            table = AllDiscTable()
            self.setCentralWidget(table)

    def disc_health_info_button(self):
        """Виджет расчета цикла чтения/записи диска"""
        widget = DiscStatistic()
        if self.free_disc_space_action.isChecked() is True and self.disc_health_action.isChecked() is True:
            self.centralWidget().deleteLater()
            self.free_disc_space_action.toggle()
            self.setCentralWidget(widget)
        elif self.disc_health_action.isChecked() is True:
            self.centralWidget().deleteLater()
            self.setCentralWidget(widget)
        else:
            self.centralWidget().deleteLater()
            table = AllDiscTable()
            self.setCentralWidget(table)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    app.setStyle('Windows')
    resolution = tkinter.Tk()
    width = resolution.winfo_screenwidth() - 70
    height = resolution.winfo_screenheight()
    window.resize(width, height)
    window.show()
    sys.exit(app.exec())


