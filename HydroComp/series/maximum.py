import sys
sys.path.insert(0, r'C:\Users\arist\OneDrive\Documentos\UFAL\PIBIC 24-25\lib_clebson') 

import pandas as pd
import plotly as py
import scipy.stats as stat
from lmoments3 import distr
from HydroComp.statistic.genextre import Gev

from HydroComp.graphics.genextreme import GenExtreme
from HydroComp.graphics.hydrogram_annual import HydrogramAnnual

class Maximum(object):

    distribution = 'GEV'

    def __init__(self, obj, station):
        self.obj = obj
        self.data = self.obj.data
        self.station = station
        self.peaks = self.__annual()
        #self.fit = None
        self.dist_gev = Gev(self.peaks['peaks'].values)

    def __annual(self):
        data_by_year_hydrologic = self.data.groupby(pd.Grouper(
            freq='YS-%s' % self.obj.month_start_year_hydrologic(self.station)[1]))
        max_vazao = data_by_year_hydrologic[self.station].max().values
        idx_vazao = data_by_year_hydrologic[self.station].idxmax().values

        self.peaks = pd.DataFrame(max_vazao, index=idx_vazao, columns=['peaks'])
        return self.peaks

    def mvs(self):
        try:
            peaks = self.peaks.copy()
            self.fit = stat.genextreme.fit(peaks['peaks'].values, method="MLE")
            return self.fit
        except AttributeError:
            self.annual()
            return self.mvs()
        
    def mml(self):
        try:
            peaks = self.peaks.copy()
            #object fitting 
            fit = distr.gev.lmom_fit(peaks['peaks'].values)
            self.fit = [param[1] for param in fit.items()]
            return self.fit
        
        except AttributeError:
            self.annual()
            return self.mml()

    def magnitude(self, period_return, estimador):
        if estimador == 'mvs':
            self.mvs()
        elif estimador == 'mml':
            self.dist_gev.mml()
        prob = 1 - (1 / period_return)
        mag = self.dist_gev.values(prob)

        return mag

    def plot_distribution(self, title, estimador, type_function, save=False):
        if estimador == 'mvs':
            self.mvs()
        elif estimador == 'mml':
            self.mml()
        else:
            raise ValueError("Estimador: [mvs or mml]")
        genextreme = GenExtreme(title, self.fit[0], self.fit[1], self.fit[2])
        data, fig = genextreme.plot(type_function)
        if save:
            py.image.save_as(fig, filename='gráficos/GEV_%s_%s.png' % (type_function,
                                                                       estimador))
        return fig, data

    def plot_hydrogram(self, save=False):
        hydrogrm = HydrogramAnnual(data=self.data, peaks=self.peaks)
        fig, data = hydrogrm.plot()
        if save:
            py.image.save_as(fig, filename='gráficos/hidrogama_maximas_anuais.png')

        return fig, data
