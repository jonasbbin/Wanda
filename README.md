
# Wanda
This tool is designed to help digitializing the Kunzer library. It uses the scan of one page of the Kunzer Buch, to extract and detect the different entries. The information needs to be verified at the end and can also be changed if errors occured.

There are different tools implemented to ease the validation process, such as automatic SISF extraction, plant name search, region updates, swiss location search as well as a local location search. 

The program is called with:
`python main.py`

---
## Dependecies
- numpy
- pandas
- geopandas
- shapely
- QtPY5
- cv2
- transformers
- datetime
- matplotlib
---
## Models
We use the [EAST](https://arxiv.org/abs/1704.03155v2) model to find the regions of the scaned page, where text is written. The model can be downloaded [here](https://www.dropbox.com/s/r2ingd0l3zt8hxs/frozen_east_text_detection.tar.gz?dl=1) and needs to be put in a folder 'Checkpoints' in the same directory as Wanda. you can follow [this](https://learnopencv.com/deep-learning-based-text-detection-using-opencv-c-python/) Tutorial if you have problems loading the model.

For the OCR (Optical Character Recognition) part of our program we use the [TrOCR](https://arxiv.org/abs/2109.10282) model from the [HuggingFace library](https://huggingface.co/microsoft/trocr-large-handwritten)

---
## Datasets
These datasets need to be downloaded such that the programme can run correctly:

We use the [swissBOUNDARIES3D](https://www.swisstopo.admin.ch/en/geodata/landscape/boundaries3d.html) dataset for the current boundaries of the different communities/cantons. The repsective GPKG must be manually downloaded.

We extract locations in Switzerland from [swissNAMES3D](https://www.swisstopo.admin.ch/de/geodata/landscape/names3d.html). More specifically the points and  polygons.

The plantnames and their respective SISF numbers are downloaded from [ArtFlora](https://www.infoflora.ch/de/allgemeines/downloads.html).

---
## Functionality
The program first looks for two title, which are present at every page ('Nr.' and 'Datum'). With these the found textboxes can be classified into plant names, dates and locations. The classified boxes are then merged. Since every page has exactly 25 entries the programme knows when not all or too many plants were found. In that case the user is notified to manually select/remove a bounding box via a GUI.
The extracted text boxes are saved temporarly in the folder 'Extractions'. On these boxes we perform OCR and search for the most similar word in our respective database. 
The user is then shown a summary of what the programme found, with the image boxes used for the result.
The output is then saved in the folder 'Outputs'. 

---
## Known Bugs/Issues
These Issues are known, they are however not fixed as it did not hinder the workflow of digitilizing the Kunzer collection or the collection was already digitilized when the bugs became known
- When no matching plantname can be found (with a similarity of at least 1%) from the OCR output of the program throws an unhandled expection.
- When removing a box (due to too many recognized boxes) the user can select a point. The programme removes the box with the nearest lower left corner. This does not always correspond to the box which the point is inside of.
- The merger only supports lists of size 25 for the computation of Kunzer numbers (the other metric are correctly calculated)
- After selecting the last box when adding/removing boxes, the selction window does not close until the OCR prediction is completed.
