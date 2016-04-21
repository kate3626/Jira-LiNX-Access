"""
Creates a graph of a the progress of LiNX Access from the json file edited in 
LA_longterm_json.py. No command line arguments needed. Designed for Python 3.
Line plot will skip over days that aren't there but will not create a line 
before the first date or after the last date. 
Author: Kate Olsen
Date: 19/04/2016
"""
import matplotlib.pyplot as plt
import json
import numpy as np
from matplotlib.backends.backend_pdf import PdfPages
import datetime


with open ('LA_progress.json','r') as cat:
    big_dict = json.load(cat)
components = list(big_dict.keys())

def fixVersions(dates):
    e = set()
    for component in components:
        for date in dates:
            e = e | (big_dict[component][date].keys())
    e.remove('done')
    return list(e)

def plot_dates(dates):
    start_date = datetime.datetime.strptime(dates[0], "%Y/%m/%d") 
    end_date = datetime.datetime.strptime(dates[-1], "%Y/%m/%d") 
    every_date = [dates[0]]
    i = 1
    while i < ((end_date - start_date).days + 1):
        every_date.append((start_date  + \
                           datetime.timedelta(days=i)).strftime('%Y/%m/%d'))
        i += 1
    return every_date


class DataLists(object):
    
    def __init__(self, fixVersion, component):
        self.varname = 'v' + fixVersion.replace('.', '_')
        self.version = fixVersion
        self.component = component
        self.data = []
        self.xticks = []
        self.x_labels = []
        
    def data_list_versions(self):
        self.data = []
        for date in all_dates:
            try:
                self.data.append(big_dict[self.component][date][self.version])
            except KeyError:
                self.data.append(None)
        return self.data
    
    def line_x(self):
        return [x for x in range(0, len(all_dates))]
    
    def setxticks(self):
        self.xticks = []
        self.xticks = [x for x in range(0, len(all_dates))]
        alist = self.xticks[::5] 
        alist.append(+ self.xticks[-1])
        self.xticks = alist
    
    def setxlabels(self):
        self.x_labels = []
        for tick in self.xticks:
            self.x_labels.append(str(all_dates[int(tick)]))
        

class DoneDate(object):
    
    def __init__(self, component):
        self.varname = component + 'done'
        self.component = component
        self.data = []
        self.x_bar = []
        self.xticks = []
        self.x_labels = []
        
    def done_data(self):
        self.data = []
        current_num = 0
        j = 0
        for i in range(0, len(all_dates)-1):
            if all_dates[i] in dates:
                next_num = big_dict[self.component][dates[j+1]]['done'] - \
                    big_dict[self.component][dates[j]]['done']
                j += 1
                if next_num > 0:
                    self.data.append(int(next_num))
                    current_num = int(next_num)
                else:
                    self.data.append(0)  
                    current_num = 0
            else:
                self.data.append(current_num)
        self.data.append(0)
        
    def bar_x(self):
        self.x_bar = []
        self.x_bar = [x for x in range(0, len(all_dates))] 
    
    def setxticks(self):
        self.xticks = []
        self.xticks = [x + 0.5 for x in range(0, len(all_dates)-1)]
        alist = self.xticks[::5] 
        alist.append(self.xticks[-1])
        self.xticks = alist
            
    def setxlabels(self):
        self.x_labels = []
        for tick in self.xticks:
            self.x_labels.append(str(all_dates[int(tick+0.5)]))


for component in components:
    pdf_name = component + '-' + str(datetime.date.today()) + '.pdf'
    pp = PdfPages(pdf_name)
    dates2 = (list(big_dict[component].keys()))
    dates = sorted(dates2)
    all_dates = plot_dates(dates)
    fix_version = fixVersions(dates)
    fig = plt.figure(figsize=(20, 10))
    fig.suptitle(component, fontsize=14, fontweight='bold')
    ax1 = fig.add_subplot(2, 1, 1)
    ax1.set_title('Story Points Uncompleted')
    ax1.set_ylabel('Story Points')
    ax2 = fig.add_subplot(2, 1, 2)
    ax2.set_title('Work Completed Since Last Date')
    ax2.set_ylabel('Story Points')
    fig.subplots_adjust(hspace=.5)
    for version in fix_version:
        x = DataLists(version, component)
        xs = np.arange(len(x.line_x()))
        series = np.array(x.data_list_versions()).astype(np.double)
        smask = np.isfinite(series)
        ax1.plot(xs[smask], series[smask], label=version)
    x = DataLists(fix_version[0], component)
    x.setxticks()
    x.setxlabels()
    ax1.legend(loc=(1.02, .45), shadow=True, fontsize=14)
    ax1.set_xticks(x.xticks)
    ax1.set_xticklabels(x.x_labels, rotation='vertical')
    g = DoneDate(component)
    g.done_data()
    g.bar_x()
    g.setxticks()
    g.setxlabels()
    ax2.hist(g.x_bar, len(g.data) - 1, weights=g.data)
    ax2.set_xticks(g.xticks)    
    ax2.set_xticklabels(g.x_labels, rotation='vertical')
    ax1.grid()
    ax2.yaxis.grid()
    plt.subplots_adjust(left=0.05, bottom=0.2)
    pp.savefig()
    pp.close()
