import numpy
from PySide import QtGui, QtCore

TOP_MARGIN = 20
RIGHT_MARGIN = 20
LEFT_AXIS_WIDTH = 70
BOTTOM_AXIS_HEIGHT = 40
AXIS_THICKNESS = 1

DBM_TOP = 20
DBM_BOTTOM = -120

class SpectrumView(QtGui.QWidget):
    """
    A complete spectrum view with left/bottom axis and plot
    """

    def __init__(self, powdata, center_freq):
        super(SpectrumView, self).__init__()
        self.plot = SpectrumViewPlot(powdata, center_freq)
        self.left = SpectrumViewLeftAxis()
        self.bottom = SpectrumViewBottomAxis()
        self.bottom.update_center_freq(center_freq)
        self.initUI()

    def initUI(self):
        grid = QtGui.QGridLayout()
        grid.setSpacing(0)
        grid.addWidget(self.left, 0, 0, 2, 1)
        grid.addWidget(self.plot, 0, 1, 1, 1)
        grid.addWidget(self.bottom, 1, 1, 1, 1)
        grid.setRowStretch(0, 1)
        grid.setColumnStretch(1, 1)
        grid.setColumnMinimumWidth(0, LEFT_AXIS_WIDTH)
        grid.setRowMinimumHeight(1, BOTTOM_AXIS_HEIGHT)

        grid.setContentsMargins(0, 0, 0, 0)
        self.setLayout(grid)

    def update_data(self, powdata, center_freq):
        if self.plot.center_freq != center_freq:
            self.bottom.update_center_freq(center_freq)
        self.plot.update_data(powdata, center_freq)


def dBm_labels(height):
    """
    return a list of (position, label_text) tuples where position
    is a value between 0 (top) and height (bottom).
    """
    # simple, fixed implementation for now
    num = 8
    dBm_labels = [str(d) for d in numpy.linspace(DBM_TOP, DBM_BOTTOM, num)]
    y_values = numpy.linspace(0, height, num)
    return zip(y_values, dBm_labels)

class SpectrumViewLeftAxis(QtGui.QWidget):
    """
    The left axis of a spectrum view showing dBm range

    This widget includes the space to the left of the bottom axis
    """
    def paintEvent(self, e):
        qp = QtGui.QPainter()
        qp.begin(self)
        size = self.size()
        self.drawAxis(qp, size.width(), size.height())
        qp.end()

    def drawAxis(self, qp, width, height):
        qp.fillRect(0, 0, width, height, QtCore.Qt.black)
        qp.setPen(QtCore.Qt.gray)
        qp.fillRect(
            width - AXIS_THICKNESS,
            TOP_MARGIN,
            AXIS_THICKNESS,
            height - BOTTOM_AXIS_HEIGHT + AXIS_THICKNESS - TOP_MARGIN,
            QtCore.Qt.gray)

        for y, txt in dBm_labels(height - BOTTOM_AXIS_HEIGHT - TOP_MARGIN):
            qp.drawText(
                0,
                y + TOP_MARGIN - 10,
                LEFT_AXIS_WIDTH - 5,
                20,
                QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter,
                txt)

def MHz_labels(width, center_freq):
    """
    return a list of (position, label_text) tuples where position
    is a value between 0 (left) and width (right).
    """
    # simple, fixed implementation for now
    offsets = (-50, -25, 0, 25, 50)
    freq_labels = [str(center_freq / 1e6 + d) for d in offsets]
    x_values = [(d + 62.5) * width / 125 for d in offsets]
    return zip(x_values, freq_labels)

class SpectrumViewBottomAxis(QtGui.QWidget):
    """
    The bottom axis of a spectrum view showing frequencies
    """
    def update_center_freq(self, center_freq):
        self.center_freq = center_freq
        self.update()

    def paintEvent(self, e):
        qp = QtGui.QPainter()
        qp.begin(self)
        size = self.size()
        self.drawAxis(qp, size.width(), size.height())
        qp.end()

    def drawAxis(self, qp, width, height):
        qp.fillRect(0, 0, width, height, QtCore.Qt.black)
        qp.setPen(QtCore.Qt.gray)
        qp.fillRect(
            0,
            0,
            width - RIGHT_MARGIN,
            AXIS_THICKNESS,
            QtCore.Qt.gray)

        for x, txt in MHz_labels(width - RIGHT_MARGIN, self.center_freq):
            qp.drawText(
                x - 40,
                5,
                80,
                BOTTOM_AXIS_HEIGHT - 10,
                QtCore.Qt.AlignTop | QtCore.Qt.AlignHCenter,
                txt)



class SpectrumViewPlot(QtGui.QWidget):
    """
    The data plot of a spectrum view
    """
    def __init__(self, powdata, center_freq):
        super(SpectrumViewPlot, self).__init__()
        self.powdata = powdata
        self.center_freq = center_freq

    def update_data(self, powdata, center_freq):
        self.powdata = powdata
        self.center_freq = center_freq
        self.update()

    def paintEvent(self, e):
        qp = QtGui.QPainter()
        qp.begin(self)
        self.drawLines(qp)
        qp.end()

    def drawLines(self, qp):
        size = self.size()
        width = size.width()
        height = size.height()
        qp.fillRect(0, 0, width, height, QtCore.Qt.black)

        qp.setPen(QtGui.QPen(QtCore.Qt.gray, 1, QtCore.Qt.DotLine))
        for y, txt in dBm_labels(height - TOP_MARGIN):
            qp.drawLine(
                0,
                y + TOP_MARGIN,
                width - RIGHT_MARGIN - 1,
                y + TOP_MARGIN)
        for x, txt in MHz_labels(width - RIGHT_MARGIN, self.center_freq):
            qp.drawLine(
                x,
                TOP_MARGIN,
                x,
                height - 1)

        qp.setPen(QtCore.Qt.green)

        y_values = height - 1 - (self.powdata - DBM_BOTTOM) * (
            float(height) / (DBM_TOP - DBM_BOTTOM))
        x_values = numpy.linspace(0, width - 1 - RIGHT_MARGIN,
            len(self.powdata))
        vpoints = numpy.frompyfunc(QtCore.QPoint, 2, 1)

        qp.drawPolyline(vpoints(x_values, y_values))

