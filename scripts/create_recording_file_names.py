"""Creates BirdVox-70k recording file names for a Vesper archive."""


import datetime


TIMESTAMPS = {
    1: 1443065462,
    2: 1443065464,
    3: 1443065462,
    5: 1443065462,
    7: 1443065463,
    10: 1443075217,
}


def main():
    
    for unit_num, timestamp in sorted(TIMESTAMPS.items()):
        dt = datetime.datetime.fromtimestamp(timestamp)
        formatted_dt = dt.strftime('%Y-%m-%d_%H.%M.%S')
        print('Station {:02d}_{}_Z'.format(unit_num, formatted_dt))
        

if __name__ == '__main__':
    main()
