import pandas as pd
import numpy as np
from calendar import month_name
import plotly.express as px

" Class for calculated statisticals circular"

class Circular(object):

    def __init__(self, df_parcial):
        self.df_parcial = df_parcial


    def day_hydrologic(self, date_input, month_num_start_year_hydrologic):

        ''' With a peak flood date, it calculates how many days occurred 
            between the beginning of the hydrological year and the chosen date
            
            date_input: Ex: '1996-01-17'
            month_num_start_year_hydrologic: Ex: January is 1, February is 2 ... December is 12
            '''

        #Converting for format datetime 
        date_input = pd.to_datetime(date_input)

        #checking whether the beginning of the hydrological year is in the same calendar year
        #Ex: If month_num_start_year_hydrologic = 9 and date_input = '1996-01-17' 
        #    start_year_hydrologic = '1995-09-01' ---> different calendar year

        #Case 1: different calendar year
        if date_input.month < month_num_start_year_hydrologic:
            date = str(date_input.year - 1) + '-' + str(month_num_start_year_hydrologic) + '-01'
            start_year_hydrologic = pd.to_datetime(date)

        #Case 2: same calendar year
        else:
            date = str(date_input.year ) + '-' + str(month_num_start_year_hydrologic) + '-01'
            start_year_hydrologic = pd.to_datetime(date)

        day_hydro = (date_input - start_year_hydrologic).days

        return day_hydro
    
    def days_total_year_hydrologic(self, date_input, month_num_start_year_hydrologic):
        '''
            Calculates the total number of days in a hydrological year.
            date_input: Ex: '1996-01-17'
            month_num_start_year_hydrologic: Ex: January is 1, February is 2 ... December is 12
        '''

        #Same logic the function 'day_hydrologic'
        date_input = pd.to_datetime(date_input)

        if date_input.month < month_num_start_year_hydrologic:
            date = str(date_input.year - 1) + '-' + str(month_num_start_year_hydrologic) + '-01'
            date_start_year_hydrologic = pd.to_datetime(date)
            end_year_hydrologic = date_input.year

        else:
            date = str(date_input.year ) + '-' + str(month_num_start_year_hydrologic) + '-01'
            date_start_year_hydrologic = pd.to_datetime(date)

            #Add year posterior. In cases ex: '2017-12-30' and month_num_start_year_hydrologic = 9
            # date_start_year_hydrologic = '2017-09-30' ---> end_year_hydrologic = 2018
            end_year_hydrologic = date_input.year + 1

        #Calculated month end year hydrologic
        if date_start_year_hydrologic.month == 1:
            month_num_end_year_hydrologic = 12
        else:
            month_num_end_year_hydrologic = date_start_year_hydrologic.month - 1
        
        #Determining date end year hydrologic
        date_end_year_hydrologic = pd.to_datetime(str(end_year_hydrologic) + '-' + str(month_num_end_year_hydrologic) + '-31')

        #Quantify days beteen start and end year hydrologic. Method date1 - date2 It is an open interval, 
        #so we must count 1 more day. Ex: '1996-01-17' -  '1996-01-16' = 1
        days_full_hydro = (date_end_year_hydrologic - date_start_year_hydrologic).days + 1

        return days_full_hydro
    
    def circular_date(self, month_num_start_year_hydrologic, unit='rad'):
        ''' Converting Gregorian dates to circular dates
            month_num_start_year_hydrologic: Ex: January is 1, February is 2 ... December is 12
            unit: seletec 'rad' or 'degrees'
        '''
        #Saving peak dates in a column
        df = self.df_parcial.copy()
        df['date_peaks'] = df.index

        #Calcule day hydrologic and days total in year hydrologic for each peak date
        day_hidrology = df['date_peaks'].apply(lambda date: self.day_hydrologic(date, month_num_start_year_hydrologic))
        days_year_hydrologic = df['date_peaks'].apply(lambda date: self.days_total_year_hydrologic(date, month_num_start_year_hydrologic))

        #Calcule circular date for radians or degrees
        if unit == 'rad':
            date_circular = 2*np.pi * (day_hidrology / days_year_hydrologic)
        elif unit == 'degrees':
            date_circular = 360 * (day_hidrology / days_year_hydrologic)

        return date_circular





    '''def radians_date(self, type_date='peak', scale='year'):
       

        df = self.df_parcial.copy()
        df['date_peak'] = df.index
        
        #Defining dict with parameters for calculus radians 
        dic_type_date = {'peak':'date_peak', 'Start':'Start', 'End':'End'}
        dict_scale = {'week':7, 'month':31, 'year':365}

        #Get parameters
        col_name = dic_type_date[type_date]
        factor_scale = dict_scale[scale]
        
        #Calculeted date radians
        radians_date = df[col_name].dt.dayofweek * 2 * np.pi / factor_scale


        #Created new dataframe for saving data
        df_new = pd.DataFrame()
        df_new[col_name], df_new['radians_date'] = df[col_name], radians_date
        df_new['Duration'], df_new['peaks'] = df['Duration'], df['peaks']

        #Ajust columns and index dataframe
        df_new.reset_index(inplace=True)
        df_new.drop(['index'], axis=1, inplace=True)

        return df_new'''
    
    
    def plot_radians_date(self, type_date='peak', scale='year'):
        #Defining dict with parameters for calculus radians 
        dic_type_date = {'peak':'date_peak', 'Start':'Start', 'End':'End'}
        dict_scale = {'week':7, 'month':31, 'year':365}

        #Get parameters
        col_name = dic_type_date[type_date]
        factor_scale = dict_scale[scale]

        #Calculated radians date
        df_radians_date = self.radians_date(type_date, scale)

        if scale == 'month':
            #Armazenando frequência de ocorrência  de cada dia dentro do mês
            list_freq = []
            for radians in df_radians_date['radians_date']:
                freq = 1
                for radians_compare in df_radians_date['radians_date']:
                    if radians == radians_compare:
                        freq += 1
                list_freq.append(freq)

            df_radians_date['freq'] = list_freq
            
            #Calculated month (numeric). Ex: January corresponding month 1, February month 2 ...
            df_radians_date['month_num'] = df_radians_date[col_name].dt.month

            #Calculated name month
            df_radians_date['month'] = df_radians_date[col_name].dt.month_name()

            #Add data for ajusting plot
            add_data = {col_name:['01-'+str(mes)+'-2000' for mes in range(1, 13)],
                    'radians_date':12*[0],
                    'Duration':12*[0],
                    'peaks':12*[0],
                    'month':['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October','November', 'December'],
                    'freq':12*[0],
                    'month_num':[month for month in range(1, 13)]}
            
            #Concat dataframes and ordened months
            df_radians_date = pd.concat([pd.DataFrame(add_data), 
                                         df_radians_date]).sort_values(by=['month_num', 'freq'])
            

            fig = px.bar_polar(df_radians_date, r="freq", theta="month", 
                   color='peaks',
                   color_continuous_scale= px.colors.sequential.Blues)


            fig.update_layout(
                title=dict(text='Eventos de cheias '),
                font=dict(family='Time New Roman', size=18, color='black'),
                legend_font_size=16,
                polar_radialaxis_ticksuffix='',
                polar_angularaxis_rotation=90,
                polar_angularaxis_tick0=5,
            )

            fig.show()

            



