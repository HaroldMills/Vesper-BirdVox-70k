"""
Plots a histogram of the center frequencies of the BirdVox-70k flight calls.
"""


import csv
import itertools

import matplotlib.pyplot as plt
import numpy as np

import vesper_birdvox.utils as utils


def main():
    
    freq_lists = [get_call_center_freqs(n) for n in utils.UNIT_NUMS]
    freqs = np.array(list(itertools.chain(*freq_lists)))
    
    plt.hist(freqs, 100)
    plt.xlabel('Center Frequency (Hz)')
    plt.ylabel('Number of Calls')
    plt.title('Histogram of BirdVox-70k Call Center Frequencies')
    plt.grid(True)
    plt.show()
    
    
def get_call_center_freqs(unit_num):
    
    annotations_file_path = utils.get_annotations_file_path(unit_num)
    
    with open(str(annotations_file_path)) as annotations_file:
        
        reader = csv.reader(annotations_file)
        
        # Skip input header.
        next(reader)
            
        return [float(r[2]) for r in reader if r[3] == utils.ANNOTATION_CALL]
    

if __name__ == '__main__':
    main()
