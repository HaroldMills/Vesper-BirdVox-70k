import h5py
import numpy as np

import vesper_birdvox.utils as utils


def main():
    
    print('Unit,Min Sample,Max Sample')
    
    for unit_num in utils.UNIT_NUMS:
        
        file_path = utils.get_unit_hdf5_file_path(unit_num)
        
        with h5py.File(file_path, 'r') as file_:
            
            group = file_['waveforms']
            
            overall_min = 0
            overall_max = 0
            
            for dataset in group.values():
                
                samples = dataset[...]
                
                min_ = np.min(samples)
                max_ = np.max(samples)
                
                if min_ < overall_min:
                    overall_min = min_
                    
                if max_ > overall_max:
                    overall_max = max_
                    
            print('{},{},{}'.format(unit_num, overall_min, overall_max))
    
    
if __name__ == '__main__':
    main()
