"""
Creates BirdVox-70k call clips in a Vesper archive.

This script must be run from the archive directory.
"""


import datetime
import os
import sys

import numpy as np

import vesper.util.signal_utils as signal_utils
import vesper.util.time_utils as time_utils
import vesper_birdvox.utils as utils


# Set up Django.
os.environ['DJANGO_SETTINGS_MODULE'] = 'vesper.django.project.settings'
import django
django.setup()

from django.db.utils import IntegrityError

from vesper.django.app.models import (
    AnnotationInfo, Clip, Processor, Recording, StringAnnotation, User)


# Duration of clips added to the archive. The BirdVox-70k data set
# provides the center time and frequency of each call, but no duration
# information. We extract clips of duration `CLIP_DURATION` centered
# at the indicated center times.
CLIP_DURATION = .400      # seconds

WAVE_SAMPLE_DTYPE = np.dtype('<i2')


def main():
    
    center_index_info = AnnotationInfo.objects.get(name='Call Center Index')
    center_freq_info = AnnotationInfo.objects.get(name='Call Center Freq')
    classification_info = AnnotationInfo.objects.get(name='Classification')
    annotation_user = User.objects.get(username='Vesper')
    
    for recording in Recording.objects.all():
        
        print('processing recording {}...'.format(str(recording)))
        
        # Get field values that are the same for all clips of this recording.
        station = recording.station
        recording_channel = recording.channels.get()
        mic_output = recording_channel.mic_output
        sample_rate = recording.sample_rate
        length = int(round(CLIP_DURATION * sample_rate))
        night = station.get_night(recording.start_time)
        detector = Processor.objects.get(name='BirdVox-70k')
        
        clip_data = get_recording_clip_data(recording)
        
        center_indices = set()

        for center_index, center_freq in clip_data:
            
            # Some call center indices in the input data are
            # duplicates, so that clip start indices computed
            # from them violate a Vesper archive database
            # uniqueness constraint. We bump duplicate indices
            # by one until they are unique to resolve the issue.
            while center_index in center_indices:
                center_index += 1
            center_indices.add(center_index)

            start_index = center_index - length // 2
            start_offset = start_index / sample_rate
            start_time_delta = datetime.timedelta(seconds=start_offset)
            start_time = recording.start_time + start_time_delta
            
            end_time = signal_utils.get_end_time(
                start_time, length, sample_rate)
            
            creation_time = time_utils.get_utc_now()
            
            try:
                
                clip = Clip.objects.create(
                    station=station,
                    mic_output=mic_output,
                    recording_channel=recording_channel,
                    start_index=start_index,
                    length=length,
                    sample_rate=sample_rate,
                    start_time=start_time,
                    end_time=end_time,
                    date=night,
                    creation_time=creation_time,
                    creating_processor=detector)
                
            except IntegrityError:
                
                print((
                    'Duplicate clip with center index {}. '
                    'Clip will be ignored.').format(center_index),
                    file=sys.stderr)
                
            else:
                
                # Add classification annotation.
                classification = get_classification(center_freq)
                StringAnnotation.objects.create(
                    clip=clip,
                    info=classification_info,
                    value=classification,
                    creation_time=creation_time,
                    creating_user=annotation_user)
                
                if classification.startswith('Call.'):
                    
                    # Add center time annotation.
                    StringAnnotation.objects.create(
                        clip=clip,
                        info=center_index_info,
                        value=str(center_index),
                        creation_time=creation_time,
                        creating_user=annotation_user)
                   
                    # Add center frequency annotation.
                    StringAnnotation.objects.create(
                        clip=clip,
                        info=center_freq_info,
                        value=str(center_freq),
                        creation_time=creation_time,
                        creating_user=annotation_user)
                
                
def get_recording_clip_data(recording):
    station_num = int(recording.station.name.split()[-1])
    return utils.get_unit_clip_data(station_num)
    
    
def get_classification(center_freq):
    if center_freq == 0:
        return 'Noise'
    elif center_freq < utils.FREQ_THRESHOLD:
        return 'Call.Low'
    else:
        return 'Call.High'
    
    
if __name__ == '__main__':
    main()
