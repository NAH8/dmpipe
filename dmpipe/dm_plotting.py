#!/usr/bin/env python
#

"""
Utilities to plot dark matter analyses
"""

import numpy as np

from fermipy import castro
from fermipy import stats_utils
from fermipy import sed_plotting

from dmpipe.dm_spectral import DMSpecTable


def plot_dm_castro(castro_dm, ylims=(1e-28, 1e-22), nstep=100, zlims=None):
    """ Make a color plot (1castro plot) of the delta log-likelihood as a function of
    DM particle mass and cross section.

    castro_dm  : A CastroData object, with the log-likelihood v. normalization for each energy bin
    ylims      : y-axis limits
    nstep      : Number of y-axis steps to plot for each energy bin
    zlims      : z-axis limits
    """
    mass_label = r"$m_{\chi}$ [GeV]"
    sigmav_label = r'$\langle \sigma v \rangle$ [$cm^{3} s^{-1}$]'
    return sed_plotting.plotCastro_base(castro_dm,
                                        xlims=(castro_dm.masses[0], castro_dm.masses[-1]),
                                        ylims=ylims,
                                        xlabel=mass_label,
                                        ylabel=sigmav_label,
                                        nstep=nstep,
                                        zlims=zlims)


def plot_castro_nuiscance(xlims, ylims, zvals, zlims=None):
    """ Make a castro plot including the effect of the nuisance parameter
    """
    import matplotlib.pyplot as plt
    import matplotlib

    fig = plt.figure()
    axis = fig.add_subplot(111)
    axis.set_yscale('log')
    axis.set_xlim(xlims)
    axis.set_ylim(ylims)
    axis.set_xlabel(r'$\delta J / J$')
    axis.set_ylabel(r'$\langle \sigma v \rangle$ [cm$^3$ s$^{-1}$]')
    if zlims is None:
        zmin = 0
        zmax = 10.
    else:
        zmin = zlims[0]
        zmax = zlims[1]

    image = axis.imshow(zvals, extent=[xlims[0], xlims[-1], ylims[0], ylims[-1]],
                        origin='lower', aspect='auto', interpolation='nearest',
                        vmin=zmin, vmax=zmax, cmap=matplotlib.cm.jet_r)
    return fig, axis, image


def plot_nll(nll_dict, xlims=None, nstep=50, ylims=None):
    """ Plot the -log(L) as a function of sigmav for each object in a dict
    """
    import matplotlib.pyplot as plt
    import matplotlib
    if xlims is None:
        xmin = 1e-28
        xmax = 1e-24
    else:
        xmin = xlims[0]
        xmax = xlims[1]

    xvals = np.logspace(np.log10(xmin), np.log10(xmax), nstep)
    fig = plt.figure()
    axis = fig.add_subplot(111)

    axis.set_xlim((xmin, xmax))
    if ylims is not None:
        axis.set_ylim((ylims[0], ylims[1]))

    axis.set_xlabel(r'$\langle \sigma v \rangle$ [cm$^3$ s$^{-1}$]')
    axis.set_ylabel(r'$\Delta \log\mathcal{L}$')
    axis.set_xscale('log')

    for lab, nll in nll_dict.items():
        yvals = nll.interp(xvals)
        yvals -= yvals.min()
        axis.plot(xvals, yvals, label=lab)

    leg = axis.legend(loc="upper left")
    return fig, axis, leg


def plot_comparison(nll, nstep=25, xlims=None):
    """ Plot the comparison between differnt version of the -log(L)
    """
    import matplotlib.pyplot as plt
    import matplotlib
    if xlims is None:
        xmin = nll._lnlfn.interp.xmin
        xmax = nll._lnlfn.interp.xmax
    else:
        xmin = xlims[0]
        xmax = xlims[1]

    xvals = np.linspace(xmin, xmax, nstep)
    yvals_0 = nll.straight_loglike(xvals)
    yvals_1 = nll.profile_loglike(xvals)
    yvals_2 = nll.marginal_loglike(xvals)

    ymin = min(yvals_0.min(), yvals_1.min(), yvals_2.min(), 0.)
    ymax = max(yvals_0.max(), yvals_1.max(), yvals_2.max(), 0.5)

    fig = plt.figure()
    axis = fig.add_subplot(111)

    axis.set_xlim((xmin, xmax))
    axis.set_ylim((ymin, ymax))

    axis.set_xlabel(r'$\langle \sigma v \rangle$ [cm$^3$ s$^{-1}$]')
    axis.set_ylabel(r'$\Delta \log\mathcal{L}$')

    axis.plot(xvals, yvals_0, 'r', label=r'Simple $\log\mathcal{L}$')
    axis.plot(xvals, yvals_1, 'g', label=r'Profile $\log\mathcal{L}$')
    #axis.plot(xvals,yvals_2,'b', label=r'Marginal $\log\mathcal{L}$')

    leg = axis.legend(loc="upper left")

    return fig, axis, leg


