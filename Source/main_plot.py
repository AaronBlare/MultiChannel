from Source.functions.file_system import get_path
from Source.functions.read_h5 import read_h5_file
from Source.functions.plot_signal_mpl import plot_all_signals
import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore
from PyQt5.QtWidgets import QApplication, QDialog, QVBoxLayout, QGroupBox, QGridLayout
import numpy as np


path = get_path()
data_path = path + '/Data/'
data_filename = '2020-10-16T13-28-55H3Do.h5'

data, time = read_h5_file(data_path + data_filename)

# plot_all_signals(data, time)


class HDF5Plot(pg.PlotCurveItem):
    def __init__(self, *args, **kwds):
        self.hdf5 = None
        self.limit = 10000  # maximum number of samples to be plotted
        pg.PlotCurveItem.__init__(self, *args, **kwds)

    def setHDF5(self, data):
        self.hdf5 = data
        self.updateHDF5Plot()

    def viewRangeChanged(self):
        self.updateHDF5Plot()

    def updateHDF5Plot(self):
        if self.hdf5 is None:
            self.setData([])
            return

        vb = self.getViewBox()
        if vb is None:
            return  # no ViewBox yet

        # Determine what data range must be read from HDF5
        xrange = vb.viewRange()[0]
        start = max(0, int(xrange[0]) - 1)
        stop = min(len(self.hdf5), int(xrange[1] + 2))

        # Decide by how much we should downsample
        ds = int((stop - start) / self.limit) + 1

        if ds == 1:
            # Small enough to display with no intervention.
            visible = self.hdf5[start:stop]
            scale = 1
        else:
            # Here convert data into a down-sampled array suitable for visualizing.
            # Must do this piecewise to limit memory usage.
            samples = 1 + ((stop - start) // ds)
            visible = np.zeros(samples * 2, dtype=self.hdf5.dtype)
            sourcePtr = start
            targetPtr = 0

            # read data in chunks of ~1M samples
            chunkSize = (1000000 // ds) * ds
            while sourcePtr < stop - 1:
                chunk = self.hdf5[sourcePtr:min(stop, sourcePtr + chunkSize)]
                sourcePtr += len(chunk)

                # reshape chunk to be integral multiple of ds
                chunk = chunk[:(len(chunk) // ds) * ds].reshape(len(chunk) // ds, ds)

                # compute max and min
                chunkMax = chunk.max(axis=1)
                chunkMin = chunk.min(axis=1)

                # interleave min and max into plot data to preserve envelope shape
                visible[targetPtr:targetPtr + chunk.shape[0] * 2:2] = chunkMin
                visible[1 + targetPtr:1 + targetPtr + chunk.shape[0] * 2:2] = chunkMax
                targetPtr += chunk.shape[0] * 2

            visible = visible[:targetPtr]
            scale = ds * 0.5

        self.setData(visible)  # update the plot
        self.setPos(start, 0)  # shift to match starting index
        self.resetTransform()
        self.scale(scale, 1)  # scale to match downsampling


class App(QDialog):

    def __init__(self):
        super().__init__()
        self.title = 'PyQt5 layout - pythonspot.com'
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)

        self.createGridLayout()

        windowLayout = QVBoxLayout()
        windowLayout.addWidget(self.horizontalGroupBox)
        self.setLayout(windowLayout)

        self.show()

    def createGridLayout(self):
        self.horizontalGroupBox = QGroupBox("Grid")
        layout = QGridLayout()
        layout.setColumnStretch(1, 4)

        Plot_Top = pg.plot()
        Plot_Top.win.hide()
        Plot_Top.enableAutoRange(False, False)
        Plot_Top.setXRange(0, 500)
        curve = HDF5Plot()
        curve.setHDF5(data[:, 0])
        Plot_Top.addItem(curve)

        layout.addWidget(Plot_Top, 0, 0)

        Plot_Bot = pg.plot()
        Plot_Bot.win.hide()
        Plot_Bot.enableAutoRange(False, False)
        Plot_Bot.setXRange(0, 500)
        curve2 = HDF5Plot()
        curve2.setHDF5(data[:, 1])
        Plot_Bot.addItem(curve2)

        Plot_Top.getViewBox().setXLink(Plot_Bot)
        Plot_Top.getViewBox().setYLink(Plot_Bot)

        layout.addWidget(Plot_Bot, 0, 1)

        self.horizontalGroupBox.setLayout(layout)


if __name__ == '__main__':
    import sys
    if sys.flags.interactive != 1 or not hasattr(QtCore, 'PYQT_VERSION'):
        app = QApplication(sys.argv)
        ex = App()
        sys.exit(app.exec_())
