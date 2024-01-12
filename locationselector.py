import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLineEdit, QPushButton, QLabel
from PyQt5.QtGui import QPixmap

"""
Class no longer in use due to inefficency in the workflow 
"""
class LocationSelector(QWidget):
    """
    Window that lets the user select one of the 5 best matches to the found location
    Can also select the 6. button, which indicates that it is neither location
    Might be useful for a future update
    """
    def __init__(self, PATH_TO_Image_location, results):
        # E, N, height
        super().__init__()
        self.result_1 = results[0]
        self.result_2  = results[1]
        self.result_3  = results[2]
        self.result_4 = results[3]
        self.result_5  = results[4]
        self.path_to_image_location = PATH_TO_Image_location
        self.init_ui()
        self.location = ""
    

    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)
        self.setWindowTitle("Wähle den richtigen Ort")

        image_label2 = QLabel(self)
        pixmap2 = QPixmap(self.path_to_image_location)  # Replace 'path_to_your_image.jpg' with your image file path
        scaled_pixmap2 = pixmap2.scaledToWidth(1080)  # Scale image to a width of 720 pixels
        if scaled_pixmap2.height() > 350:  # Ensure the image height fits within 480 pixels
            scaled_pixmap2 = scaled_pixmap2.scaledToHeight(350)
        image_label2.setPixmap(scaled_pixmap2)
        layout.addWidget(image_label2)

        

        submit_button_1 = QPushButton(self.result_1, self)
        submit_button_1.clicked.connect(self.on_submit_1)

        submit_button_2 = QPushButton(self.result_2, self)
        submit_button_2.clicked.connect(self.on_submit_2)

        submit_button_3 = QPushButton(self.result_3, self)
        submit_button_3.clicked.connect(self.on_submit_3)

        submit_button_4 = QPushButton(self.result_4, self)
        submit_button_4.clicked.connect(self.on_submit_4)

        submit_button_5 = QPushButton(self.result_5, self)
        submit_button_5.clicked.connect(self.on_submit_5)

        submit_button_6 = QPushButton("Keine Trifft zu", self)
        submit_button_6.clicked.connect(self.on_submit_6)


        layout.addWidget(submit_button_1)
        layout.addWidget(submit_button_2)
        layout.addWidget(submit_button_3)
        layout.addWidget(submit_button_4)
        layout.addWidget(submit_button_5)
        layout.addWidget(submit_button_6)
        self.setFixedSize(1280, 480)  # Set window size to 480p
        self.show()
        self.raise_()

    def on_submit_1(self):
        self.location = self.result_1
        self.close()
    
    def on_submit_2(self):
        self.location = self.result_2
        self.close()

    def on_submit_3(self):
        self.location = self.result_3
        self.close()

    def on_submit_4(self):
        self.location = self.result_4
        self.close()

    def on_submit_5(self):
        self.location = self.result_5
        self.close()

    def on_submit_6(self):
        self.location = ""
        self.close()

def main():
    app = QApplication(sys.argv)
    ex = LocationSelector("Extractions/2023_12_22_14_30_05/Locations/location_01.jpg", ["dfas", "sdklafj", "SDFsd", "sdfafd", "skdlfj"])
    app.exec_()
    #sys.exit(app.exec_())

if __name__ == '__main__':
    main()
