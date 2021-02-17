import matplotlib.pyplot as plt
from matplotlib.widgets import Slider


def plot_all_signals(data, time):
    num_rows = 12
    num_columns = 5
    fig, axes = plt.subplots(num_rows, num_columns, sharex=True, sharey=True)
    plt.subplots_adjust(bottom=0.25)

    for row_id in range(0, num_rows):
        for col_id in range(0, num_columns):
            axes[row_id, col_id].plot(time, data[:, row_id * num_columns + col_id])

    axcolor = 'lightgoldenrodyellow'
    axpos = plt.axes([0.2, 0.1, 0.65, 0.03], facecolor=axcolor)
    axzoom = plt.axes([0.2, 0.15, 0.65, 0.03], facecolor=axcolor)

    spos = Slider(axpos, 'Sec', min(time), max(time), valinit=0)
    szoom = Slider(axzoom, 'V', -2000, 0, valinit=-2000)

    def update(val):
        pos = spos.val
        zoom = szoom.val
        for i in range(0, axes.shape[0]):
            for j in range(0, axes.shape[1]):
                axes[i, j].axis([pos, pos + 10, zoom, -zoom])
        fig.canvas.draw_idle()

    spos.on_changed(update)
    szoom.on_changed(update)

    plt.show()
