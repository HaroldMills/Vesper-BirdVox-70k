"""
Creates Raven selection tables from the BirdVox-70k annotation CSV files.
"""


import csv

import vesper_birdvox.utils as utils


SELECTION_TABLE_HEADER = (
    'Selection', 'View', 'Channel', 'Begin Time (s)', 'End Time (s)',
    'Low Freq (Hz)', 'High Freq (Hz)', 'Annotation')


def main():
    for unit_num in utils.UNIT_NUMS:
        create_selection_table(unit_num)
        
        
def create_selection_table(unit_num):
            
    clip_data = utils.get_unit_clip_data(unit_num)
    
    file_path = utils.get_raven_selection_table_file_path(unit_num)
    
    with open(str(file_path), 'w') as file_:
        
        writer = csv.writer(file_, delimiter='\t')
        
        writer.writerow(SELECTION_TABLE_HEADER)
        
        for i, (center_index, center_freq) in enumerate(clip_data):
            
            if center_freq != 0:
                
                center_time = center_index / utils.SAMPLE_RATE
                classification = utils.get_classification(center_freq)
                
                selection_num = str(i + 1)
                
                writer.writerow((
                    selection_num, 'Waveform 1', '1',
                    center_time, center_time,
                    center_freq, center_freq,
                    classification))
        
                writer.writerow((
                    selection_num, 'Spectrogram 1', '1',
                    center_time, center_time,
                    center_freq, center_freq,
                    classification))
    
    
if __name__ == '__main__':
    main()
