import os
import pandas as pd
import numpy as np
"""
Merges multiple wanda outputfiles together
"""
class Merger():
    def __init__(self, csv=False) -> None:
        self.csv = csv

    def merge(self, Path_to_folder):
        files = sorted(os.listdir(Path_to_folder))
        index_counter = 0
        whole_dataframe = 0
        for idx, f in enumerate(files):
            filepath = os.path.join(Path_to_folder, f)
            if self.csv:
                df = pd.read_csv(filepath, delimiter=";")
            else:
                df = pd.read_excel(filepath)

            if idx == 0:
                whole_dataframe = df
                index_counter += 25
                continue
                
            df['Kunzernummer'] = df["Kunzernummer"] + index_counter
            index_counter +=25
            whole_dataframe = pd.concat([whole_dataframe, df], ignore_index=True)
        whole_dataframe.to_excel(f"{Path_to_folder}/merged_output.xlsx", index=False)

def main():
    merger = Merger()
    merger.merge("Outputs/test")


if __name__ == '__main__':
    main()