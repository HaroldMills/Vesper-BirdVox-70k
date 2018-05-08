"""Constants and functions for use by Vesper-BirdVox-70k scripts."""


from pathlib import Path
import csv


UNIT_NUMS = (1, 2, 3, 5, 7, 10)

SAMPLE_RATE = 24000

BIRDVOX_DIR_PATH = Path('/Users/harold/Desktop/NFC/Data/BirdVox')
BIRDVOX_70K_DATASET_DIR_PATH = BIRDVOX_DIR_PATH / 'BirdVox-70k Dataset'
BIRDVOX_70K_OTHER_DIR_PATH = BIRDVOX_DIR_PATH / 'BirdVox-70k Other'
BIRDVOX_FULL_NIGHT_DATASET_DIR_PATH = \
    BIRDVOX_DIR_PATH / 'BirdVox-full-night Dataset'
BIRDVOX_70K_UNIT_HDF5_FILE_NAME_FORMAT = 'BirdVox-70k_unit{:02d}.hdf5'
UNIT_CLIPS_CSV_DIR_PATH = BIRDVOX_70K_OTHER_DIR_PATH / 'Unit Clips CSV Files'
UNIT_CLIPS_CSV_FILE_NAME_FORMAT = 'Unit {:02d} Clips.csv'
RAVEN_SELECTION_TABLES_DIR_PATH = \
    BIRDVOX_70K_OTHER_DIR_PATH / 'Raven Selection Tables'
RAVEN_SELECTION_TABLE_FILE_NAME_FORMAT = 'Unit {:02d} Selections.txt'

# Call center frequency threshold separating "Call.Low" and "Call.High"
# classifications. The BirdVox-70k data set has only a call category,
# not low- and high-frequency categories, but we find the additional
# categories useful since they correspond approximately to the familiar
# thrush and tseep categories. We chose the threshold value by visual
# inspection of the call center frequency histogram plotted by the
# `plot_center_frequency_histogram` script of this package. The
# threshold is also consistent with traditional conceptions of the
# thrush and tseep frequency ranges.
FREQ_THRESHOLD = 5000    # hertz


def get_unit_hdf5_file_path(unit_num):
    file_name = BIRDVOX_70K_UNIT_HDF5_FILE_NAME_FORMAT.format(unit_num)
    return BIRDVOX_70K_DATASET_DIR_PATH / file_name


def get_unit_clips_csv_file_path(unit_num):
    file_name = UNIT_CLIPS_CSV_FILE_NAME_FORMAT.format(unit_num)
    return UNIT_CLIPS_CSV_DIR_PATH / file_name


def get_raven_selection_table_file_path(unit_num):
    file_name = RAVEN_SELECTION_TABLE_FILE_NAME_FORMAT.format(unit_num)
    return RAVEN_SELECTION_TABLES_DIR_PATH / file_name


def get_unit_clip_infos(unit_num):
    file_path = get_unit_clips_csv_file_path(unit_num)
    with open(file_path) as file_:
        reader = csv.reader(file_)
        next(reader)   # skip header
        return [(int(r[0]), int(r[1])) for r in reader]


def get_classification(center_freq):
    return 'Call.High' if center_freq >= FREQ_THRESHOLD else 'Call.Low'
