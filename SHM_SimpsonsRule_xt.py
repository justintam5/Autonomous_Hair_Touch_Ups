import numpy as np
import matplotlib.pyplot as plt


def read_csv(file_name, dim):
    at_t = np.genfromtxt(file_name, delimiter=',') # at_t has a time dimension
    dt = at_t[1, 0] - at_t[0, 0]
    t = at_t[:, 0]
    at = at_t[:, 1] # doesn't have a time dimension
    return at, t, np.shape(at_t)[0], dt


def double_simps_integral(x0, v0, dim, file_name):
    at1, t, ti, dt = read_csv(file_name, dim) # where at1 is the 1D acc/time retrieved from the file, ti is time index
    if (ti-1)%2 == 1:
        raise ValueError('N must be an even integer')
    at = np.zeros((ti, dim)); at[:, 0] = at1
    xt = np.zeros((ti, dim))
    vt = np.zeros((ti, dim))
    for d in range(dim):
        for i in range(1, ti):
            vt[i, d] = dt/3*(np.sum(at[0:i-1:2, d])+np.sum(4*at[1:i:2, d])+np.sum(at[2:i:2, d])) + v0[0, d]
            xt[i, d] = dt/3*(np.sum(vt[0:i-1:2, d])+np.sum(4*vt[1:i:2, d])+np.sum(vt[2:i:2, d])) + x0[0, d]
    return xt, vt, t


def plot_dim(zt, t, dim, ylabel):
    plt.plot(t.transpose(), zt.transpose()[dim-1])
    plt.ylabel(ylabel)
    plt.xlabel('Time(seconds)')
    plt.show()


if __name__ == '__main__':
    dim = 1
    x0 = np.zeros((1, dim)); x0[0] = 1
    v0 = np.zeros((1, dim))
    xt, vt, t = double_simps_integral(x0, v0, dim, 'SHM_acceleration.csv')
    # plot 1st dimension:
    plot_dim(xt, t, 1, 'Position')
    plot_dim(vt, t, 1, 'Velocity')
