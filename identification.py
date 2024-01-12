import pandas as pd
from difflib import *
import numpy as np
import geopandas as gpd
from shapely.geometry import Point


class Identifier():
    """
    Class to identify given strings to a matching item in the list
    i.e. locations, coordinates, plantnames
    """
    def __init__(self, only_SG = True) -> None:
        """
        only_SG: Only looks at locations that in or near the border of SG, AI, AR
        """
        self.geo_data = gpd.read_file('swissBOUNDARIES3D_1_5_LV95_LN02.gpkg', layer='TLM_HOHEITSGEBIET' )  # Replace with your file path
        self.geo_data = self.geo_data[self.geo_data.objektart=="Gemeindegebiet"]

        self.location_pd = pd.read_csv("swissNAMES3D_PLY.csv", delimiter=";")
        allowed = ["Ort", "Ortsteil", "Quartierteil", "Historisches Areal", "Tal", "Graben", "See", "Gebiet", "Grat", "Gletscher", "Quartier"]
        self.location_pd = self.location_pd[ self.location_pd["OBJEKTART"].isin(allowed)]
        self.plants_pd = pd.read_excel("Checklist_2017_simple_version_20230503.xlsx")
        #Only in the area of SG
        self.location_pd= self.location_pd.drop(columns=['OBJEKTART', 'OBJEKTKLASSE_TLM', 'EINWOHNERKATEGORIE', 'NAME_UUID', 'STATUS', 'SPRACHCODE', 'NAMEN_TYP', 'NAMENGRUPPE_UUID', 'ISCED'], axis=1)
        location_pd_2 = pd.read_csv("swissNAMES3D_PKT.csv", delimiter=";", low_memory=False)

        allowed = ["Pass", "Hauptgipfel", "Gipfel", "Huegel", "Haupthuegel", "Alpiner Gipfel", "Grotte, Hoehle"]
        location_pd_2 = location_pd_2[ location_pd_2["OBJEKTART"].isin(allowed)]
        location_pd_2= location_pd_2.drop(columns=['OBJEKTART', 'OBJEKTKLASSE_TLM', 'HOEHE', 'GEBAEUDENUTZUNG', 'NAME_UUID', 'STATUS', 'SPRACHCODE', 'NAMEN_TYP', 'NAMENGRUPPE_UUID'], axis=1)

        #This is the location database of the identifier
        self.location_pd = pd.concat([self.location_pd, location_pd_2], ignore_index=True)
        if only_SG:
            self.location_pd= self.location_pd[(self.location_pd['E'] > 2698440) & (self.location_pd['N'] > 1188486)]
        
        self.plant_names = self.plants_pd.Taxonname.values.tolist()
        self.location_names = self.location_pd.NAME.values.tolist()

        self.canton_dict = {
    1 : "ZH",
    2 : "BE",
    3 : "LU",
    4 : "UR",
    5 : "SZ",
    6 : "OW",
    7 : "NW",
    8 : "GL",
    9 : "ZG",
    10: "FR",
    11: "SO",
    12: "BS",
    13: "BL",
    14: "SH",
    15: "AR",
    16: "AI",
    17: "SG",
    18: "GR",
    19: "AG",
    20: "TG",
    21: "TI",
    22: "VD",
    23: "VS",
    24: "NE",
    25: "GE",
    26: "JU"
}     

    def identify(self, plant_name, location_name):
        """
        Finds the plantname (and it's id) as well as the location
        The return types are a bit wierd
        """
        try: 
            if len(location_name)>1:
                location_results = get_close_matches(location_name, self.location_names, n=9, cutoff=0.35)
            else:
                location_results = [""]
            if len(location_results)==0:
                location_results = [""]
            plant_result = get_close_matches(plant_name, self.plant_names, n=1, cutoff=0.01)
            if len(plant_result)==0:
                plant_result = [""]
            return [plant_result[0], self.plants_pd[self.plants_pd.Taxonname == plant_result[0]]["Nr. SISF"].values], location_results
        except Exception as e:
            print(f"An error occured, returning default values: {e}. Try writing the values by hand")
            return ["", [""]], [""]
    
    def get_location_metrics(self, location_name_identified):
        """
        Finds the coordinates to a given location
        Every element is in a list
        """
        try:
            E = self.location_pd[self.location_pd.NAME == location_name_identified]["E"].values
            N = self.location_pd[self.location_pd.NAME == location_name_identified]["N"].values
            height = self.location_pd[self.location_pd.NAME == location_name_identified]["Z"].values
            if len(E) == 0:
                E = np.append(E, "")
                N = np.append(N, "")
                height = np.append(height, "")
            return E, N, height
        except Exception as e:
            print(f"An error occured, returning default values: {e}. Try writing the values by hand")
            print(f"The prompt that caused this prolem is {location_name_identified}")
            return [""], [""], [""]
    
    def get_plant_id(self, plant_name):
        """
        Finds the plantID to a given ID 
                
        Every element is in a list
        """
        try:
            result =  self.plants_pd[self.plants_pd.Taxonname == plant_name]["Nr. SISF"].values
            if len(result)==0:
                return [""]
            return result
        except Exception as e:
            print(f"An error occured, returning default values: {e}. Try writing the values by hand")
            return [""]
    def get_closest_plant(self, plant_name):
        """
        Finds the closest plant to a given name
        Every element is in a list
        """
        try:
            result = get_close_matches(plant_name, self.plant_names, n=1, cutoff=0.01)
            if len(result)==0:
                return [""]
            return result
        
        except Exception as e:
            print(f"An error occured, returning default values: {e}. Try writing the values by hand")
            return [""]
    
    def get_close_plants(self, plant_name):
        """
        Returns the 5 nearest plants, deprecated
        """
        try:
            result =get_close_matches(plant_name, self.plant_names, n=5, cutoff=0.01)
            if len(result)==0:
                return [""]
            return result
        
        except Exception as e:
            print(f"An error occured, returning default values: {e}. Try writing the values by hand")
            return [""]
        
    def get_closest_location(self, location_name):
        """
        Gets the closest location to a name
        Return name is in a list
        """
        try: 
            result = get_close_matches(location_name, self.location_names, n=1, cutoff=0.01)
            if len(result)==0:
                return [""]
            return result
        except Exception as e:
            print(f"An error occured, returning default values: {e}. Try writing the values by hand")
            return [""]
    
    def get_closes_locations(self, location_name):
        """
        Gets the closest locations to a given name
        Return name is in a list, deprecated
        """
        try:
            result = get_close_matches(location_name, self.location_names, n=5, cutoff=0.01)
            if len(result)==0:
                return [""]
            return result
        except Exception as e:
            print(f"An error occured, returning default values: {e}. Try writing the values by hand")
            return [""]
    
    def get_gemeinde_region_canton(self, x, y):
        """
        Gets nearest community, canton, country given the coordinates.
        """
        try:
            if x== "" or y== "":
                return "", "", ""
            point = Point(x, y)  # Create a Shapely Point object
            for index, row in self.geo_data.iterrows():
                if row['geometry'].contains(point):
                
                    return row['name'], self.canton_dict[int(row["kantonsnummer"])], row['icc'] # Replace 'Canton' with the column containing canton names
            return "", "", ""
    
        except Exception as e:
            print(f"An error occured, returning default values: {e}. Try writing the values by hand")
            return "", "", ""

if __name__ == '__main__':
    identifier = Identifier()
    identifier.location_pd.to_csv(f"sg_locations.csv")
    