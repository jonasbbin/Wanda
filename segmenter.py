import cv2
import math
import numpy as np
import datetime
import os
import sys
from datetime import datetime
from regionselector import Regionselector
from PyQt5.QtWidgets import QApplication
from main_point_verifier import Verifier

"""
Class to extract a line of text from the scan. There are three categories:
    Plants
    Dates
    Locations
"""
class Segmenter():
    def __init__(self) -> None:
        """
        We use the East model from cv2
        """
        self.net = cv2.dnn.readNet('Checkpoints/frozen_east_text_detection.pb')

    def decode(self, scores, geometry, scoreThresh):
        """
        Used to decode predictions from east
        """
        detections = []
        confidences = []

        ############ CHECK DIMENSIONS AND SHAPES OF geometry AND scores ############
        assert len(scores.shape) == 4, "Incorrect dimensions of scores"
        assert len(geometry.shape) == 4, "Incorrect dimensions of geometry"
        assert scores.shape[0] == 1, "Invalid dimensions of scores"
        assert geometry.shape[0] == 1, "Invalid dimensions of geometry"
        assert scores.shape[1] == 1, "Invalid dimensions of scores"
        assert geometry.shape[1] == 5, "Invalid dimensions of geometry"
        assert scores.shape[2] == geometry.shape[2], "Invalid dimensions of scores and geometry"
        assert scores.shape[3] == geometry.shape[3], "Invalid dimensions of scores and geometry"
        height = scores.shape[2]
        width = scores.shape[3]
        for y in range(0, height):

            # Extract data from scores
            scoresData = scores[0][0][y]
            x0_data = geometry[0][0][y]
            x1_data = geometry[0][1][y]
            x2_data = geometry[0][2][y]
            x3_data = geometry[0][3][y]
            anglesData = geometry[0][4][y]
            for x in range(0, width):
                score = scoresData[x]

                # If score is lower than threshold score, move to next x
                if(score < scoreThresh):
                    continue

                # Calculate offset
                offsetX = x * 4.0
                offsetY = y * 4.0
                angle = anglesData[x]

                # Calculate cos and sin of angle
                cosA = math.cos(angle)
                sinA = math.sin(angle)
                h = x0_data[x] + x2_data[x]
                w = x1_data[x] + x3_data[x]

                # Calculate offset
                offset = ([offsetX + cosA * x1_data[x] + sinA * x2_data[x], offsetY - sinA * x1_data[x] + cosA * x2_data[x]])

                # Find points for rectangle
                p1 = (-sinA * h + offset[0], -cosA * h + offset[1])
                p3 = (-cosA * w + offset[0],  sinA * w + offset[1])
                center = (0.5*(p1[0]+p3[0]), 0.5*(p1[1]+p3[1]))
                detections.append((center, (w,h), -1*angle * 180.0 / math.pi))
                confidences.append(float(score))

        # Return detections and confidences
        return [detections, confidences]
    
    def get_rectangle_corners(self, point1, point2):
        x_values = [point1[0], point2[0]]
        y_values = [point1[1], point2[1]]

        min_x = min(x_values)
        max_x = max(x_values)
        min_y = min(y_values)
        max_y = max(y_values)

        corners = np.array([
            [min_x, max_y],  # Bottom-left corner
            [min_x, min_y],  # Top-left corner
            [max_x, min_y],  # Top-right corner
            [max_x, max_y],  # Bottom-right corner
        ])

        return corners
    
    def partition(self, arr, low, high, compare):
            pivot = arr[high]
            i = low - 1

            for j in range(low, high):
                if compare(arr[j], pivot) <= 0:
                    i += 1
                    arr[i], arr[j] = arr[j], arr[i]

            arr[i + 1], arr[high] = arr[high], arr[i + 1]
            return i + 1

    def quick_sort(self, arr, low, high, compare):
        """
        basic quicksort for the custom sorting function
        """
        if low < high:
            pi = self.partition(arr, low, high, compare)

            self.quick_sort(arr, low, pi - 1, compare)
            self.quick_sort(arr, pi + 1, high, compare)


    def sort_boxes(self, item_a, item_b):
        """
        Sorts the corrected boxes such that they are sorted line by line
        """
        
        width_1 = np.min(item_a[:, 0])#item_a[0][0]
        height_1 = np.min(item_a[:, 1])
        width_2 = np.min(item_b[:, 0])
        height_2 = np.min(item_b[:, 1])


        height_diff = height_1 - height_2
        if height_diff > self.height_scaler* 100: # 1 is lower on different line
            return 1 # 2 is before 1
        elif height_diff < -100*self.height_scaler:
            return -1 # 1 is before 2

        if width_1 < width_2: # 1 is more left
            return -1 #1 is before 2
        return 1

    
    def segment(self, path_to_scan):
        assert os.path.exists(path_to_scan)
        regionselector = Regionselector()
        image = cv2.imread(path_to_scan)
        frame = np.copy(image)
        H,W, _ = np.shape(image)
        H_original, W_original = (8387.0, 12992.0)
        H_extractor, W_extractor = (2048, 1024+2048)
        self.height_scaler = H/H_original
        # Prepare the image for EAST, (123.68, 116.78, 103.94) used for training the model
        blob = cv2.dnn.blobFromImage(image, 1.0, (W_extractor, H_extractor), (123.68, 116.78, 103.94), swapRB=True, crop=False)

        #output layers to calc scores and geometry
        outputLayers = []
        outputLayers.append("feature_fusion/Conv_7/Sigmoid")
        outputLayers.append("feature_fusion/concat_3")

        # Set the prepared blob as the input to the network and perform a forward pass
        self.net.setInput(blob)
        (scores, geometry) = self.net.forward(outputLayers)
        # Define the minimum confidence threshold for text detection
        confThreshold = 0.1  # You can adjust this threshold

        [boxes, confidences] = self.decode(scores, geometry, confThreshold)
        # Apply NMS
        indices = cv2.dnn.NMSBoxesRotated(boxes, confidences, confThreshold,0.2)
        rW = W/ float(W_extractor)
        rH = H / float(H_extractor)

        corrected_boxes=[]
        for i in indices:
            # get 4 corners of the rotated rect
            test = boxes[i]#i[0]
            vertices = cv2.boxPoints(test)
            # scale the bounding box coordinates based on the respective ratios
            for j in range(4):
                vertices[j][0] *= rW
                vertices[j][1] *= rH
            box = np.intp(vertices)
            corrected_boxes.append(box)
            
        

        self.quick_sort(corrected_boxes, 0, len(corrected_boxes) - 1, self.sort_boxes)
        nr_idx = -1
        date_idx = -1
        i = 0
        #We want to find the Nr. and Date title. Allows us to categorize boxes
        while(nr_idx ==-1 or date_idx ==-1):
            box = corrected_boxes[i]
            coord_1 = box[0,0]
            if (coord_1 < int(3000.0*W/W_original) and nr_idx==-1):
                nr_idx = i
            if (int(6000.0*W/W_original)  < coord_1 < int(8000.0*W/W_original)  and date_idx==-1):
                date_idx = i
            i+=1

        numberbox = corrected_boxes[nr_idx]
        datebox = corrected_boxes[date_idx]
        cv2.drawContours(frame,[datebox], 0, (255, 0, 0), int(50*W/W_original))
        cv2.drawContours(frame,[numberbox], 0, (0, 0, 255), int(50*W/W_original))

        #Check with the user if detection was successful
        cv2.imwrite('temp.jpg', frame)
        app = QApplication(sys.argv)
        verifier = Verifier('temp.jpg')
        app.exec_()
        
        #Adjust if there is a mistake
        if not verifier.number_okay:
            vertices, _ = regionselector.find_additional('temp.jpg', [], scaling=W/W_original)
            numberbox = self.get_rectangle_corners(vertices[0], vertices[1])

        if not verifier.date_okay:
            vertices, _ = regionselector.find_additional('temp.jpg', [], scaling=W/W_original)
            datebox = self.get_rectangle_corners(vertices[0], vertices[1])
        os.remove('temp.jpg')
        
        plantboxes = []
        locationboxes = []
        dateboxes = []

        #Categorize boxes using the Nr and Date boxes
        for box in corrected_boxes:
            coord_1 = box[0,0]
            coord_4 = box[3,0]
            height_2 = box[1, 1]
            
            #In the title line
            if (box[1, 1]- box[0,1] > box[3,0] - box[0,0] ):
                continue
            if (coord_1 > numberbox[3, 0] and coord_4 < datebox[0,0] and height_2 > numberbox[3, 1]):
                plantboxes.append(box)
            elif (coord_1 > datebox[3,0] and height_2 > datebox[3, 1]):
                locationboxes.append(box)
            #Make sure to extract the date
            elif (coord_1 < datebox[3,0] and coord_1 > datebox[0, 0]-int(300.0*W/W_original)  and height_2 > datebox[3, 1]):
                if height_2 > datebox[3, 1] + int(1000.0*H/H_original) :
                    if coord_1 > datebox[0, 0]-int(100.0*W/W_original) :
                        dateboxes.append(box)
                else:
                    dateboxes.append(box)

        merged_plantboxes = []
        while len(plantboxes)>0:
            currbox = plantboxes.pop(0)
            curr_height = currbox[0,1]
            curr_start = currbox[1] #top left
            curr_end = currbox[3] #top right

            #Skip cases when somewhere in the line
            if(curr_start[0]> numberbox[3][0]+int(700.0*W/W_original) ):
                continue

            #Merge along the line
            while(len(plantboxes)>0 and np.abs(curr_height - plantboxes[0][0,1]) < int(200.0*H/H_original) ):
                next_box = plantboxes.pop(0)
                curr_end = next_box[3]
            merged_plantboxes.append([curr_start, curr_end])


        #Apply Bounding box constraints
        for box in merged_plantboxes:
            #Adjust height
            if (box[1][1]- box[0][1] < int(250.0*H/H_original)  ):
                gainedspace = int(250.0*H/H_original)  - (box[1][1]- box[0][1])
                box[1][1] += int(gainedspace/2)
                box[0][1] -= int(gainedspace/2)
            #Adjust width
            if (box[1][0] - box[0][0] < int(2500.0*W/W_original) ):
                gainedspace = int(2500.0*W/W_original)  - (box[1][0] - box[0][0])
                box[1][0] += gainedspace #We are at the left border, only increase to the right
            box[0][0] -= int(150.0*W/W_original) 
            box[1][0] += int(50.0*W/W_original) 

        merged_dateboxes = []
        while len(dateboxes)>0:
            currbox = dateboxes.pop(0)
            curr_height = currbox[0,1]
            curr_start = currbox[1] #top left
            curr_end = currbox[3] #top right

            while(len(dateboxes)>0 and np.abs(curr_height - dateboxes[0][0,1]) < int(200.0*H/H_original) ):#220):
                next_box = dateboxes.pop(0)
                curr_end = next_box[3]
            merged_dateboxes.append([curr_start, curr_end])

        for box in merged_plantboxes:
            cv2.rectangle(frame, box[0], box[1], (255, 0, 0), 50)

        merged_locationboxes = []
        while len(locationboxes)>0:
            currbox = locationboxes.pop(0)
            curr_height = currbox[0,1]
            curr_start = currbox[1] #top left
            curr_end = currbox[3] #top right

            #Skip cases when somewhere in the line
            if(curr_start[0]> datebox[3][0]+int(800.0*W/W_original) ):
                continue

            while(len(locationboxes)>0 and np.abs(curr_height - locationboxes[0][0,1]) < int(200.0*H/H_original) ):
                #print("hello")
                next_box = locationboxes.pop(0)
                curr_end = next_box[3]
            merged_locationboxes.append([curr_start, curr_end])

        #Minimal Bounding box constraints
        for box in merged_locationboxes:
            #Adjust height
            if (box[1][1]- box[0][1] < int(250.0*H/H_original)  ):
                gainedspace = int(250.0*H/H_original)  - (box[1][1]- box[0][1])
                box[1][1] += int(gainedspace/2)
                box[0][1] -= int(gainedspace/2)
            #Adjust width
            if (box[1][0] - box[0][0] < int(2500.0*W/W_original) ):
                gainedspace = int(2500.0*W/W_original)  - (box[1][0] - box[0][0])
                box[1][0] += gainedspace #We are at the left border, only increase to the right
            box[0][0] -= int(120.0*W/W_original) 
            box[1][0] += int(50.0*W/W_original) 
        for box in merged_locationboxes:
            cv2.rectangle(frame, box[0], box[1], (0, 255, 0), 50)
        
        for box in merged_dateboxes:
            #Adjust height
            if (box[1][1]- box[0][1] < int(250.0*H/H_original)  ):
                gainedspace = int(250.0*H/H_original)  - (box[1][1]- box[0][1])
                box[1][1] += int(gainedspace/2)
                box[0][1] -= int(gainedspace/2)
            #Ajust width
            if (box[1][0] - box[0][0] < int(700.0*W/W_original) ):
                gainedspace = int(700.0*W/W_original) - (box[1][0] - box[0][0])
                box[1][0] += gainedspace #We are at the left border, only increase to the right
            box[0][0] -= int(70.0*W/W_original)
        for box in merged_dateboxes:
            cv2.rectangle(frame, box[0], box[1], (0, 0, 255), 50)

        #We know every page has exactly 25 entires
        #Finde more if there are to few, with the help of the user       
        while len(merged_locationboxes)<25:
            #print("Missing Locations")
            coord, index = regionselector.find_additional(path_to_scan, merged_locationboxes, scaling=W/W_original)
            merged_locationboxes.insert(index, coord)
        while len(merged_plantboxes)< 25:
            #print("Missing Plants")
            coord, index = regionselector.find_additional(path_to_scan, merged_plantboxes, scaling=W/W_original)
            merged_plantboxes.insert(index, coord)
        while len(merged_dateboxes)<25:
           # print("Missing Dates")
            coord, index = regionselector.find_additional(path_to_scan, merged_dateboxes, scaling=W/W_original)
            merged_dateboxes.insert(index, coord)

        #We know every page has exactly 25 entires
        #Delete boxes if there are too many           
        while len(merged_locationboxes)>25:
            #print("Too many Locations")
            id = regionselector.get_nearest_box(path_to_scan, merged_locationboxes, scaling=W/W_original)
            merged_locationboxes.pop(id)
        while len(merged_plantboxes)> 25:
            print("Too many Plants")
            id = regionselector.get_nearest_box(path_to_scan, merged_plantboxes, scaling=W/W_original)
            merged_plantboxes.pop(id)
        while len(merged_plantboxes)> 25:
            print("Too many Dates")
            id = regionselector.get_nearest_box(path_to_scan, merged_dateboxes, scaling=W/W_original)
            merged_plantboxes.pop(id)
        #Create Output folders
        dt_string = now = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
        os.mkdir("Extractions/"+dt_string)
        os.mkdir("Extractions/"+dt_string+"/Locations")
        os.mkdir("Extractions/"+dt_string+"/Plants")
        os.mkdir("Extractions/"+dt_string+"/Dates")
        
        #Output
        for idx, box in enumerate(merged_locationboxes):
            x0 = box[0][0]
            y0 = box[0][1]
            x1 = box[1][0]
            y1 = box[1][1]

            cropped_image = image[y0:y1, x0:x1]
            img_idx = str(idx+1).zfill(2)
            cv2.imwrite(f'Extractions/{dt_string}/Locations/location_{img_idx}.jpg', cropped_image)

        for idx, box in enumerate(merged_plantboxes):
            x0 = box[0][0]
            y0 = box[0][1]
            x1 = box[1][0]
            y1 = box[1][1]
            cropped_image = image[y0:y1, x0:x1]
            img_idx = str(idx+1).zfill(2)
            cv2.imwrite(f'Extractions/{dt_string}/Plants/plant_{img_idx}.jpg', cropped_image)

        for idx, box in enumerate(merged_dateboxes):
            x0 = box[0][0]
            y0 = box[0][1]
            x1 = box[1][0]
            y1 = box[1][1]
            cropped_image = image[y0:y1, x0:x1]
            img_idx = str(idx+1).zfill(2)
            cv2.imwrite(f'Extractions/{dt_string}/Dates/date_{img_idx}.jpg', cropped_image)
        return (f'Extractions/{dt_string}')
            