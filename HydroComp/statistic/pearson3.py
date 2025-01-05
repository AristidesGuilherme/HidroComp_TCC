import sys
sys.path.insert(0, r'C:\Users\arist\OneDrive\Documentos\UFAL\PIBIC 24-25\lib_clebson') 

import numpy

import HydroComp.statistic.exceptions as e
from HydroComp.statistic.stats_build import StatsBuild
from scipy.stats import pearson3
from lmoments3.distr import pe3
from HydroComp.graphics.pearson_3 import Pearson3

class PearsonIII(StatsBuild):
    name = 'Pearson3'
    estimador = None
    dist = pearson3

    def __init__(self, data=None,  shape=None, loc=None, scale=None):
        super().__init__(data,  shape, loc, scale)
            
    def mml(self):
        if self.data is None:
            raise e.DataNotExist("Data not's None", 25)
        mml = pe3.lmom_fit(self.data)
        self.estimador = 'MML'
        self.shape = mml['c']
        self.loc = mml['loc']
        self.scale = mml['scale']
        self.dist = pearson3(c=self.shape, loc=self.loc, scale=self.scale)

        return self.shape, self.loc, self.scale

    def mvs(self):
        if self.data is None:
            raise e.DataNotExist("Data not's None", 35)
        mvs = pearson3.fit(data=self.data)
        self.estimador = 'MVS'
        self.shape = mvs[0]
        self.loc = mvs[1]
        self.scale = mvs[2]
        self.dist = pearson3(c=self.shape, loc=self.loc, scale=self.scale)

        return self.shape, self.loc, self.scale

    def probs(self, x):
        if self.dist is None:
            raise e.DistributionNotExist('Distribuição não existe', 51)
        else:
            if type(x) is list:
                return [self.probs(i) for i in x]
            return self.dist.cdf(x)

    def values(self, p):
        if self.dist is None:
            raise e.DistributionNotExist('Distribuição não existe', 51)
        else:
            if type(p) is list:
                return [self.values(i) for i in p]
            return self.dist.ppf(p)

    def interval(self, alpha):
        if self.dist is None:
            raise e.DistributionNotExist('Distribuição não existe', 51)
        else:
            return self.dist.interval(alpha)
