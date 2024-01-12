import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QWidget, QTextEdit, QFileDialog, QGridLayout, QApplication, QWidget, QLineEdit, QLabel, QRadioButton, QButtonGroup
from wanda import Wanda
from merger import Merger

"""
This is the main program that is run to run the wanda program.
This file constructs a window in which the user can choose what he wants to do.
After selecting the window closes and calls the respective process.
"""

class WandaWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.run_wanda_bool = False
        self.run_merging_bool = False
        self.wanda_iscsv = False
        self.merging_iscsv = False
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Wanda 1.0')
        #Window Layout/ Design
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        radio_group = QButtonGroup(self)
        radio_group_2 = QButtonGroup(self)

        layout = QGridLayout()
        select_button = QPushButton('Select File', self)
        select_button.clicked.connect(self.get_file)
        layout.addWidget(select_button, 1 , 1)

        self.wanda_path_entry = QLineEdit(self)
        self.wanda_path_entry.setText(" ")
        self.wanda_path_entry.setStyleSheet("color: white")  # Set initial text color to grey

        path_title = QLineEdit(self)
        path_title .setText("Pfad auswählen")
        path_title .setStyleSheet("background-color: palette(window)")  # Set text color to grey
        path_title .setReadOnly(True) 
        layout.addWidget(path_title , 0 , 0, 1, 2) 
        layout.addWidget(self.wanda_path_entry, 1, 0)

        self.csv_radio_wanda = QRadioButton('CSV Format', self)
        self.csv_radio_wanda.toggled.connect(self.format_selection_wanda)
        layout.addWidget(self.csv_radio_wanda, 2, 0)

        self.xlxx_radio_wanda = QRadioButton('Xlsx Format', self)
        self.xlxx_radio_wanda.toggled.connect(self.format_selection_wanda)
        self.xlxx_radio_wanda.setChecked(True)  # Default selection
        layout.addWidget(self.xlxx_radio_wanda, 2, 1)
        radio_group.addButton(self.csv_radio_wanda)
        radio_group.addButton(self.xlxx_radio_wanda)

        wanda_button = QPushButton('Extraction starten', self)
        wanda_button.clicked.connect(self.run_wanda)
        layout.addWidget(wanda_button, 3 , 0, 1, 2)

        select_button_2 = QPushButton('Ordner auswählen', self)
        select_button_2.clicked.connect(self.get_folder)
        layout.addWidget(select_button_2, 8 , 1)

        self.merger_path_entry = QLineEdit(self)
        self.merger_path_entry.setText(" ")
        self.merger_path_entry.setStyleSheet("color: white")  # Set initial text color to grey
        layout.addWidget(self.merger_path_entry, 8, 0)

        path_title_2 = QLineEdit(self)
        path_title_2.setText("Pfad auswählen")
        path_title_2.setStyleSheet("background-color: palette(window)")  # Set text color to grey
        path_title_2.setReadOnly(True) 
        layout.addWidget(path_title_2 , 7 , 0, 1, 2) 

        self.csv_radio_merging = QRadioButton('CSV Format', self)

        self.csv_radio_merging.toggled.connect(self.format_selection_merging)
        layout.addWidget(self.csv_radio_merging, 9, 0)

        self.xlxx_radio_merging = QRadioButton('Xlsx Format', self)
        self.xlxx_radio_merging.toggled.connect(self.format_selection_merging)
        self.xlxx_radio_merging.setChecked(True)  # Default selection
        layout.addWidget(self.xlxx_radio_merging, 9, 1)
        radio_group_2.addButton(self.csv_radio_merging)
        radio_group_2.addButton(self.xlxx_radio_merging)

        wanda_button = QPushButton('Merging starten', self)
        wanda_button.clicked.connect(self.run_merging)
        layout.addWidget(wanda_button, 10, 0, 1, 2)

        central_widget.setLayout(layout)

    def format_selection_wanda(self):
        """
        Handles output format selection box
        """
        if self.csv_radio_wanda.isChecked():
            self.wanda_iscsv = True
        else:
            self.wanda_iscsv = False
    
    def format_selection_merging(self):
        """
        Handles output format selection box
        """
        if self.csv_radio_merging.isChecked():
            self.merging_iscsv = True
        else:
            self.merging_iscsv = False

    def run_wanda(self):
        """
        Called when starting the wanda extraction
        """
        self.run_wanda_bool = True
        self.close()

    def run_merging(self):
        """
        Called when starting the merging extraction
        """
        self.run_merging_bool = True
        self.close()

    def get_folder(self):
        """
        let's the user select a folder
        """
        folder_dialog = QFileDialog()
        folder_path = folder_dialog.getExistingDirectory(self, 'Select a folder')
        self.merger_path_entry.setText(folder_path)



    def get_file(self):
        """
        Let's the user select a file
        """
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, 'Select a file')
        self.wanda_path_entry.setText(file_path)

        

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = WandaWindow()
    window.show()
    app.exec_()
    app.quit()
    run_wanda = window.run_wanda_bool
    run_merger = window.run_merging_bool
    wanda_iscsv = window.wanda_iscsv
    wanda_path_entry = str(window.wanda_path_entry.text())

    merger_iscsv = window.merging_iscsv
    merger_path_entry = str(window.merger_path_entry.text())
    #This is extremly ugly but Qtpy creates a segmentation fault if you call QApplication a second time
    #I don't know this library so I just force remove the first window
    del app
    if run_wanda:
        #Call Wanda
        wanda = Wanda(wanda_path_entry, csv=wanda_iscsv)

    if run_merger:
        #Call Mergercd
        merger = Merger(merger_iscsv)
        merger.merge(merger_path_entry)
