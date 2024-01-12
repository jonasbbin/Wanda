from transformers import TrOCRProcessor, VisionEncoderDecoderModel
from cv2 import imread
import os
class HandToText():
    """
    Class to convert a line of handwritten text to computer text
    Model used: https://huggingface.co/microsoft/trocr-large-handwritten
    """
    def __init__(self, model="large") -> None:
        print("Loading Model...")
        if model=="turbo":
            self.processor = TrOCRProcessor.from_pretrained('microsoft/trocr-small-handwritten')
            self.model = VisionEncoderDecoderModel.from_pretrained('microsoft/trocr-small-handwritten')
        elif model=="base":
            self.processor = TrOCRProcessor.from_pretrained('microsoft/trocr-base-handwritten')
            self.model = VisionEncoderDecoderModel.from_pretrained('microsoft/trocr-base-handwritten')
            
        else:
            #This is the best model and suggested the others do not perform that well
            self.processor = TrOCRProcessor.from_pretrained('microsoft/trocr-large-handwritten')
            self.model = VisionEncoderDecoderModel.from_pretrained('microsoft/trocr-large-handwritten')

    def predict(self, image_path):
        """
        predict the text on the image
        """
        image = imread(image_path)
        pixel_values = self.processor(images=image, return_tensors="pt").pixel_values

        generated_ids = self.model.generate(pixel_values)
        generated_text = self.processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
        return generated_text
    
    def predict_folder(self, Path_to_folder):
        """
        predict the text of all images inside a folder. The folder needs to consist of three folders:
        Locations
        Plants
        Dates
        Each of these need to consist of the respective images alligned in the correct order
        """
        text_locations = []
        files = sorted(os.listdir(Path_to_folder+"/Locations"))
        for f in files:
            image_path = os.path.join(Path_to_folder+"/Locations", f)
            print("Looking at: ", f)
            text_locations.append(self.predict(image_path))
        
        text_plants = []
        files = sorted(os.listdir(Path_to_folder+"/Plants"))
        for f in files:
            image_path = os.path.join(Path_to_folder+"/Plants", f)
            print("Looking at: ", f)
            text_plants.append(self.predict(image_path))

        text_dates = []
        files = sorted(os.listdir(Path_to_folder+"/Dates"))
        for f in files:
            image_path = os.path.join(Path_to_folder+"/Dates", f)
            print("Looking at: ", f)
            text_dates.append(self.predict(image_path))

        return text_plants, text_locations, text_dates
