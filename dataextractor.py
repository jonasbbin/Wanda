import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLineEdit, QPushButton, QLabel, QGridLayout, QComboBox
from PyQt5.QtGui import QPixmap
from identification import Identifier
import re

"""
Designes the window that acts like the filemaker
"""
class DataExtractor(QWidget):
    def __init__(self, PATH_TO_Image_plant, PATH_TO_Image_location, PATH_TO_date, location, plant, plant_id, date, X, Y, height, identifier=None, authorid="97", idx=0):
        #Initilizes fields for the window
        #Could be optimized
        super().__init__()
        self.location = location
        self.original_location = location
        self.plant = plant
        self.plant_id = plant_id
        self.date = date
        self.fix_date()
        self.X = X
        self.Y = Y
        self.authorid = authorid
        self.accuracy = ""
        if identifier == None:
            self.identifier = Identifier(only_SG=False)
        else:
            self.identifier = identifier
        self.sg_identifier = Identifier(only_SG=True)
        self.height = height
        self.path_to_image_plant = PATH_TO_Image_plant
        self.path_to_image_location = PATH_TO_Image_location
        self.path_to_date = PATH_TO_date

        self.gemeinde , self.canton, self.country = self.identifier.get_gemeinde_region_canton(self.X, self.Y)
        self.region = ""
        self.idx = idx
        self.init_ui()


    
    def fix_date(self):
        """
        Simple logics to improve the date output of the model
        """
        # Split the string by common delimiters like '-', '/', ' ' in case they exist
        parts = re.split(r'[-/.;:,\s]', self.date) 

        # Extract day, month, and year components
        if len(parts)<3:
            #Try to fix data
            if len(self.date)>4:
                if(self.date[2]=="."):
                   self.date = self.date[0:4]+"." + self.date[4:]
                else:
                    self.date = self.date[0:2]+"." + self.date[2:3] +"." + self.date[4:]
                self.fix_date()
                return
            else:
                self.date = ""
                return

        if parts[0].isdigit():
            if len(parts[0])>2:
                day = parts[0][0:2]
            else:
                day = parts[0].zfill(2)
        else:
            day = "00"

        if parts[1].isdigit():
            if len(parts[1])>2:
                month = parts[1][0:2]
            else:
                month = parts[1].zfill(2)
        else:
            month = "00"

        if parts[2].isdigit():
            if len(parts[2])>4:
                year = parts[2][0:4]
            elif len(parts[2])==2:
                year = "19"+parts[2]
            elif len(parts[2])==3:
                year = "1" + parts[2]
            else:
                year = "0000"
        else:
            year = "0000"


        # Return the reformatted string
        self.date =  f"{day}.{month}.{year}"

    def plant_search(self):
        """
        Find the closest plant in the database and it's corresponding ID.
        If empty also makes the ID empty
        """
        new_plant = self.identifier.get_closest_plant(self.plant_name_entry.text())
        self.plant_name_entry.setText(str(new_plant[0]))
        id = self.identifier.get_plant_id(new_plant[0])[0]
        self.plant_id_entry.setText(str(id))
    
    def local_location_search(self):
        """
        Find the closest locations in the database and update all related fields.
        If empty also empty all related fields.
        Only looks at locations near the canton St. Gallen
        """
        new_location = self.sg_identifier.get_closest_location(self.location_entry.text())
        self.location_entry.setText(new_location[0])
        E, N, H = self.sg_identifier.get_location_metrics(new_location[0])

        self.gemeinde, self.canton, self.country = self.sg_identifier.get_gemeinde_region_canton(E[0], N[0])

        self.x_coord_entry.setText(str(E[0]))
        self.y_coord_entry.setText(str(N[0]))
        self.height_entry.setText(str(H[0]))
        self.gemeinde_entry.setText(self.gemeinde)
        self.canton_entry.setText(self.canton)
        self.land_entry.setText(self.country)

    def location_search(self):
        """
        Find the closest locations in the database and update all related fields.
        If empty also empty all related fields.
        Looks at the whole of Switzerland
        """
        new_location = self.identifier.get_closest_location(self.location_entry.text())
        self.location_entry.setText(new_location[0])
        E, N, H = self.identifier.get_location_metrics(new_location[0])

        self.gemeinde, self.canton, self.country = self.identifier.get_gemeinde_region_canton(E[0], N[0])

        self.x_coord_entry.setText(str(E[0]))
        self.y_coord_entry.setText(str(N[0]))
        self.height_entry.setText(str(H[0]))
        self.gemeinde_entry.setText(self.gemeinde)
        self.canton_entry.setText(self.canton)
        self.land_entry.setText(self.country)

    def update_gemeinde(self):
        """
        Updates Gemeinde, Kanton and Land
        """
        self.gemeinde, self.canton, self.country = self.identifier.get_gemeinde_region_canton(int(self.x_coord_entry.text()), int(self.y_coord_entry.text()))
        self.gemeinde_entry.setText(self.gemeinde)
        self.canton_entry.setText(self.canton)
        self.land_entry.setText(self.country)

    
    def init_ui(self):
        
        layout = QVBoxLayout()
        grid_layout = QGridLayout()
        # Show an image at the start
        image_label = QLabel(self)
        pixmap = QPixmap(self.path_to_image_plant)  # Replace 'path_to_your_image.jpg' with your image file path
        scaled_pixmap = pixmap.scaledToWidth(1080)  # Scale image to a width of 720 pixels
        if scaled_pixmap.height() > 100:  # Ensure the image height fits within 480 pixels
            scaled_pixmap = scaled_pixmap.scaledToHeight(100)
        image_label.setPixmap(scaled_pixmap)
        layout.addWidget(image_label)

        image_label3 = QLabel(self)
        pixmap3 = QPixmap(self.path_to_date)  # Replace 'path_to_your_image.jpg' with your image file path
        scaled_pixmap3 = pixmap3.scaledToWidth(1080)  # Scale image to a width of 720 pixels
        if scaled_pixmap3.height() > 100:  # Ensure the image height fits within 480 pixels
            scaled_pixmap3 = scaled_pixmap3.scaledToHeight(100)
        image_label3.setPixmap(scaled_pixmap3)
        layout.addWidget(image_label3)

        image_label2 = QLabel(self)
        pixmap2 = QPixmap(self.path_to_image_location)  # Replace 'path_to_your_image.jpg' with your image file path
        scaled_pixmap2 = pixmap2.scaledToWidth(1080)  # Scale image to a width of 720 pixels
        if scaled_pixmap2.height() > 125:  # Ensure the image height fits within 480 pixels
            scaled_pixmap2 = scaled_pixmap2.scaledToHeight(100)
        image_label2.setPixmap(scaled_pixmap2)
        layout.addWidget(image_label2)

        plant_name = QLineEdit(self)
        plant_name.setText("Original Taxonname")
        plant_name.setStyleSheet("color: grey")  # Set text color to grey
        plant_name.setReadOnly(True) 

        self.plant_name_entry = QLineEdit(self)
        self.plant_name_entry.setText(self.plant)
        self.plant_name_entry.setStyleSheet("color: white")  # Set initial text color to grey
        self.plant_name_entry.selectAll()  # Select all text when entry is focused

        plant_id = QLineEdit(self)
        plant_id.setText("SISF_NR")
        plant_id.setStyleSheet("color: grey")  # Set text color to grey
        plant_id.setReadOnly(True) 

        self.plant_id_entry = QLineEdit(self)
        self.plant_id_entry.setText(str(self.plant_id))
        self.plant_id_entry.setStyleSheet("color: white")  # Set initial text color to grey
        self.plant_id_entry.selectAll()  # Select all text when entry is focused

        date = QLineEdit(self)
        date.setText("Datum")
        date.setStyleSheet("color: grey")  # Set text color to grey
        date.setReadOnly(True) 

        self.date_entry = QLineEdit(self)
        self.date_entry.setText(self.date)
        self.date_entry.setStyleSheet("color: white")  # Set initial text color to grey
        self.date_entry.selectAll()  # Select all text when entry is focused

        location = QLineEdit(self)
        location.setText("Ort")
        location.setStyleSheet("color: grey")  # Set text color to grey
        location.setReadOnly(True) 

        self.location_entry = QLineEdit(self)
        self.location_entry.setText(self.location)
        self.location_entry.setStyleSheet("color: white")  # Set initial text color to grey
        self.location_entry.selectAll()  # Select all text when entry is focused

        x_coord = QLineEdit(self)
        x_coord.setText("X_Koordinate")
        x_coord.setStyleSheet("color: grey")  # Set text color to grey
        x_coord.setReadOnly(True) 

        self.x_coord_entry = QLineEdit(self)
        self.x_coord_entry.setText(str(self.X))
        self.x_coord_entry.setStyleSheet("color: white")  # Set initial text color to grey
        self.x_coord_entry.selectAll()  # Select all text when entry is focused

        y_coord = QLineEdit(self)
        y_coord.setText("Y Koordinate")
        y_coord.setStyleSheet("color: grey")  # Set text color to grey
        y_coord.setReadOnly(True) 

        self.y_coord_entry = QLineEdit(self)
        self.y_coord_entry.setText(str(self.Y))
        self.y_coord_entry.setStyleSheet("color: white")  # Set initial text color to grey
        self.y_coord_entry.selectAll()  # Select all text when entry is focused

        height = QLineEdit(self)
        height.setText("Höhe")
        height.setStyleSheet("color: grey")  # Set text color to grey
        height.setReadOnly(True) 

        self.height_entry = QLineEdit(self)
        self.height_entry.setText(str(self.height))
        self.height_entry.setStyleSheet("color: white")  # Set initial text color to grey
        self.height_entry.selectAll()  # Select all text when entry is focused

        author = QLineEdit(self)
        author.setText("SammlerID")
        author.setStyleSheet("color: grey")  # Set text color to grey
        author.setReadOnly(True) 

        self.author_entry = QLineEdit(self)
        self.author_entry.setText(str(self.authorid))
        self.author_entry.setStyleSheet("color: white")  # Set initial text color to grey
        self.author_entry.selectAll()  # Select all text when entry is focused

        original_ort = QLineEdit(self)
        original_ort.setText("Fundort Orginaltext")
        original_ort.setStyleSheet("color: grey")  # Set text color to grey
        original_ort.setReadOnly(True) 

        self.original_ort_entry = QLineEdit(self)
        self.original_ort_entry.setText(str(self.location))
        self.original_ort_entry.setStyleSheet("color: white")  # Set initial text color to grey
        self.original_ort_entry.selectAll()  # Select all text when entry is focused

        gemeinde = QLineEdit(self)
        gemeinde.setText("Gemeinde")
        gemeinde.setStyleSheet("color: grey")  # Set text color to grey
        gemeinde.setReadOnly(True) 

        self.gemeinde_entry = QLineEdit(self)
        self.gemeinde_entry.setText(str(self.gemeinde))
        self.gemeinde_entry.setStyleSheet("color: white")  # Set initial text color to grey
        self.gemeinde_entry.selectAll()  # Select all text when entry is focused

        canton = QLineEdit(self)
        canton.setText("Kanton")
        canton.setStyleSheet("color: grey")  # Set text color to grey
        canton.setReadOnly(True) 

        self.canton_entry = QLineEdit(self)
        self.canton_entry.setText(str(self.canton))
        self.canton_entry.setStyleSheet("color: white")  # Set initial text color to grey
        self.canton_entry.selectAll()  # Select all text when entry is focused

        land = QLineEdit(self)
        land.setText("Land")
        land.setStyleSheet("color: grey")  # Set text color to grey
        land.setReadOnly(True) 

        self.land_entry = QLineEdit(self)
        self.land_entry.setText(str(self.country))
        self.land_entry.setStyleSheet("color: white")  # Set initial text color to grey
        self.land_entry.selectAll()  # Select all text when entry is focused

        genauigkeit = QLineEdit(self)
        genauigkeit.setText("Genauigkeit")
        genauigkeit.setStyleSheet("color: grey")  # Set text color to grey
        genauigkeit.setReadOnly(True) 

        self.genauigkeit_entry = QComboBox()
        self.genauigkeit_entry.addItems(['ungenau', '1000', '500', '200'])
        self.genauigkeit_entry.setCurrentText('ungenau')  # Default selection
        
        region = QLineEdit(self)
        region.setText("Region")
        region.setStyleSheet("color: grey")  # Set text color to grey
        land.setReadOnly(True) 

        self.region_entry = QLineEdit(self)
        self.region_entry.setText(self.region)
        self.region_entry.setStyleSheet("color: white")  # Set initial text color to grey
        self.region_entry.selectAll()  # Select all text when entry is focused


        submit_button = QPushButton("Submit", self)
        submit_button.clicked.connect(self.on_submit)

        plant_search_button = QPushButton("Suchen", self)
        plant_search_button.clicked.connect(self.plant_search)

        location_search_button = QPushButton("Schweizweit Suchen", self)
        location_search_button.clicked.connect(self.location_search)

        local_location_search_button = QPushButton("Lokal Suchen", self)
        local_location_search_button.clicked.connect(self.local_location_search)

        region_update = QPushButton("Region Updaten", self)
        region_update.clicked.connect(self.update_gemeinde)

        grid_layout.addWidget(plant_name, 0, 0)
        grid_layout.addWidget(self.plant_name_entry, 0, 1)
        grid_layout.addWidget(plant_search_button, 0, 2)
        
        grid_layout.addWidget(plant_id, 1,0)
        grid_layout.addWidget(self.plant_id_entry, 1, 1)
    
        grid_layout.addWidget(date, 2, 0)
        grid_layout.addWidget(self.date_entry, 2, 1)
        
        grid_layout.addWidget(location, 3, 0)
        grid_layout.addWidget(self.location_entry, 3, 1)
        grid_layout.addWidget(local_location_search_button, 3, 2)
        

        grid_layout.addWidget(x_coord, 4, 0)
        grid_layout.addWidget(self.x_coord_entry, 4, 1)
        grid_layout.addWidget(location_search_button, 4, 2)
        
        grid_layout.addWidget(y_coord, 5, 0)
        grid_layout.addWidget(self.y_coord_entry, 5, 1)

        grid_layout.addWidget(height, 6, 0)
        grid_layout.addWidget(self.height_entry, 6, 1)

        grid_layout.addWidget(author, 7,0)
        grid_layout.addWidget(self.author_entry ,7, 1)

        grid_layout.addWidget(original_ort, 8, 0)
        grid_layout.addWidget(self.original_ort_entry, 8, 1)

        grid_layout.addWidget(gemeinde, 9, 0)
        grid_layout.addWidget(self.gemeinde_entry, 9, 1)
        grid_layout.addWidget(region_update, 9,2)

        grid_layout.addWidget(canton, 10, 0)
        grid_layout.addWidget(self.canton_entry, 10, 1)

        grid_layout.addWidget(land, 11, 0)
        grid_layout.addWidget(self.land_entry, 11, 1)

        grid_layout.addWidget(genauigkeit, 12, 0)
        grid_layout.addWidget(self.genauigkeit_entry, 12, 1)

        grid_layout.addWidget(region, 13, 0)
        grid_layout.addWidget(self.region_entry, 13, 1)

        grid_layout.addWidget(submit_button, 14, 1)
        main_layout = QVBoxLayout()
        
        main_layout.addLayout(layout)
        main_layout.addLayout(grid_layout)
        
        self.setTabOrder(self.plant_name_entry, self.plant_id_entry)
        self.setTabOrder(self.plant_id_entry, self.date_entry)
        self.setTabOrder(self.date_entry, self.location_entry)
        self.setTabOrder(self.location_entry, self.x_coord_entry)
        self.setTabOrder(self.x_coord_entry, self.y_coord_entry)
        self.setTabOrder(self.y_coord_entry, self.height_entry)
        self.setTabOrder(self.height_entry, self.author_entry)
        self.setTabOrder(self.author_entry, self.original_ort_entry)
        self.setTabOrder(self.original_ort_entry, self.gemeinde_entry)
        self.setTabOrder(self.gemeinde_entry, self.canton_entry)
        self.setTabOrder(self.canton_entry, self.land_entry)
        self.setLayout(main_layout)
        self.setWindowTitle("Datenverifizierung Pflanze Nr. " + str(self.idx))
        self.setFixedSize(1280, 720)  # Set window size to 480p
        self.show()
        self.raise_()

    def on_submit(self):
        self.plant = self.plant_name_entry.text()
        self.plant_id = self.plant_id_entry.text()
        self.location = self.location_entry.text()
        self.date = self.date_entry.text()
        self.X = self.x_coord_entry.text()
        self.Y = self.y_coord_entry.text()
        self.height = self.height_entry.text()
        self.region = self.region_entry.text()
        self.authorid = self.author_entry.text()
        self.gemeinde = self.gemeinde_entry.text()
        self.original_location = self.original_ort_entry.text()
        self.canton = self.canton_entry.text()
        self.country = self.land_entry.text()
        self.accuracy = self.genauigkeit_entry.currentText()
        self.region = self.region_entry.text()

        self.close()

def main():
    app = QApplication(sys.argv)
    ex = DataExtractor("Extractions/test_folder/Plants/plant_01.jpg", "Extractions/test_folder/Locations/location_01.jpg", "Extractions/test_folder/Dates/date_01.jpg","SG", "Baum", "01", "1.2.963", "2692184", "1207246", "399")
    app.exec_()
    #sys.exit(app.exec_())


if __name__ == '__main__':
    main()
