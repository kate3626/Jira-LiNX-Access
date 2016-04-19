"""
Create a json file containing the work left to do per component and version and the total work done in LiNX Access.
Json file is not created but updated from an existing json file.
The python3 script LA_longterm_graph.py can be used to graph the information created in the json file
No command line arguments needed. -h will give the current versions, components and file name that is being used.
Author: Kate Olsen 
Date: 19/04/2016
"""

import time
import json
import os.path
import sys
import argparse
from jira.client import JIRA
jira = JIRA(server="http://jiraprod1.au.ivc")

class Info(object):
    def __init__(self):
        self.main_dict = {}
        self.versions = []
        self.components = []
        self.version_sort = {}
        self.done = {}
        
    def set_version(self):
        self.versions = ['3.0', '3.0.1', '3.1']
    
    def set_components(self):
        self.components = ['PC', 'iOS']
    
    def __dic__(self):
        """ Gets a dictionary of the wanted epics and the stories that are linked to them. """
        self.main_dict = {}
        e = set()
        everything = jira.search_issues('project="LiNX Access" and type="Story"', maxResults = 800)
        stories = set()
        for issue in everything:
            stories.add(issue.key)
        for component in self.components:
            self.main_dict[component] = {}
        for story in stories:
            epic_code = jira.issue(story).fields.customfield_10006
            try: # Check for approved component and version.
                if epic_code != None and (jira.issue(epic_code).fields.components[0].name).split()[0] in self.components \
                and (jira.issue(epic_code).fields.fixVersions[0].name).split()[-1] in self.versions:
                    e.add(epic_code)
                    if epic_code not in self.main_dict[(jira.issue(epic_code).fields.components[0].name).split()[0]].keys():
                        self.main_dict[(jira.issue(epic_code).fields.components[0].name).split()[0]][epic_code] = [story]
                    else:
                        self.main_dict[(jira.issue(epic_code).fields.components[0].name).split()[0]][epic_code].append(story)
            except TypeError:
                pass
            except IndexError:
                pass

    def versionDoneSort(self):
        """ First organsises epics into versions. Then adds story points left to do per version/component and 
        story points done per component. """
        self.version_sort = {}
        versions = {}
        self.done = {}
        for component in self.components:
            epics = self.main_dict[component].keys()
            versions[component] = {}
            self.done[component] = 0
            self.version_sort[component] = {}
            for epic in epics: 
                version  = (jira.issue(epic).fields.fixVersions[0].name).split()[-1]
                if version not in versions[component].keys():
                    versions[component][version] = [epic]
                else:
                    versions[component][version].append(epic)
            for version in versions[component].keys():
                epics = versions[component][version]
                num = 0
                for epic in epics:
                    nd_num = 0
                    d_num = 0
                    all_Done = True 
                    stories = self.main_dict[component][epic]
                    epic_points = jira.issue(epic).fields.customfield_10014
                    for story in stories:
                        storystatus = jira.issue(story).fields.status.name
                        points = jira.issue(story).fields.customfield_10002
                        if points != None:
                            if storystatus == "Done" or storystatus == 'Resolved' or storystatus == 'Closed':
                                self.done[component] += points
                                d_num += points
                            else: 
                                nd_num += points
                                all_Done = False
                    if epic_points != None and (d_num + nd_num) < epic_points and all_Done == False:
                        num += epic_points - d_num
                    else:
                        num += nd_num
                self.version_sort[component][version] = num
    
    def json_dict(self, component):
        """ Gets the dictionary format needed for the json file. """
        end_dict = {}
        end_dict['done'] = self.done[component]
        for version in self.versions:
            end_dict[version] = self.version_sort[component][version]
        return end_dict
            
                
if __name__ == "__main__":  
    file_name = 'LA_progress.json'
    x = Info()
    x.set_components()
    x.set_version()
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--components', help=str(x.components)) # Doesn't work properly just desplays with the help message.
    parser.add_argument('-v', '--versions', help=str(x.versions))
    parser.add_argument('-f', '--file name', help=file_name)
    args = parser.parse_args()     
    x.__dic__()
    x.versionDoneSort()
    print(x.main_dict)
    with open(file_name, 'r') as cat:
        big_dict = json.load(cat)    
    date = time.strftime("%Y/%m/%d")
    dates_in_dict = list(big_dict[x.components[0]].keys())
    if date in dates_in_dict:
        for component in x.components:
            del big_dict[component][date]
    for component in x.components:
        big_dict[component][date] = x.json_dict(component)
    with open(file_name, 'w') as cat:
        cat.write(json.dumps(big_dict))    