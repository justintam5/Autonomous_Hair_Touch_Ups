import numpy as np
import matplotlib.pyplot as plt


def read_csv(file_name, dim):
    at_t = np.genfromtxt(file_name, delimiter=',')
    dt = at_t[1, 0] - at_t[0, 0]
    t = at_t[:, 0]
    at = at_t[:, 1]
    return at, t, np.shape(at_t)[0], dt


def double_integral(x0, v0, dim, file_name):
    at1, t, ti, dt = read_csv(file_name, dim) # where at1 the 1D acc/time retrived from the file
    at = np.zeros((ti, dim)); at[:, 0] = at1
    xt = np.zeros((ti, dim)); xt[0, :] = x0[0]
    vt = np.zeros((ti, dim)); vt[0, :] = v0[0]
    for d in range(dim):
        for i in range(1, ti):
            vt[i, d] = vt[i-1, d] + at[i, d]*dt
            xt[i, d] = xt[i-1, d] + vt[i, d]*dt
    return xt, vt, t


def plot_dim(zt, t, dim):
    plt.plot(t.transpose(), zt.transpose()[dim-1])
    plt.show()


if __name__ == '__main__':
    dim = 1
    x0 = np.zeros((1, dim)); x0[0] = 1
    v0 = np.zeros((1, dim))
    xt, vt, t = double_integral(x0, v0, dim, 'SHM_acceleration.csv')
    # plot 1st dimension:
    plot_dim(xt, t, 1)
    plot_dim(vt, t, 1)
