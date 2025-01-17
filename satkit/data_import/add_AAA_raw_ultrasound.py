#
# Copyright (c) 2019-2022 Pertti Palo, Scott Moisik, Matthew Faytak, and Motoki Saito.
#
# This file is part of Speech Articulation ToolKIT 
# (see https://github.com/giuthas/satkit/).
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
# The example data packaged with this program is licensed under the
# Creative Commons Attribution-NonCommercial-ShareAlike 4.0
# International (CC BY-NC-SA 4.0) License. You should have received a
# copy of the Creative Commons Attribution-NonCommercial-ShareAlike 4.0
# International (CC BY-NC-SA 4.0) License along with the data. If not,
# see <https://creativecommons.org/licenses/by-nc-sa/4.0/> for details.
#
# When using the toolkit for scientific publications, please cite the
# articles listed in README.markdown. They can also be found in
# citations.bib in BibTeX format.
#
import logging
from contextlib import closing
from datetime import datetime
from math import inf
from pathlib import Path
from typing import Optional, Union

from satkit.data_structures import ModalityData, Recording, RecordingMetaData
from satkit.modalities import RawUltrasound

_AAA_raw_ultrsound_logger = logging.getLogger('satkit.AAA_raw_ultrasound')


def parse_aaa_promptfile(filepath: Union[str, Path]) -> dict:
    """
    Read an AAA .txt (not US.txt or .param) file and save prompt, 
    recording date and time, and participant name into the meta dictionary.
    """
    if isinstance(filepath, str):
        filepath = Path(filepath)

    with closing(open(filepath, 'r', encoding="utf8")) as promptfile:
        lines = promptfile.read().splitlines()
        prompt = lines[0]

        # The date used to be just a string, but needs to be more sturctured since
        # the spline export files have a different date format.
        time_of_recording = datetime.strptime(
            lines[1], '%d/%m/%Y %H:%M:%S')

        if len(lines) > 2 and lines[2].strip():
            participant_id = lines[2].split(',')[0]
        else:
            _AAA_raw_ultrsound_logger.info(
                "Participant does not have an id in file %s.", filepath)
            participant_id = ""

        meta = RecordingMetaData(prompt, time_of_recording, participant_id)
        _AAA_raw_ultrsound_logger.debug("Read prompt file %s.", filepath)
    return meta

def parse_ultrasound_meta_aaa(filename):
    """
    Parse metadata from an AAA export file into a dictionary.

    This is either a 'US.txt' or a '.param' file. They have
    the same format.

    Arguments:
    filename -- path and name of file to be parsed.

    Returns a dictionary which should contain the following keys:
        NumVectors -- number of scanlines in a frame
        PixPerVector -- number of pixels in a scanline
        ZeroOffset --
        BitsPerPixel -- byte length of a single pixel in the .ult file
        Angle -- angle in radians between two scanlines
        Kind -- type of probe used
        PixelsPerMm -- depth resolution of a scanline
        FramesPerSec -- framerate of ultrasound recording
        TimeInSecsOfFirstFrame -- time from recording start to first frame
    """
    meta = {}
    with closing(open(filename, 'r', encoding="utf8")) as metafile:
        for line in metafile:
            (key, value_str) = line.split("=")
            try:
                value = int(value_str)
            except ValueError:
                value = float(value_str)
            meta[key] = value

        _AAA_raw_ultrsound_logger.debug(
            "Read and parsed ultrasound metafile %s.", filename)
        meta['meta_file'] = filename
    return meta


def add_aaa_raw_ultrasound(recording: Recording, preload: bool,
                            path: Optional[Path]=None) -> None:
    """Create a RawUltrasound Modality and add it to the Recording."""
    if not path:
        ult_file = (recording.path/recording.basename).with_suffix(".ult")
        meta_file = (recording.path/(recording.basename+"US.txt"))
    else:
        ult_file = path
        meta_file = path.with_suffix("US.txt")

    ult_time_offset = -inf
    if meta_file.is_file():
        meta = parse_ultrasound_meta_aaa(meta_file)
        # We pop the timeoffset from the meta dict so that people will not
        # accidentally rely on setting that to alter the timeoffset of the
        # ultrasound data in the Recording. This throws KeyError if the meta
        # file didn't contain TimeInSecsOfFirstFrame.
        ult_time_offset = meta.pop('TimeInSecsOfFirstFrame')
    else:
        if not path:
            meta_file = (recording.path/(recording.basename+".param"))
        else:
            meta_file = path.with_suffix(".param")

    if meta_file.is_file():
        meta = parse_ultrasound_meta_aaa(meta_file)
        # We pop the timeoffset from the meta dict so that people will not
        # accidentally rely on setting that to alter the timeoffset of the
        # ultrasound data in the Recording. This throws KeyError if the meta
        # file didn't contain TimeInSecsOfFirstFrame.
        ult_time_offset = meta.pop('TimeInSecsOfFirstFrame')
    else:
        notice = 'Note: ' + str(meta_file) + " does not exist. Excluding."
        _AAA_raw_ultrsound_logger.warning(notice)
        recording.exclude()

    _AAA_raw_ultrsound_logger.debug(
            "Trying to read RawUltrasound for Recording representing %s.",
            recording.basename)
    
    if ult_file.is_file():
        if preload:
            raise NotImplementedError("It looks like SATKIT is trying " 
                + "to preload ultrasound data. This may lead to Python's " 
                + "memory running out or the whole computer crashing.")
        else:
            ultrasound = RawUltrasound(
                recording=recording,
                data_path=ult_file,
                time_offset=ult_time_offset,
                meta=meta
            )
            recording.add_modality(ultrasound)

        _AAA_raw_ultrsound_logger.debug(
            "Added RawUltrasound to Recording representing %s.",
            recording.basename)
    else:
        notice = 'Note: ' + str(ult_file) + " does not exist. Excluding."
        _AAA_raw_ultrsound_logger.warning(notice)
        recording.exclude()

