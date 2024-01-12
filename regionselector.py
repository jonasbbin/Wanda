import cv2  
import numpy as np
from indexfinder import IndexFinder
from PyQt5.QtWidgets import QApplication
import sys
import os

"""
Allows the user to select boxes
"""

class Regionselector():
    def __init__(self) -> None:
        self.x_coord_1 = -1
        self.y_coord_1 = -1
        self.x_coord_0 = -1
        self.y_coord_0 = -1
        self.id = -1
        pass

    #This is inconsistent and not strictly needed, however since it already works we leave it
    def set_cooords(self, x0, y0, x1, y1):
        self.x_coord_1 = x1
        self.y_coord_1 = y1
        self.x_coord_0 = x0
        self.y_coord_0 = y0

    #This is inconsistent and not strictly needed, however since it already works we leave it
    def get_cooords(self):
        return self.x_coord_0, self.y_coord_0, self.x_coord_1, self.y_coord_1
    
    def process_number(self, entry, root):
            number = entry.get()
            self.id = int(number)-1

    def find_additional(self, PATH_TO_Image, boxes, scaling=1,  manual_id = False):
        """
        Draws the existing boxes on to the image and lets the user draw another box. Returns the drawn box
        """
        img = cv2.imread(PATH_TO_Image)
        h,w, _ = np.shape(img)
        for box in boxes:
            cv2.rectangle(img, box[0], box[1], (255, 255, 0), int(scaling*40))
            cv2.line(img,[0,box[1][1]] ,[w,box[1][1]],(255, 255, 0), int(scaling*10))
        img_display = img.copy()
        # Global variables
        selected_x, selected_y = -1, -1
        selected_x_2, selected_y_2 = -1, -1
        tempx, tempy = -1, -1
        selecting = False
        selected = False
        # Mouse callback function
        def select_region(event, x, y, flags, param):
            global selected_x, selected_y, selected, img_display, selected_x_2, selected_y_2, tempx, tempy
            if event == cv2.EVENT_LBUTTONDOWN:
                #selecting = True
                tempx, tempy = x, y
            if event == cv2.EVENT_LBUTTONUP:
                selected = True
                selected_x_2, selected_y_2 = x, y
                selected_x, selected_y = tempx, tempy
                img_display = img.copy()
                cv2.rectangle(img_display, (selected_x, selected_y), (selected_x_2, selected_y_2), (0, 255, 0), int(scaling*30))
                cv2.imshow('Select Region press Q to quit', img_display)
                param.set_cooords(selected_x, selected_y, selected_x_2, selected_y_2)

        

        if manual_id:
            cv2.imwrite('temp_2.jpg', img)
            app = QApplication(sys.argv)
            index_finder = IndexFinder('temp_2.jpg')
            app.exec_()
            self.id = index_finder.id -1
            os.remove('temp_2.jpg')

        cv2.imshow('Select Region press Q to quit', img_display)
        cv2.namedWindow('Select Region press Q to quit')
        cv2.setMouseCallback('Select Region press Q to quit', select_region, self )
        
        while True:
            
            key = cv2.waitKey(0) 

            if key == ord('q') or selected:
                break
        cv2.destroyAllWindows()
        selected_x, selected_y, selected_x_2, selected_y_2 = self.get_cooords()
        #print(f"Found coordinates {selected_x}, {selected_y}, {selected_x_2}, {selected_y_2}")
        if not manual_id:
            self.id = 0
            highest_y = np.max([selected_y, selected_y_2])
            for box in boxes:
                if np.max([box[0][1], box[1][1]]) > highest_y:
                    break
                self.id += 1
        return [[selected_x, selected_y], [selected_x_2, selected_y_2]], self.id
    
    def get_nearest_box(self, PATH_TO_Image, boxes, scaling=1):
        """
        Gets the nearest box to a point selected by the user.
        This function is not that good as it only looks at nearest lower left corner of the boxes.
        However, it turns out that the case that we have too many boxes never occured. Therefore, to save the work this function is not improved
        """

        img = cv2.imread(PATH_TO_Image)
        
        for box in boxes:
            cv2.rectangle(img, box[0], box[1], (255, 255, 0), int(scaling*20))
        img_display = img.copy()
        # Global variables
        selected_x, selected_y = -1, -1
        # Mouse callback function
        def select_region_2(event, x, y, flags, param):
            global selected_x, selected_y, img_display
            if event == cv2.EVENT_LBUTTONDOWN :
                selected_x, selected_y = x, y

                img_display = img.copy()
                cv2.circle(img_display,(selected_x, selected_y), int(scaling*20), (0, 255, 0), -1)
                cv2.imshow('Select Box to remove and press Q to quit', img_display)
                param.set_cooords(selected_x, selected_y, -1, -1)

        

        # Create a window
        cv2.startWindowThread()
        cv2.namedWindow('Select Box to remove and press Q to quit')
        cv2.setMouseCallback('Select Box to remove and press Q to quit', select_region_2, self)
        cv2.imshow('Select Box to remove and press Q to quit', img_display)
        while True:
            
            key = cv2.waitKey(0) 

            if key == ord('q'):
                break
        #cv2.setMouseCallback('Select Box', lambda *args : None)
        cv2.destroyWindow('Select Box to remove and press Q to quit')
        cv2.destroyAllWindows()
        cv2.waitKey(1)
        cv2.waitKey(1)
        cv2.waitKey(1)
        cv2.waitKey(1)
        

        distance = 2000000
        box_id = -1
        selected_x, selected_y, _, _ = self.get_cooords()
        mouse = np.array([selected_x, selected_y])

        
        for id, box in enumerate(boxes):
            cv2.destroyAllWindows()
            x0 = box[0][0]
            y0 = box[0][1]
            x1 = box[1][0]
            y1 = box[1][1]

            center_x = (x0 + x1) / 2
            center_y = (y0 + y1) / 2
    
            # Calculate the coordinates of the other two points
            # Since the all the boxes should be without an angle
            # Other point 1
            other_point1_x = center_x - (y1 - center_y)
            other_point1_y = center_y + (x1 - center_x)
            
            # Other point 2
            other_point2_x = center_x + (y1 - center_y)
            other_point2_x = center_y - (x1 - center_x)

            point_0 = np.array([x0, y0])
            point_1 = np.array([other_point1_x, other_point1_y])
            point_2 = np.array([other_point2_x, other_point2_x])
            point_3 = np.array([x1, y1])
            
            dist_0 = np.linalg.norm(mouse-point_0)
            dist_1 = np.linalg.norm(mouse-point_1)
            dist_2 = np.linalg.norm(mouse-point_2)
            dist_3 = np.linalg.norm(mouse-point_3)

            curr_distance = np.min([dist_0, dist_1, dist_2, dist_3])
            curr_distance = dist_0
            if (curr_distance < distance):
                distance = curr_distance
                box_id = id
        #print(f"Found Box {box_id}")
        cv2.destroyAllWindows()
        return box_id

            
