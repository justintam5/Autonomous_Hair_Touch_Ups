import numpy as np
import matplotlib.pyplot as plt
from scipy import signal, integrate

file_name_g = 'TestLastData.csv'


def butter_filter(data, normal_cutoff,  order, type):
    # Get the filter coefficients
    b, a = signal.butter(order, normal_cutoff, btype=type)
    y = signal.filtfilt(b, a, data)
    return y


def acc_post_process(at, t, ti):
    fc = 5  # cut off frequency Hz
    fs = int(ti/t[-1, 0])
    normalized_fc = 2*fc/fs
    at_mavg = np.zeros((ti, 1))
    #plot_1(at[:, 0], t, 'Acceleration before moving average :)')
    window = 2  # must be even
    for i in range(int(window/2), ti-int(window/2)):
        at_mavg[i, 0] = np.sum(at[i-int(window/2):i + int(window/2), 0])/window
    #plot_1(at_mavg[:, 0], t, 'Acceleration after moving average :)')
    at_mavg[:, 0] = butter_filter(at_mavg[:, 0], normalized_fc, 1, 'low')
    return at_mavg


def read_csv(file_name, dim):
    at_t12 = np.genfromtxt(file_name, delimiter=',')  # at_t has a time dimension
    ti = np.shape(at_t12)[0]
    if ti % 2 == 1:
        ti = ti - 1
    at_t = at_t12[:ti, :]
    t = np.zeros((ti, 1))
    at = np.zeros((ti, dim))
    t[:, 0] = 1/1000000*at_t[:ti, 6]  # convert microseconds to seconds
    at[:, 0] = 9.81/1000*at_t[:ti, 0]  # doesn't have a time dimension
    dti = np.zeros((ti-1, 1))  # debugging tool
    for i in range(ti-1):
        dti[i] = t[i+1]-t[i]
    at = acc_post_process(at, t, ti)
    return at, t, ti


def double_simps_integral(x0, v0, dim, file_name):
    at1, t, ti = read_csv(file_name, dim)  # where at1 is the 1D acc/time retrieved from the file, ti is time index
    at = np.zeros((ti, dim)); at[:, 0] = at1[:, 0]
    xt = np.zeros((ti, dim))
    vt = np.zeros((ti, dim))
    freq_factor = 2/int(ti/t[-1, 0])
    for d in range(dim):
        for i in range(1, ti):
            vt[i, d] = integrate.simps(at[:i+1, d], x=t[:i+1, 0]) + v0[0]
    vt[:, 0] = butter_filter(vt[:, 0], 0.2*freq_factor, 1, 'high')
    #vt[:, 0] = butter_filter(vt[:, 0], 6*freq_factor, 1, 'low')
    for d in range(dim):
        for i in range(1, ti):
            xt[i, d] = integrate.simps(vt[:i+1, d], x=t[:i+1, 0]) + x0[0]
    #xt[:, 0] = butter_filter(xt[:, 0], 0.7*freq_factor, 1, 'high')
    #xt[:, 0] = butter_filter(xt[:, 0], 4*freq_factor, 1, 'low')
    return xt, vt, at, t


def plot_1(zt, t, ylabel):
    plt.plot(t, zt)
    plt.ylabel(ylabel)
    plt.xlabel('Time (s)')
    plt.show()


def plot_3(pt, bt, jt, t, title_pt, title_bt, title_jt):
    fig, axs = plt.subplots(2, 2)
    axs[0, 0].plot(t, pt)
    axs[0, 0].set_title(title_pt)
    axs[0, 1].plot(t, bt, 'tab:orange')
    axs[0, 1].set_title(title_bt)
    axs[1, 0].plot(t, jt, 'tab:green')
    axs[1, 0].set(xlabel='Time (seconds)', ylabel=title_jt)
    plt.show()


if __name__ == '__main__':
    dimensions = 1
    x0f = np.zeros((1, dimensions)); x0f[0] = 0
    v0f = np.zeros((1, dimensions)); v0f[0] = 0
    xtf, vtf, atf, tf = double_simps_integral(x0f, v0f, dimensions, file_name_g)
    plot_3(xtf[:, 0], vtf[:, 0], atf[:, 0], tf, 'Position(m)', 'Velocity(m/s)', 'Acceleration(m/s^2)')
