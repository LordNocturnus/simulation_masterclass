from matplotlib import pyplot as plt
from scipy.interpolate import interp1d
import numpy as np


def plot_average(data, x_label, y_label, title, confidence, individual, save):
    time = np.sort(np.concatenate(data, axis=1)[0])
    merged_data = []
    fig, ax = plt.subplots()

    for k, d in enumerate(data):
        interp = interp1d(d[0], d[1], kind="previous", fill_value="extrapolate")
        merged_data.append(interp(time))
        if individual:
            ax.plot(time, merged_data[-1], label=f"run {k}")

    merged_data = np.array(merged_data)
    average = np.average(merged_data, axis=0)
    std = np.std(merged_data, axis=0)

    ax.step(time, average, where='post', label="average")
    if confidence:
        ax.plot(time, average - 2 * std, label="lower bound", color="r")
        ax.plot(time, average + 2 * std, label="upper bound", color="r")

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

    if save:
        plt.savefig("/plots/{}.svg".format(title))
    else:
        plt.show()
