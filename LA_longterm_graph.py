"""
Creates a graph of a the progress of LiNX Access from the json file edited in LA_longterm_json.py
No command line arguments needed. Designed for Python 3.
Line plot will skip over days that aren't there but will not create a line before the first date
or after the last date. 
Author: Kate Olsen
Date: 19/04/2016
"""
import matplotlib.pyplot as plt
import json
import numpy as np
from matplotlib.backends.backend_pdf import PdfPages
pp = PdfPages('Access_Timeline.pdf')

with open ('LA_progress.json','r') as cat:
    big_dict = json.load(cat)
dates2 = (list(big_dict['iOS'].keys()))
dates = sorted(dates2)
components = list(big_dict.keys())

def fixVersions():
    e = set()
    for component in components:
        for date in dates:
            e = e | (big_dict[component][date].keys())
    e.remove('done')
    return list(e)
fix_version = fixVersions()

class DataLists(object):
    
    def __init__(self, fixVersion, component):
        self.varname = 'v' + fixVersion.replace('.', '_')
        self.version = fixVersion
        self.component = component
        self.data = []
        
    def data_list_versions(self):
        self.data = []
        for date in dates:
            try:
                self.data.append(big_dict[self.component][date][self.version])
            except KeyError:
                self.data.append(None)
        return self.data
    
    def line_x(self):
        return [x for x in range(0, len(dates))]


class DoneDate(object):
    
    def __init__(self, component):
        self.varname = component + 'done'
        self.component = component
        self.data = []
        self.x_bar = []
        self.xticks = []
        
    def done_data(self):
        self.data = []
        for i in range(0, len(dates)-1):
            try:
                next_num = big_dict[self.component][dates[i+1]]['done']-big_dict[self.component][dates[i]]['done']
                if next_num > 0:
                    self.data.append(int(next_num))
                else:
                    self.data.append(0)
            except KeyError:
                self.data.append(0)
        self.data.append(0)
        
    def bar_x(self):
        self.x_bar = []
        self.x_bar = [x for x in range(0, len(dates))] 
    
    def setxticks(self):
        self.xticks = []
        self.xticks = [x + 0.5 for x in range(0, len(dates)-1)]


for component in components:
    fig = plt.figure(figsize=(20, 10))
    fig.suptitle(component, fontsize=14, fontweight='bold')
    ax1 = fig.add_subplot(2, 1, 1)
    ax1.set_title('Story Points Uncompleted')
    ax1.set_ylabel('Story Points')
    ax2 = fig.add_subplot(2, 1, 2)
    ax2.set_title('Work Completed Per Day')
    ax2.set_ylabel('Story Points')
    fig.subplots_adjust(hspace=.5)
    for version in fix_version:
        x = DataLists(version, component)
        xs = np.arange(len(x.line_x()))
        series = np.array(x.data_list_versions()).astype(np.double)
        smask = np.isfinite(series)
        ax1.plot(xs[smask], series[smask], label=version)
    ax1.legend(loc=(1.02, .45), shadow=True, fontsize=14)
    ax1.set_xticks(DataLists(fix_version[0], component).line_x())
    ax1.set_xticklabels(dates, rotation='vertical')
    g = DoneDate(component)
    g.done_data()
    g.bar_x()
    g.setxticks()
    ax2.hist(g.x_bar, len(g.data) - 1, weights=g.data)
    ax2.set_xticks(g.xticks)    
    ax2.set_xticklabels(dates[1:], rotation='vertical')
    ax1.grid()
    ax2.yaxis.grid()
    plt.subplots_adjust(left=0.05, bottom=0.2)
    pp.savefig()
    plt.show()
