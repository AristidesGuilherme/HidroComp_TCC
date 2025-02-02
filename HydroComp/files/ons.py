"""
Created on 21 de mar de 2018

@author: clebson
"""
import sys
sys.path.insert(0, r'C:\Users\arist\OneDrive\Documentos\UFAL\Pesquisas\PIBIC 24-25\lib_clebson') 

from HydroComp.files.fileRead import FileRead
import os
import pandas as pd
import numpy as np


class Ons(FileRead):

    source = "ONS"
    extension = "xls"

    def __init__(self, path=os.getcwd(), type_data='FLUVIOMÉTRICO', station=None):
        super().__init__(path)
        self.type_data = type_data
        self.station = station
        if self.station is None:
            self.data = self.read(self.name)
        else:
            self.data = pd.DataFrame(self.read(self.name)[self.station])

    def list_files(self):
        return super().list_files()

    def read(self, name=None):
        if name is None:
            return super().read()
        else:
            self.name = name
            return self.__read_lxs()

    def __read_lxs(self):
        file_ons = os.path.join(self.path, self.name+'.xls')
        data_flow = pd.read_excel(file_ons, shettname='Total', header=0, skiprows=5, index_col=0)
        data_flow.drop(np.NaN, inplace=True)

        aux = []
        dic = {'jan': '1', 'fev': '2', 'mar': '3', 'abr': '4', 'mai': '5',
               'jun': '6', 'jul': '7', 'ago': '8', 'set': '9', 'out': '10',
               'nov': '11', 'dez': '12'
               }
        for i in data_flow.index:
            aux.append(i.replace(i[-8:-5], dic[i[-8:-5]]))

        data_flow.index = pd.to_datetime(aux, dayfirst=True)
        code_column = [i.split(' (')[0] for i in data_flow.axes[1]]
        data_flow.columns = code_column

        return data_flow.astype(float)
