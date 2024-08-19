from PyQt6.QtWidgets import (
    QApplication,
    QFileDialog,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QListWidget,
)
import sys
import logging


class DirectorySelector(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Multiple Directory Selector")
        self.setGeometry(100, 100, 500, 400)

        self.selected_directories = []
        self.select_button = QPushButton("Add directory containing films")
        self.select_button.clicked.connect(self.open_file_dialog)

        # Create a button to close the dialog
        self.done_button = QPushButton("Done")
        self.done_button.clicked.connect(self.close_dialog)

        # Create a list widget to display selected directories
        self.directory_list = QListWidget()

        # Create a layout and central widget
        layout = QVBoxLayout()
        layout.addWidget(self.select_button)
        layout.addWidget(self.directory_list)
        layout.addWidget(self.done_button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def open_file_dialog(self):
        dialog = QFileDialog(self)
        dialog.setFileMode(QFileDialog.FileMode.Directory)
        dialog.setOption(QFileDialog.Option.ShowDirsOnly, True)
        dialog.setOption(QFileDialog.Option.DontUseNativeDialog, True)

        if dialog.exec():
            selected_dirs = dialog.selectedFiles()
            if selected_dirs:
                directory = selected_dirs[0]
                if directory not in self.selected_directories:
                    self.selected_directories.append(directory)
                    self.directory_list.addItem(directory)

    def close_dialog(self):
        self.close()

    def get_input_directories(self):
        logging.info(
            "Please select one or multiple folders where your films are stored, then click Done"
        )
        self.show()
        QApplication.instance().exec()
        return self.selected_directories
