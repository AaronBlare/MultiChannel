import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore
from PyQt5.QtWidgets import QApplication, QDialog, QVBoxLayout, QGroupBox, QGridLayout
import numpy as np
import sys


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


def initUI(app, data, time):
    createGridLayout(app, data, time)
    app.resize(2000, 800)

    windowLayout = QVBoxLayout()
    windowLayout.addWidget(app.horizontalGroupBox)
    app.setLayout(windowLayout)

    app.show()


def createGridLayout(app, data, time):
    app.horizontalGroupBox = QGroupBox()
    layout = QGridLayout()

    num_rows = 12
    num_columns = 5

    plots = []

    for row_id in range(0, num_rows):
        layout.setColumnStretch(row_id, num_columns)

    for col_id in range(0, num_columns):
        for row_id in range(0, num_rows):
            curr_id = col_id * num_rows + row_id
            curr_plot = pg.PlotWidget(title='#' + str(curr_id + 1))
            curr_plot.enableAutoRange(False, False)
            curr_plot.setXRange(0, 500)
            curve = HDF5Plot()
            curve.setHDF5(data[:, curr_id])
            curr_plot.addItem(curve)
            layout.addWidget(curr_plot, col_id, row_id)
            plots.append(curr_plot)
            if curr_id > 0:
                plots[curr_id - 1].getViewBox().setXLink(plots[curr_id])
                plots[curr_id - 1].getViewBox().setYLink(plots[curr_id])

    app.horizontalGroupBox.setLayout(layout)


class App(QDialog):

    def __init__(self):
        super().__init__()


def plot_all_signals(data, time):
    if sys.flags.interactive != 1 or not hasattr(QtCore, 'PYQT_VERSION'):
        app = QApplication(sys.argv)
        ex = App()
        initUI(ex, data, time)
        sys.exit(app.exec_())
