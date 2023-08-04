import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('agg')
import seaborn as sns
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import make_pipeline
import numpy as np


class Visualizer:
    
    def __init__(self) -> None:
        pass
    
    def pie_chart_building(types, amounts):
        colors = sns.cubehelix_palette(start=.5, rot=-.5)[0:len(amounts)]
        plt.pie(amounts, labels = types, colors = colors)
        path = f'pie_Chart{amounts[0]}.png'
        plt.savefig(path)
        return path
        
    def plotting(dates, amounts):
        polyModel = make_pipeline(PolynomialFeatures(7), LinearRegression())
        dates = np.array(dates, dtype='datetime64')
        amounts = np.array(amounts)
        xfit = np.linspace(0,1,10)
        polyModel.fit(dates[:, np.newaxis], amounts)
        yfit = polyModel.predict(xfit[:, np.newaxis])
        plt.xlim(dates[0], dates[-1])
        plt.ylim(0, 1100)
        plt.scatter(dates, amounts)
        plt.plot(xfit, yfit)
        plt.show()
        
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