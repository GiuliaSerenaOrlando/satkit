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

from pathlib import Path

import numpy as np
import satkit.audio_processing as satkit_audio
# wav file handling
import scipy.io.wavfile as sio_wavfile
from satkit.data_structures import ModalityData


# TODO: break into two different functions: one that runs beep detection and one that doesn't.
def read_wav(path: Path, detect_beep: bool=False) -> ModalityData:
    """
    Read wavfile from path.

    Positional argument:
    path -- Path of the wav file

    Keyword argument:
    detect_beep -- Should 1kHz beep detection be run. Changes return values (see below).

    Returns a ModalityData instance that contains the wav frames, a timevector, and
    the sampling rate. 

    Also returns the time of a 1kHz go-signal and a guess about if the file contains 
    speech if detect_beep = True.
    """
    (wav_fs, wav_frames) = sio_wavfile.read(path)

    timevector = np.linspace(0, len(wav_frames),
                                    len(wav_frames),
                                    endpoint=False)
    timevector = timevector/wav_fs
    data = ModalityData(wav_frames, wav_fs, timevector)

    if detect_beep:
        # use a high-pass filter for removing the mains frequency (and anything below it)
        # from the recorded sound.
        go_signal, has_speech = satkit_audio.detect_beep_and_speech(
            wav_frames, 
            wav_fs, 
            satkit_audio.MainsFilter.mains_filter['b'],
            satkit_audio.MainsFilter.mains_filter['a'],
            path
        )

        return data, go_signal, has_speech
    else:
        return data
