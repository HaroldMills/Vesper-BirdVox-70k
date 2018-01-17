"""Constants and functions for use by Vesper-BirdVox-70k scripts."""


from pathlib import Path


UNIT_NUMS = (1, 2, 3, 5, 7, 10)
BIRDVOX_DIR_PATH = Path(
    '/Users/harold/Desktop/NFC/Data/BirdVox/BirdVox-70k/'
    'BirdVox-70k_full-nights')
ANNOTATIONS_DIR_PATH = BIRDVOX_DIR_PATH / 'BirdVox-70k_annotations'
ANNOTATIONS_FILE_NAME_FORMAT = 'BirdVox-70k_annotations_unit{:02d}.csv'
ANNOTATION_CALL = 'flight call'


def get_annotations_file_path(unit_num):
    file_name = ANNOTATIONS_FILE_NAME_FORMAT.format(unit_num)
    return ANNOTATIONS_DIR_PATH / file_name
