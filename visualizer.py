import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('agg')
import seaborn as sns
import numpy as np
import time
from threading import Thread


class Visualizer:
    
    def __init__(self) -> None:
        pass
    
    def pie_chart_building(types, amounts, debit):
        colors = sns.cubehelix_palette(start=.5, rot=-.5)[0:len(amounts)]
        if debit:
            plt.title('Дебит', fontsize = 20)
        else:
            plt.title('Кредит', fontsize = 20)
        plt.pie(amounts, labels = types, colors = colors, textprops={'fontsize': 14}, autopct='%1.1f%%')
        path = f'pie_Chart{amounts[0]}.png'
        plt.savefig(path)
        plt.close()
        return path
        
    def plotting(dates, amounts):
        plt.plot(dates, amounts)
        path = f'pie_Chart{amounts[0]}.png'
        plt.savefig(path)
        plt.close()
        return path
        
    def func():
        #написать функцию, которая будет подводить баланс и писать насколько расходы/доходы превысили
        pass
    
    def func():
        #написать функцию, которая будет сравнивать показатели с предыдущим месяцем. 
        pass

        
    
if __name__ == '__main__':
    a = Visualizer
    #a.pieChartBuilding(types=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], amounts=[324.12, 121.31, 582.12, 1023.12, 100.42, 234.32, 324.12, 324.12, 324.12, 324.12, 324.12, 324.12])
    a.plotting(dates=['2001-01-01', '2002-02-02','2003-03-03', '2004-04-04', '2005-05-05', '2006-06-06', '2007-07-07', '2008-08-08', '2009-09-09','2010-10-10'], amounts=[324.12, 121.31, 300.12, 1023.12, 100.42, 324.12, 121.31, 300.12, 1023.12, 100.42])   