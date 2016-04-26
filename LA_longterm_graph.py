"""
Creates a graph of a the progress of LiNX Access from the json file edited in 
LA_longterm_json.py. No command line arguments needed but can be added to print 
out your choice of graphs. Designed for Python 3.
Line plot will skip over days that aren't there but will not create a line 
before the first date or after the last date. Moving average set to 2 months.
Author: Kate Olsen
Date: 19/04/2016
"""
import matplotlib.pyplot as plt
import json
import numpy as np
from matplotlib.backends.backend_pdf import PdfPages
import datetime
from collections import deque
import argparse


def fixVersions(dates, vlist, component):
    own_versions = False
    if len(vlist) != 0:
        version_list = []
        for version in vlist:
            if version[0].lower() == component:
                own_versions = True
                version_list.append(version[1:])
        if own_versions:
            return version_list
    if not own_versions: 
        e = set()
        for date in dates:
            e = e | (big_dict[date].keys())
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
    
    def __init__(self, fixVersion):
        self.varname = 'v' + fixVersion.replace('.', '_')
        self.version = fixVersion
        self.data = []
        self.xticks = []
        self.x_labels = []
        
    def data_list_versions(self):
        self.data = []
        for date in all_dates:
            try:
                self.data.append(big_dict[date][self.version])
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
    
    def __init__(self):
        self.varname = 'done'
        self.data = []
        self.x_bar = []
        self.xticks = []
        self.x_labels = []
        self.mov_avg = []
        
    def done_data(self):
        self.data = []
        current_num = 0
        j=0
        for i in range(0, len(all_dates)):
            if all_dates[i] in dates:
                next_num = big_dict[dates[j]]['done']
                self.data.append(int(next_num))
                j += 1
            else:
                self.data.append(0)
        self.data.append(0)
        
    def bar_x(self):
        self.x_bar = []
        self.x_bar = [x for x in range(0, len(all_dates) + 1)] 
    
    def setxticks(self):
        self.xticks = []
        self.xticks = [x + 0.5 for x in range(0, len(all_dates))]
        alist = self.xticks[::5] 
        alist.append(self.xticks[-1])
        self.xticks = alist
            
    def setxlabels(self):
        self.x_labels = []
        for tick in self.xticks:
            self.x_labels.append(str(all_dates[int(tick-0.5)]))
    
    def moving_average(self):
        self.mov_avg = []
        nums = deque(maxlen=60) #change length of moving average here
        for i in range(0, len(all_dates)):
            nums.append(self.data[i])
            self.mov_avg.append(sum(nums)/len(nums))
            
            
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--PC', help='Json file is: LA-PC.json\n' + \
                        'To choose versions write "p" then version number, eg, p3.0.' + \
                        '\n-p and/or -i needs to come before the version list.', 
                        action='store_true')
    parser.add_argument('-i', '--iOS', help='Json file is: LA-iOS.json\n' + \
                        'To choose versions write "i" then version number, eg, i3.0.' + \
                        '\n-p and/or -i needs to come before the version list.', 
                        action='store_true')
    parser.add_argument('args', nargs=argparse.REMAINDER)
    args = parser.parse_args() 
    filenames = []
    print(args.args)
    if args.PC:
        filenames.append('LA-PC.json')
    if args.iOS:
        filenames.append('LA-iOS.json') 
    if len(filenames) == 0:
        filenames = ['LA-iOS.json', 'LA-PC.json']
    for i in range(0, len(filenames)):
        with open (filenames[i],'r') as cat:
            big_dict = json.load(cat)
        pdf_name = filenames[i].split('-')[1].split('.')[0] + '-' + str(datetime.date.today()) + '.pdf'
        pp = PdfPages(pdf_name)
        dates2 = (list(big_dict.keys()))
        dates = sorted(dates2)
        all_dates = plot_dates(dates)
        fix_version = fixVersions(dates, args.args, filenames[i].split('-')[1].split('.')[0][0].lower())
        fig = plt.figure(figsize=(20, 10))
        fig.suptitle(filenames[i].split('-')[1].split('.')[0], fontsize=14, fontweight='bold')
        ax1 = fig.add_subplot(2, 1, 1)
        ax1.set_title('Story Points Uncompleted')
        ax1.set_ylabel('Story Points')
        ax2 = fig.add_subplot(2, 1, 2)
        ax2.set_title('Work Completed Each Day')
        ax2.set_ylabel('Story Points')
        fig.subplots_adjust(hspace=.5)
        for version in fix_version:
            x = DataLists(version)
            xs = np.arange(len(x.line_x()))
            series = np.array(x.data_list_versions()).astype(np.double)
            smask = np.isfinite(series)
            ax1.plot(xs[smask], series[smask], label=version, marker='o')
        x = DataLists(fix_version[0])
        x.setxticks()
        x.setxlabels()
        ax1.legend(loc=(1.02, .45), shadow=True, fontsize=14)
        ax1.set_xticks(x.xticks)
        ax1.set_xticklabels(x.x_labels, rotation='vertical')
        g = DoneDate()
        g.done_data()
        g.bar_x()
        g.setxticks()
        g.setxlabels()
        g.moving_average()
        ax2.hist(g.x_bar, len(g.data) - 1, weights=g.data)
        ax2.plot([x + 0.5 for x in range(0, len(all_dates))], g.mov_avg, linewidth=2.0)
        ax2.set_xticks(g.xticks)    
        ax2.set_xticklabels(g.x_labels, rotation='vertical')
        ax1.grid()
        ax2.yaxis.grid()
        plt.subplots_adjust(left=0.05, bottom=0.2)
        pp.savefig()
        pp.close()
