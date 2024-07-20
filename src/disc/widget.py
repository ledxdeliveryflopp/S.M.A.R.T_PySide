import shutil
import subprocess
import psutil
from PySide6 import QtWidgets, QtCore
from PySide6.QtWidgets import QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget
from psutil._common import bytes2human


class AllDiscInfo(QtWidgets.QTableWidget):
    """Виджет информации о всех дисках"""

    def __init__(self):
        super().__init__()
        self.resize(1920, 1080)
        drives = {}
        number = 1
        all_disc = psutil.disk_partitions(all=True)
        for disc in range(len(all_disc)):
            disc_path = all_disc[disc].device
            disc_usage = shutil.disk_usage(disc_path)
            number += 1
            drives.update({f"drive_data{number}": {"drive": disc_path, "usage": disc_usage}})


class FreeSpaceDiscWidget(QtWidgets.QWidget):
    """Виджет расчета свободного места на диске"""

    def __init__(self):
        super().__init__()
        self.button = QtWidgets.QPushButton("Поиск")
        self.text = QtWidgets.QLabel("Введите нужный диск", alignment=QtCore.Qt.AlignCenter)
        self.search = QtWidgets.QLineEdit()
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.addWidget(self.text)
        self.layout.addWidget(self.search)
        self.layout.addWidget(self.button)
        self.button.clicked.connect(self.get_free_disc_memory)

    @QtCore.Slot()
    def get_free_disc_memory(self):
        disc = self.search.text().upper() + ":"
        try:
            disc_free_space = shutil.disk_usage(disc).free
            self.text.setText(
                f"Свободное место на диске - {disc} {disc_free_space // (2 ** 30)} гб")
        except FileNotFoundError:
            self.text.setText("Такого диска нет")


class AllDiscTable(QWidget):

    def __init__(self):
        super().__init__()
        self.bytes_per_gb = 1024 * 1024 * 1024
        self.tableWidget = QTableWidget()
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.tableWidget)
        self.setLayout(self.layout)
        self.all_drives = psutil.disk_partitions()
        self.__construct_table()
        self.__get_all_disc_path()
        self.__get_free_disc_space()
        self.__get_usage_disc_space()
        self.__get_total_disc_space()

    def __get_all_disc_path(self) -> list:
        """Все диски"""
        column_position = 0
        drives = []
        for drive in range(len(self.all_drives)):
            if self.all_drives[drive].opts == "cdrom":
                continue
            drive_path = self.all_drives[drive].device
            self.tableWidget.setItem(0, column_position, QTableWidgetItem(f"{drive_path}"))
            column_position += 1
            drives.append(drive_path)
        return drives

    def __construct_table(self) -> None:
        """Создание колонок и строк"""
        drives = self.__get_all_disc_path()
        self.tableWidget.setRowCount(4)
        self.tableWidget.setColumnCount(len(drives))
        self.tableWidget.setVerticalHeaderLabels(["Диск", "Свободное место", "Использовано",
                                                  "Всего места"])

    def __get_free_disc_space(self) -> None:
        """Свободное место на диске"""
        column_position = 0
        drives = self.__get_all_disc_path()
        for drive in drives:
            drive_free_space_full = shutil.disk_usage(drive)
            free_space = bytes2human(drive_free_space_full.free)
            self.tableWidget.setItem(1, column_position,
                                     QTableWidgetItem(f"{free_space}"))
            column_position += 1

    def __get_usage_disc_space(self) -> None:
        """Использованое место на диске"""
        column_position = 0
        drives = self.__get_all_disc_path()
        for drive in drives:
            drive_free_space_full = shutil.disk_usage(drive)
            full_space = bytes2human(drive_free_space_full.used)
            self.tableWidget.setItem(2, column_position,
                                     QTableWidgetItem(f"{full_space}"))
            column_position += 1

    def __get_total_disc_space(self) -> None:
        """Всего места на диске"""
        column_position = 0
        drives = self.__get_all_disc_path()
        for drive in drives:
            drive_total_space_full = shutil.disk_usage(drive)
            total_space = bytes2human(drive_total_space_full.total)
            self.tableWidget.setItem(3, column_position,
                                     QTableWidgetItem(f"{total_space}"))
            column_position += 1


class DiscStatistic(QWidget):
    def __init__(self):
        super().__init__()
        self.all_drives = psutil.disk_partitions()
        self.drive_code = []
        self.tableWidget = QTableWidget()
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.tableWidget)
        self.setLayout(self.layout)
        self.construct_table()
        self.get_all_disc_path()
        self.get_disc_read_count()

    def construct_table(self) -> None:
        """Создание колонок и строк"""
        self.tableWidget.setRowCount(3)
        smart_command = subprocess.run(["smartctl", "--scan"], capture_output=True, text=True)
        result = smart_command.stdout
        data = result.split('\n')
        for code in data:
            drive = code.split('\n')
            drive = drive[0].split(' ')
            drive = drive[0]
            self.drive_code.append(drive)
        self.drive_code.remove("")
        self.tableWidget.setColumnCount(len(self.drive_code))
        self.tableWidget.setVerticalHeaderLabels(["Название", "Колличество циклов чтения", "test2"])

    def get_all_disc_path(self) -> None:
        """Все диски"""
        column_position = 0
        for drive in self.drive_code:
            smart_command = subprocess.run(["smartctl", "-i", f"{drive}"], capture_output=True,
                                           text=True)
            result = smart_command.stdout
            data = result.split("\n")
            data = data[4:]
            if "=== START OF INFORMATION SECTION ===" in data:
                data = data[1:]
            data = data[0].split(":")
            disc_name = data[1].replace(" ", "")
            self.tableWidget.setItem(0, column_position, QTableWidgetItem(f"{disc_name}"))
            column_position += 1

    def get_disc_read_count(self) -> None:
        """Количество циклов чтения"""
        column_position = 0
        for drive in self.drive_code:
            smart_command = subprocess.run(["smartctl", "-a", f"{drive}"], capture_output=True, text=True)
            result = smart_command.stdout
            data = result.split("\n")
            for item in data:
                if "Data Units Read:" in item:
                    read_count = item.replace("Data Units Read:", "")
                    read_count = read_count.replace(" ", "")
                    self.tableWidget.setItem(1, column_position, QTableWidgetItem(f"{read_count}"))
                    if self.tableWidget.item(1, column_position - 1) is None:
                        self.tableWidget.setItem(1, column_position - 1, QTableWidgetItem(f"Не "
                                                                                          f"возможно подсчитать"))
            column_position += 1


