from matplotlib import pyplot as plt
from scipy.interpolate import interp1d
import numpy as np


def plot_average(data, x_label, y_label, title, confidence):
    time = np.sort(np.concatenate(data, axis=1)[0])
    merged_data = []

    for d in data:
        interp = interp1d(d[0], d[1], kind="previous", fill_value="extrapolate")
        merged_data.append(interp(time))

    merged_data = np.array(merged_data)
    average = np.average(merged_data, axis=0)
    std = np.std(merged_data, axis=0)

    fig, ax = plt.subplots()
    ax.step(time, average, where='post', label="average")
    if confidence:
        ax.plot(time, average - 2 * std, label="lower bound", linestyle='--')
        ax.plot(time, average + 2 * std, label="upper bound", linestyle='--')

    ax.axhline(0, color='k', linestyle='dashed')

    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    ax.set_title(title)
    ax.legend()

    ymin, ymax = ax.get_ylim()
    ax.axhspan(ymin=ymin, ymax=0, facecolor='r', alpha=0.25)
    ax.axhspan(ymin=0, ymax=ymax, facecolor='g', alpha=0.25)
    ax.set_ylim(ymin, ymax)
    ax.set_xlim(0, max(time))

    plt.show()
