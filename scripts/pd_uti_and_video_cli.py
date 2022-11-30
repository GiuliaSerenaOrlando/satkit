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
import time

# local modules
from satkit.commandLineInterface import RawAndVideoCLI
from satkit.data_import.AAA_video import Video
from satkit.metrics import pd
from satkit.recording import RawUltrasound

# how do we tell RawAndVideoCLI or RawCLI to run pd (and others) on all modalities. ie. how do we bind an operation to a modality?
# answer: we hack it for now and document we've hacked it.


def main():
    # Run the command line interface.
    function_dict = {'PD': (pd.add_pd, [RawUltrasound, Video])}
    RawAndVideoCLI(
        "PD processing script for raw ultrasound and videos", function_dict)


if (__name__ == '__main__'):
    t = time.time()
    main()
    elapsed_time = time.time() - t
    logging.info('Elapsed time ' + str(elapsed_time))