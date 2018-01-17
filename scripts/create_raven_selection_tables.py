"""
Creates Raven selection tables from the BirdVox-70k annotation CSV files.
"""


import csv
import os

import vesper_birdvox.utils as utils


SELECTIONS_DIR_PATH = utils.BIRDVOX_DIR_PATH / 'BirdVox-70k_selections'
SELECTIONS_FILE_NAME_FORMAT = 'BirdVox-70k_selections_unit{:02d}.txt'
SELECTIONS_HEADER = (
    'Selection', 'View', 'Channel', 'Begin Time (s)', 'End Time (s)',
    'Low Freq (Hz)', 'High Freq (Hz)', 'Annotation')


def main():
    for unit_num in utils.UNIT_NUMS:
        create_selection_table(unit_num)
        
        
def create_selection_table(unit_num):
            
    annotations_file_path = utils.get_annotations_file_path(unit_num)
    
    selections_file_name = SELECTIONS_FILE_NAME_FORMAT.format(unit_num)
    selections_file_path = SELECTIONS_DIR_PATH / selections_file_name
    
    os.makedirs(str(SELECTIONS_DIR_PATH), exist_ok=True)
    
    with open(str(annotations_file_path)) as annotations_file:
        
        reader = csv.reader(annotations_file)
        
        # Skip input header.
        next(reader)
            
        with open(str(selections_file_path), 'w') as selections_file:
            
            writer = csv.writer(selections_file, delimiter='\t')
            
            writer.writerow(SELECTIONS_HEADER)
            
            for i, row in enumerate(reader):
                
                _, center_time, center_freq, annotation = row
                
                selection_num = str(i + 1)
                
                writer.writerow((
                    selection_num, 'Waveform 1', '1',
                    center_time, center_time,
                    center_freq, center_freq,
                    annotation))
        
                writer.writerow((
                    selection_num, 'Spectrogram 1', '1',
                    center_time, center_time,
                    center_freq, center_freq,
                    annotation))
    
    
if __name__ == '__main__':
    main()
