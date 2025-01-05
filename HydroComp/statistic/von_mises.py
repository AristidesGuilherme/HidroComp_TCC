import HydroComp.statistic.exceptions as e
from HydroComp.statistic.stats_build import StatsBuild
from scipy.stats import vonmises
from lmoments3.distr import m


class Vonm(StatsBuild):

    name = 'VM'
    estimator = None
    dist = vonmises

    def __init__(self, data=None,  shape=None, loc=None, scale=None):
        super().__init__(data, shape, loc, scale)
    
    def mml(self):
        if self.data is None:
            raise e.DataNotExist("Data not's None", 25)
        mml = vonmises.fit(data=self.data, method='MM')
        self.estimador = 'MML'
        self.shape = mml['c']
        self.loc = mml['loc']
        self.scale = mml['scale']
        self.dist = vonmises(c=self.shape, loc=self.loc, scale=self.scale)

        return self.shape, self.loc, self.scale

    def mvs(self):
        if self.data is None:
            raise e.DataNotExist("Data not's None", 35)
        mvs = vonmises.fit(data=self.data)
        self.estimador = 'MVS'
        self.shape = mvs[0]
        self.loc = mvs[1]
        self.scale = mvs[2]
        self.dist = vonmises(c=self.shape, loc=self.loc, scale=self.scale)

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