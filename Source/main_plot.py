from Source.functions.file_system import get_path
from Source.functions.read_h5 import read_h5_file
from Source.functions.plot_signals_qt import plot_all_signals


path = get_path()
data_path = path + '/Data/'
data_filename = '2020-10-16T13-28-55H3Do.h5'

data, time = read_h5_file(data_path + data_filename)

plot_all_signals(data, time)
