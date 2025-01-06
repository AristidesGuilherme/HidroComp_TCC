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
            between the start of the hydrological year and the chosen date
            
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
    
    
    def plot_bar_circular(self, month_num_start_year_hydrologic, unit='rad'):

        #Generating copy of daframe SDP
        df_circular_date = self.df_parcial.copy()

        #Add col with dates peaks floods
        df_circular_date['date_peaks'] = df_circular_date.index

        #Add circular dates 
        df_circular_date['circular_date'] = self.circular_date(month_num_start_year_hydrologic, unit)

        #Calculating the number of occurrences of each flood event
        list_freq = []
        for circular in df_circular_date['circular_date']:
            freq = 1
            for circular_compare in df_circular_date['circular_date']:
                if circular == circular_compare:
                    freq += 1
            list_freq.append(freq)

        #Add frequence events floods
        df_circular_date['freq'] = list_freq
        
        #Calculated month (numeric). Ex: January corresponding month 1, February month 2 ...
        df_circular_date['month_num'] = df_circular_date['date_peaks'].dt.month

        #Calculated name month
        df_circular_date['month'] = df_circular_date['date_peaks'].dt.month_name()

        #Add data for ajusting plot
        add_data = {'date_peaks':['01-'+str(mes)+'-2000' for mes in range(1, 13)],
                'circular_date':12*[0],
                'Duration':12*[0],
                'peaks':12*[0],
                'month':['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October','November', 'December'],
                'freq':12*[0],
                'month_num':[month for month in range(1, 13)]}
        
        #Concat dataframes and ordened months
        df_circular_date = pd.concat([pd.DataFrame(add_data), 
                                        df_circular_date]).sort_values(by=['month_num', 'freq'])
        
        #Showing only the first three letters of the months
        df_circular_date['month'] = df_circular_date['month'].apply(lambda x: x[:3])
        

        fig = px.bar_polar(df_circular_date, r="freq", theta="month", 
                color='peaks',
                color_continuous_scale= px.colors.sequential.Blues,
                labels={
                    'freq': 'Floods number',
                    'month': 'Month',
                    'peaks': 'Peak (m³/s)'})

        fig.update_layout(
            title='Eventos de cheias ',
            font=dict(family='Times New Roman', size=25, color='black'),
            font_size=22,
            legend_font_size=12,
            polar_radialaxis_ticksuffix=' Floods',
            polar_radialaxis_tickfont=dict(size=14),
            polar_angularaxis_rotation=90)

        fig.show()


    def plot_scatter_circular(self, month_num_start_year_hydrologic, unit='rad'):
        #Generating copy of daframe SDP
        df_circular_date = self.df_parcial.copy()

        #Add col with dates peaks floods
        df_circular_date['date_peaks'] = df_circular_date.index

        #Add circular dates 
        df_circular_date['circular_date'] = self.circular_date(month_num_start_year_hydrologic, unit)
        
        #Selecting columns that will be used
        df_circular_date = df_circular_date[['Duration', 'peaks', 'circular_date', 'date_peaks']]

        #Calculating year and month of each date
        df_circular_date['year'] = df_circular_date.index.year
        df_circular_date['month_num'] = df_circular_date.index.month
        df_circular_date['month'] = df_circular_date.index.month_name()


        #Add data for ajusting plot
        add_data = pd.DataFrame({'date_peaks':['01-'+str(mes)+'-2000' for mes in range(1, 13)],
                'circular_date':12*[0],
                'Duration':12*[0],
                'peaks':12*[0],
                'month':['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October','November', 'December'],
                'month_num':[month for month in range(1, 13)]})

        #Joining and ordering dataframes
        df_circular_date = pd.concat([df_circular_date, add_data]).sort_values(['month_num'])

        #Plotting data
        fig = px.scatter_polar(df_circular_date, r="peaks", theta="circular_date", 
                   color='year',
                   color_continuous_scale= px.colors.sequential.Plasma,
                   labels={
                     'peaks': 'Peaks (m³/s)',
                     'circular_date': 'Circular Date',
                     'year': 'Ano'})

        # ============ Ajusting ticktext legend =========
        # We need to generate the sequence of months of the hydrological year

        #Created list with all months year
        list_months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October','November', 'December']

        #List for saving sequence months
        sequence_month = []

        #Saving months from the beginning of the hydrological year until December
        for n_month in range(month_num_start_year_hydrologic, 13):
            sequence_month.append(list_months[n_month - 1][:3])

        ##Saving months from the January until end year hydrologic
        for n_month in range(1, month_num_start_year_hydrologic):
            sequence_month.append(list_months[n_month - 1][:3])

        fig.update_layout(
            title='Eventos de cheias ',
            font=dict(family='Times New Roman', size=25, color='black'),
            legend_font_size=18,
            polar_radialaxis_ticksuffix='',
            polar_radialaxis_tickfont=dict(size=14),
            polar_angularaxis_rotation=240,      
            #Ajust graph 
            polar=dict(
                bgcolor='white',
                angularaxis=dict(showline=True, linewidth=1, linecolor='white', gridcolor='gray',
                                tickvals=[30, 60, 90, 120, 150, 180, 210, 240, 270, 300, 330, 360],  # degrees 
                                ticktext=sequence_month),
                radialaxis=dict(showline=False, gridcolor='gray')),
            )

        fig.show()






