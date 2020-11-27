import numpy as np
import matplotlib.pyplot as plt
from scipy import signal

file_name = '2020-11-26 12_52_47.520127_LOG1.csv'


def acc_preprocess(at, t, ti):
    fc = 1  # cut off frequency Hz
    fs = int(ti/t[-1, 0])
    normalized_fc = 2*fc/fs
    at_avg = np.sum(at[:, 0])/ti
    at[:, 0] = at[:, 0] - at_avg
    num_coeff, denum_coeff = signal.butter(5, normalized_fc)
    #  plot_dim(lpf_freq_response, t, dim, 'Freq. Response of the BPF')
    at = signal.lfilter(num_coeff, denum_coeff, at)
    plot_dim(at, t, dim, 'Freq. Response of the BPF')
    #  at = np.fft.ifft(at_ft_output)
    return at


def read_csv(file_name, dim):
    at_t12 = np.genfromtxt(file_name, delimiter=',')  # at_t has a time dimension
    ti = np.shape(at_t12)[0]
    if (ti)%2 == 1:
        ti = ti - 1
    # ti = int(ti/2) # divided the time by 2
    at_t = np.zeros((ti, dim))
    at_t = at_t12[:ti, :]
    t = np.zeros((ti, 1))
    at = np.zeros((ti, dim))
    t[:, 0] = 1/1000000*at_t[:ti, 6]  # convert microseconds to seconds
    at[:, 0] = 9.81/1000*at_t[:ti, 0]  # doesn't have a time dimension
    dti = np.zeros((ti-1, 1))  # debugging tool
    for i in range(ti-1):
        dti[i] = t[i+1]-t[i]
    # plot_dim(at, t, dim, 'Acceleration')
    at = acc_preprocess(at, t, ti)
    return at, t, ti


def double_simps_integral(x0, v0, dim, file_name):
    at1, t, ti = read_csv(file_name, dim)  # where at1 is the 1D acc/time retrieved from the file, ti is time index
    at = np.zeros((ti, dim)); at[:, 0] = at1[:, 0]
    xt = np.zeros((ti, dim))
    vt = np.zeros((ti, dim))
    dt = 0.006  # seconds, hard set for MSU tracker
    for d in range(dim):
        for i in range(1, ti):
            vt[i, d] = dt/3*(np.sum(at[0:i-1:2, d])+np.sum(4*at[1:i:2, d])+np.sum(at[2:i:2, d])) + v0[0, d]*np.sum(t[:i])
            xt[i, d] = dt/3*(np.sum(vt[0:i-1:2, d])+np.sum(4*vt[1:i:2, d])+np.sum(vt[2:i:2, d])) + x0[0, d]
    return xt, vt, at, t


def plot_dim(zt, t, dim, ylabel):
    plt.plot(t, zt)
    plt.ylabel(ylabel)
    plt.xlabel('Time (s)')
    plt.show()


if __name__ == '__main__':
    dim = 1
    x0 = np.zeros((1, dim)); x0[0] = 0
    v0 = np.zeros((1, dim)); v0[0] = 0
    xt, vt, at, t = double_simps_integral(x0, v0, dim, file_name)
    # plot 1st dimension:
    plot_dim(xt, t, dim, 'Position(m)')
    plot_dim(vt, t, dim, 'Velocity(m/s)')
    plot_dim(at, t, dim, 'Acceleration(m/s^2)')
