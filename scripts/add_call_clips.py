"""
Extracts BirdVox-70k call clips from recordings and adds them to a Vesper
archive.

This script must be run from the archive directory.
"""


from pathlib import Path
import csv
import datetime
import os
import sys
import wave

# Set up Django.
os.environ['DJANGO_SETTINGS_MODULE'] = 'vesper.django.project.settings'
import django
django.setup()

from django.db.utils import IntegrityError
import numpy as np

from vesper.django.app.models import (
    AnnotationInfo, Clip, Processor, Recording, StringAnnotation, User)
import vesper.util.audio_file_utils as audio_file_utils
import vesper.util.signal_utils as signal_utils
import vesper.util.time_utils as time_utils
import vesper_birdvox.utils as utils


# Call center frequency threshold separating "Call.Low" and "Call.High"
# classifications. The BirdVox-70k data set has only a "flight call"
# category, not low- and high-frequency categories, but we find those
# additional categories useful since they correspond approximately to
# the familiar thrush and tseep categories. We chose the threshold value
# by visual inspection of the call center frequency histogram plotted by
# the `plot_center_frequency_histogram` script of this package. The
# threshold is also consistent with traditional conceptions of the
# thrush and tseep frequency ranges.
FREQ_THRESHOLD = 5000    # hertz

# Duration of clips extracted from continuous recordings. The BirdVox-70k
# data set provides the center time and frequency of each call, but no
# duration information. We extract clips of duration `CLIP_DURATION`
# centered at the indicated center times.
CLIP_DURATION = .5       # seconds

WAVE_SAMPLE_DTYPE = np.dtype('<i2')


def main():
    
    center_info = AnnotationInfo.objects.get(name='Call Center')
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
        detector = Processor.objects.get(name='Andrew Farnsworth')
        
        call_centers = get_call_centers(recording)
        
        recording_file_path = get_recording_file_path(recording)
        
        with wave.open(str(recording_file_path), 'rb') \
                as recording_file_reader:
            
            sample_period = 1 / sample_rate
            existing_times = set()
            
            for time, freq in call_centers:
                
                # Some call center times in the input data are duplicates,
                # which violates a Vesper archive database uniqueness
                # constraint. We bump duplicate times by one sample period
                # until they are unique to resolve the issue.
                while time in existing_times:
                    time += sample_period
                existing_times.add(time)
                    
                start_offset = time - CLIP_DURATION / 2
                start_index = \
                    signal_utils.seconds_to_frames(start_offset, sample_rate)
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
                        'Duplicate clip with center time {}. '
                        'Clip will be ignored.').format(time),
                        file=sys.stderr)
                    
                else:
                    
                    # Add center annotation.
                    center_json = get_center_json(recording, time, freq)
                    StringAnnotation.objects.create(
                        clip=clip,
                        info=center_info,
                        value=center_json,
                        creation_time=creation_time,
                        creating_user=annotation_user)
                    
                    # Add classification annotation.
                    classification = get_classification(freq)
                    StringAnnotation.objects.create(
                        clip=clip,
                        info=classification_info,
                        value=classification,
                        creation_time=creation_time,
                        creating_user=annotation_user)
                    
                    create_clip_audio_file(clip, recording_file_reader)
                
                
def get_call_centers(recording):
    annotations_file_path = get_annotations_file_path(recording)
    with open(str(annotations_file_path)) as annotations_file:
        reader = csv.reader(annotations_file)
        return [
            (float(r[1]), float(r[2]))
            for r in reader
            if r[3] == 'flight call']


def get_annotations_file_path(recording):
    unit_num = int(recording.station.name.split()[-1])
    return utils.get_annotations_file_path(unit_num)
    

def get_recording_file_path(recording):
    # We assume here that a recording comprises a single file.
    return Path(recording.files.get().path)
                
    
def get_center_json(recording, time, freq):
    delta = datetime.timedelta(seconds=time)
    dt = recording.start_time + delta
    time_string = format_datetime(dt)
    freq_string = format_freq(freq)
    return '{{"time": "{}", "freq": {}}}'.format(time_string, freq_string)


def format_datetime(dt):
    if dt.microsecond == 0:
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    else:
        return dt.strftime('%Y-%m-%d %H:%M:%S.%f').rstrip('0')
    
    
def format_freq(freq):
    return '{:g}'.format(freq)

    
def get_classification(freq):
    return 'Call.High' if freq >= FREQ_THRESHOLD else 'Call.Low'
    
    
def create_clip_audio_file(clip, recording_file_reader):
    clip_samples = get_recording_samples(
        recording_file_reader, clip.start_index, clip.length)
    audio_file_path = Path(clip.wav_file_path)
    audio_file_path.parent.mkdir(parents=True, exist_ok=True)
    audio_file_utils.write_wave_file(
        str(audio_file_path), clip_samples, clip.sample_rate)


def get_recording_samples(recording_file_reader, start_index, length):
    recording_file_reader.setpos(start_index)
    bytes_ = recording_file_reader.readframes(length)
    samples = np.frombuffer(bytes_, dtype=WAVE_SAMPLE_DTYPE)
    samples = samples.reshape((1, length))
    return samples
    
        
if __name__ == '__main__':
    main()
