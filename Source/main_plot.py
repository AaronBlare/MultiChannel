from Source.functions.file_system import get_path
from Source.functions.read_h5 import read_h5_file

path = get_path()
data_path = path + '/Data/'
data_filename = '2020-10-16T13-28-55H3Do.h5'

data, time = read_h5_file(data_path + data_filename)

import matplotlib.pyplot as plt
from matplotlib.widgets import Slider

fig, axes = plt.subplots(2, 1)
plt.subplots_adjust(bottom=0.25)

t = time
s = data[:, 0]
axes[0].plot(t, s)

s1 = data[:, 1]
axes[1].plot(t, s1)

axcolor = 'lightgoldenrodyellow'
axpos = plt.axes([0.2, 0.1, 0.65, 0.03], facecolor=axcolor)

spos = Slider(axpos, 'Pos', min(time), max(time))


def update(val):
    pos = spos.val
    axes[0].axis([pos, pos + 10, -2000, 2000])
    axes[1].axis([pos, pos + 10, -2000, 2000])
    fig.canvas.draw_idle()


spos.on_changed(update)

plt.show()
