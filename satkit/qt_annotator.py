#
# Copyright (c) 2019-2021 Pertti Palo, Scott Moisik, and Matthew Faytak.
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

# GUI functionality
from PyQt5.uic import loadUiType

# Plotting functions and hooks for GUI
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar)

# Local modules
from satkit.annotator import CurveAnnotator, PD_Annotator
from satkit.pd_annd_plot import plot_mpbpd, plot_pd, plot_pd_3d, plot_pd_vid, plot_wav, plot_wav_3D_ultra

# Load the GUI layout generated with QtDesigner.
Ui_MainWindow, QMainWindow = loadUiType('satkit/qt_annotator.ui')


class Qt_Annotator_Window(QMainWindow, Ui_MainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)

        self.setupUi(self)
        self.fig_dict = {}

        self.mplfigs.itemClicked.connect(self.changefig)

        self.fig = Figure()
        #
        # Graphs to be annotated and the waveform for reference.
        #
        gs = self.fig.add_gridspec(4, 7)
        self.ax1 = self.fig.add_subplot(gs[0:0+3, 0:0+6])
        self.ax3 = self.fig.add_subplot(gs[3:3+1, 0:0+6])
        # self.ax1 = fig.subplot2grid(
        #     self.subplot_grid, (0, 0),
        #     rowspan=3, colspan=6)
        # self.ax3 = fig.subplot2grid(self.subplot_grid, (3, 0), colspan=6)

        self.draw_plots()

        self.fig.align_ylabels()
        self.fig.canvas.mpl_connect('pick_event', self.onpick)

        self.addmpl(self.fig)

    # TODO: better names
    def changefig(self, item):
        text = item.text()
        self.rmmpl()
        self.addmpl(self.fig_dict[text])

    # TODO: better names
    def addfig(self, name, fig):
        self.fig_dict[name] = fig
        self.mplfigs.addItem(name)

    # TODO: better names
    def addmpl(self, fig):
        self.canvas = FigureCanvas(fig)
        self.mplWindowVerticalLayout.addWidget(self.canvas)
        self.canvas.draw()
        self.toolbar = NavigationToolbar(self.canvas,
                                         self, coordinates=True)
        self.addToolBar(self.toolbar)

    # TODO: better names
    def rmmpl(self):
        self.mplWindowVerticalLayout.removeWidget(self.canvas)
        self.canvas.close()
        self.mplWindowVerticalLayout.removeWidget(self.toolbar)
        self.toolbar.close()


# TODO: PD_Annotator needs to be agnostic about which implementation it follows.
class PD_Qt_Annotator(PD_Annotator):
    def __init__(self, recordings, args):
        super().__init__(self, recordings, args)

        self.qtWindow = Qt_Annotator_Window()

    @property
    def default_annotations(self):
        return {
            'pdCategory': len(self.categories)-1,
            'pdOnset': -1.0,
        }

    def draw_plots(self):
        """
        Updates title and graphs. Called by self.update().
        """
        self.ax1.set_title(self._get_title())
        self.ax1.axes.xaxis.set_ticklabels([])

        audio = self.current.modalities['MonoAudio']
        stimulus_onset = audio.meta['stimulus_onset']
        wav = audio.data
        wav_time = audio.timevector

        pd = self.current.modalities['PD on ThreeD_Ultrasound']
        ultra_time = pd.timevector - pd.timevector[-1] + wav_time[-1]

        self.xlim = [ultra_time[0] - 0.05, ultra_time[-1]+0.05]

        textgrid = self.current.textgrid

        plot_pd_3d(
            self.ax1, pd.data['pd'],
            ultra_time, self.xlim, textgrid, stimulus_onset,
            picker=CurveAnnotator.line_xdirection_picker)
        plot_wav_3D_ultra(self.ax3, wav, wav_time, self.xlim,
                          textgrid, stimulus_onset)

        if self.current.annotations['pdOffset'] > -1:
            self.ax1.axvline(x=self.current.annotations['pdOffset'],
                             linestyle=':', color="deepskyblue", lw=1)
            self.ax3.axvline(x=self.current.annotations['pdOffset'],
                             linestyle=':', color="deepskyblue", lw=1)