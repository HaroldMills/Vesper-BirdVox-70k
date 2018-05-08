"""
Plots a histogram of the center frequencies of the BirdVox-70k flight calls.
"""


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
    data = utils.get_unit_clip_data(unit_num)
    return [freq for _, freq in data if freq != 0]


if __name__ == '__main__':
    main()
