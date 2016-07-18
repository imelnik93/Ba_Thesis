# importing modules
import sys
import math as m
import random as r
import numpy as np
import pandas as pd
import statsmodels.tsa.stattools as tsa
from pylab import *
from multiprocessing import Pool
import os

# setting functions


def createacfdf(df, lag=90, aleph=.05):
    temp = tsa.acf(df, nlags=lag, fft=1, alpha=aleph)
    acf = pd.Series(temp[0])
    lb = pd.Series(transpose(temp[1])[0])
    ub = pd.Series(transpose(temp[1])[1])
    return pd.DataFrame(transpose([lb, acf, ub]), columns=['lb', 'acf', 'ub'])


def tempdata(tgen, l, extpars, exttype='const', xmean=0, xvar=100, theta=1, noiseext=1, noisevar=1):
    """
    Creates a temporary DataFrame filled with data generated at time t.
    :param tgen: "birth" time counter
    :param l: the expected number of generated traders
    :param extpars: parameters of the distribution of the exec time T
    :param exttype: distribution of the exec time T
    :param xmean: mean of the target volume of the ith trader
    :param xvar: variance of the target volume of the ith trader
    :param theta: probability of LT appearance
    :param noiseext: life expectancy of an NT, set to const 1 by default
    :param noisevar: variance of an NT trade
    """
    extvec = 0
    n = np.random.poisson(lam=l)
    ltvec = np.random.binomial(1, theta, size=n)
    xvec = m.sqrt(xvar) * np.random.randn(n) + xmean  # a Series of execution targets?
    tvec = np.transpose([tgen] * n)  # a Series of "birth times" of traders
    if exttype == 'const':
            extvec = [extpars] * n
    elif exttype == 'unif':
        a = extpars[0] - extpars[1]
        b = extpars[0] + extpars[1]
        extvec = np.random.randint(a, b, n)
    elif exttype == 'geom':
        extvec = np.random.geometric(float(1) / extpars, n)
    elif exttype == 'pois':
        extvec = np.random.poisson(extpars, n)
    for i in range(n):
        if ltvec[i] == 0:
            extvec[i] = noiseext
            xvec[i] = m.sqrt(noisevar) * np.random.randn(1)
    tvvec = xvec / extvec  # a Series of trading volumes
    return pd.DataFrame(np.transpose(np.array([tvec + extvec, xvec, tvvec])), index=range(1, n + 1),
                        columns=['death', 'Q', 'tv'])


def simdata(tmax, l, extpars, exttype='const', xmean=0, xvar=100, theta=1, noisevar=1, noiseext=1):
    df = tempdata(1, l, extpars, exttype, xmean, xvar, theta, noisevar, noiseext)
    output = pd.Series(sum(df.tv))
    for i in range(2, tmax + 1):
        temp = tempdata(i, l, extpars, exttype, xmean, xvar, theta, noisevar, noiseext)
        df = pd.ordered_merge(df, temp)
        df = df[df.death > i]
        output = output.append(pd.Series(sum(df.tv)))
    output = pd.DataFrame(output)
    output.columns = ['TV']
    output.index = range(1, len(output) + 1)
    return output

# globals
path = '/Users/ilyamelnikov/Dropbox/Study/Coursework/BaThesis/Data/simdata/short/'
os.chdir(path)
t = 10000
lam = 10
tavg = 50
tavgunif = [50, 20]


def store_sim(mode):
    if mode[0] == 'unif':
        createacfdf(simdata(t, lam, tavgunif, exttype='unif', xmean=0, xvar=100, theta=mode[1], noisevar=1,
                            noiseext=1)).to_csv('acfunif'+str(mode[1])+'.csv', sep='\t', encoding='utf-8')
    else:
        createacfdf(simdata(t, lam, tavg, exttype='const', xmean=0, xvar=100, theta=mode[1], noisevar=1,
                            noiseext=1)).to_csv('acfconst'+str(mode[1])+'.csv', sep='\t', encoding='utf-8')
mode_list = [['unif', 1], ['unif', 0.7], ['const', 1], ['const', 0.7]]
Pool().map(store_sim, mode_list)

