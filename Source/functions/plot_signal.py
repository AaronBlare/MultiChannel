import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider

fig, axes = plt.subplots(2, 1)
plt.subplots_adjust(bottom=0.25)

t = np.arange(0.0, 100.0, 0.1)
s = np.sin(2*np.pi*t)
axes[0].plot(t,s)

s1 = np.cos(2*np.pi*t)
axes[1].plot(t,s1)

axcolor = 'lightgoldenrodyellow'
axpos = plt.axes([0.2, 0.1, 0.65, 0.03], facecolor=axcolor)

spos = Slider(axpos, 'Pos', 0.1, 90.0)

def update(val):
    pos = spos.val
    axes[0].axis([pos,pos+10,-1,1])
    axes[1].axis([pos, pos + 10, -1, 1])
    fig.canvas.draw_idle()

spos.on_changed(update)

plt.show()