def plot_stacked(sdict, xlims, ibin=0):
    """ Stack a set of -log(L) curves and plot the stacked curve
    as well as the individual curves
    """
    import matplotlib.pyplot as plt
    import matplotlib
    ndict = {}

    for key, val in sdict.items():
        ndict[key] = val[ibin]

    #mles = np.array([n.mle() for n in ndict.values()])

    fig = plt.figure()
    axis = fig.add_subplot(111)

    xvals = np.linspace(xlims[0], xlims[-1], 100)

    axis.set_xlim((xvals[0], xvals[-1]))
    axis.set_xlabel(r'$\langle \sigma v \rangle$ [cm$^3$ s$^{-1}$]')
    axis.set_ylabel(r'$\Delta \log\mathcal{L}$')

    for key, val in ndict.items():
        yvals = val.interp(xvals)
        if key.lower() == "stacked":
            axis.plot(xvals, yvals, lw=3, label=key)
        else:
            yvals -= yvals.min()
            axis.plot(xvals, yvals, label=key)
    leg = axis.legend(loc="upper left", fontsize=10, ncol=2)
    return fig, axis, leg


def plot_limits(sdict, xlims, ylims, alpha=0.05):
    """ Plot the upper limits as a functino of DM particle mass and cross section.

    sdict      : A dictionary of CastroData objects,
                 with the log-likelihood v. normalization for each energy bin
    xlims      : x-axis limits
    ylims      : y-axis limits
    alpha      : Confidence level to use in setting limits = 1 - alpha
    """
    import matplotlib.pyplot as plt
    import matplotlib

    fig = plt.figure()
    axis = fig.add_subplot(111)
    axis.set_xlabel(r'$m_{\chi}$ [GeV]')
    axis.set_ylabel(r'$\langle \sigma v \rangle$ [cm$^3$ s$^{-1}$]')

    axis.set_xscale('log')
    axis.set_yscale('log')
    axis.set_xlim((xlims[0], xlims[1]))
    axis.set_ylim((ylims[0], ylims[1]))

    for key, val in sdict.items():
        xvals = val.masses
        yvals = val.getLimits(alpha)
        if key.lower() == "stacked":
            axis.plot(xvals, yvals, lw=3, label=key)
        else:
            axis.plot(xvals, yvals, label=key)

    leg = axis.legend(loc="upper left")  # ,fontsize=10,ncol=2)
    return fig, axis, leg


def compare_limits(sdict, xlims, ylims, alpha=0.05):
    """ Plot the upper limits as a functino of DM particle mass and cross section.

    sdict      : limits and keys
    xlims      : x-axis limits
    ylims      : y-axis limits
    alpha      : Confidence level to use in setting limits = 1 - alpha
    """
    import matplotlib.pyplot as plt
    import matplotlib

    fig = plt.figure()
    axis = fig.add_subplot(111)

    axis.set_xscale('log')
    axis.set_yscale('log')
    axis.set_xlim((xlims[0], xlims[1]))
    axis.set_ylim((ylims[0], ylims[1]))

    for key, val in sdict.items():
        xvals = val.masses
        yvals = val.getLimits(alpha)
        axis.plot(xvals, yvals, label=key)

    leg = axis.legend(loc="upper left", fontsize=10, ncol=2)
    return fig, axis, leg


def plot_limit(dm_castro_data, ylims, alpha=0.05):
    """ Plot the limit curve for a given DMCastroData object
    """
    import matplotlib.pyplot as plt
    import matplotlib
    xbins = dm_castro_data.masses
    xmin = xbins[0]
    xmax = xbins[-1]

    fig = plt.figure()
    axis = fig.add_subplot(111)

    axis.set_xscale('log')
    axis.set_yscale('log')
    axis.set_xlim((xmin, xmax))

    if ylims is not None:
        axis.set_ylim((ylims[0], ylims[1]))

    yvals = dm_castro_data.getLimits(alpha)
    if yvals.shape[0] == xbins.shape[0]:
        xvals = xbins
    else:
        xvals = np.sqrt(xbins[0:-1] * xbins[1:])
    axis.plot(xvals, yvals)

    return fig, axis



def test_func():
    """ Test the functionality of this module """
    norm_type = "EFLUX"

    spec_table = DMSpecTable.create_from_fits("dm_spec_2.fits")
    castro_eflux = castro.CastroData.create_from_fits("dsph_castro.fits", norm_type, irow=3)
    castro_dm = spec_table.convert_castro_data(castro_eflux, 4, norm_type)

    mass_label = r"$m_{\chi}$ [GeV]"
    sigmav_label = r'$\langle \sigma v \rangle$ [$cm^{3} s^{-1}$]'
    masses = np.logspace(1, 4, 13)

    fig2_dm = sed_plotting.plotCastro_base(castro_dm,
                                           xlims=(masses[0], masses[-1]),
                                           ylims=(1e-28, 1e-22),
                                           xlabel=mass_label,
                                           ylabel=sigmav_label,
                                           nstep=100)

    nll_dm = castro_dm[2]
    j_prior = stats_utils.create_prior_functor(dict(functype='lgauss', mu=1., sigma=0.15))
    j_vals = np.linspace(0.7, 1.3, 30)

    in_vals = np.meshgrid(j_vals, nll_dm.interp.x)
    func = stats_utils.LnLFn_norm_prior(nll_dm, j_prior)

    out_vals = func.loglike(in_vals[0], in_vals[1])

    xlims = (j_vals[0], j_vals[-1])
    ylims = (nll_dm.interp.x[1], nll_dm.interp.x[-1])

    cnn = plot_castro_nuiscance(xlims, ylims, out_vals, zlims=(0., 30.))
    cll = plot_comparison(func, nstep=100, xlims=(0, 1e-26))

    return fig2_dm, cnn, cll

if __name__ == "__main__":
    test_func()
