import plotly.graph_objs as go

from abc import ABCMeta, abstractmethod


class HydrogramBiuld(object, metaclass=ABCMeta):

    @abstractmethod
    def plot(self):
        pass

    def _plot_one(self, data):

        fig = go.Scatter(x=data.index, y=data.values, name=data.name,
                         line = dict(color = 'rgb(0,0,0)', width = 1),
                         opacity = 1)

        return fig