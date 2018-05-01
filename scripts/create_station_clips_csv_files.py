"""
Script that extracts clip center index, center frequency, and classification
information from BirdVox-70k dataset HDF5 files and writes it to CSV files.
"""


import csv

import h5py

import vesper_birdvox.utils as utils


def main():
    
    for unit_num in utils.UNIT_NUMS:

        hdf5_file_path = utils.get_unit_hdf5_file_path(unit_num)
        csv_file_path = utils.get_station_clips_csv_file_path(unit_num)
        
        with h5py.File(hdf5_file_path, 'r') as hdf5_file:
            
            group = hdf5_file['waveforms']
            
            with open(csv_file_path, 'w') as csv_file:
            
                writer = csv.writer(csv_file)
                
                writer.writerow(
                    ['Center Index', 'Center Frequency (Hz)'])
                
                for key in group.keys():
                    _, index, freq, _ = key.split('_')
                    writer.writerow([int(index), int(freq)])
                
    
if __name__ == '__main__':
    main()
