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
        self.component_versions = {}
        self.version_sort = {}
        self.done = {}
        self.components = []
        
    def set_component_versions(self):
        self.component_versions = {'PC': ['3.0', '3.0.1', '3.1'],
                                   'iOS': ['3.0', '3.0.1', '3.1']}
    def set_component(self):
        self.components = ['PC', 'iOS']
    
    def __dic__(self):
        """ Gets a dictionary of the wanted epics and the stories that are linked to them. """
        self.main_dict = {}
        everything = jira.search_issues('project="LiNX Access" and type="Story"', maxResults = 800)
        stories = set()
        for issue in everything:
            stories.add(issue.key)
        for component in self.components:
            self.main_dict[component] = {}
        for story in stories:
            epic_code = jira.issue(story).fields.customfield_10006
            try: # Check for approved component and version.
                if epic_code != None:
                    component = (jira.issue(epic_code).fields.components[0].name).split()[0]
                    version = (jira.issue(epic_code).fields.fixVersions[0].name).split()[-1]
                    if component in self.components and version in self.component_versions[component]:
                        if epic_code not in self.main_dict[component].keys():
                            self.main_dict[component][epic_code] = [story]
                        else:
                            self.main_dict[component][epic_code].append(story)
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
                if version not in versions[component].keys() and version in self.component_versions[component]:
                    versions[component][version] = [epic]
                elif version in self.component_versions[component]:
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
        for version in self.component_versions[component]:
            end_dict[version] = self.version_sort[component][version]
        return end_dict
            
                
if __name__ == "__main__":  
    file_name = 'LA_progress.json'
    x = Info()
    x.set_component_versions()
    x.set_component()
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--PC', help=str(x.component_versions['PC']))
    parser.add_argument('-i', '--iOS', help=str(x.component_versions['iOS']))
    parser.add_argument('-f', '--file name', help=file_name)
    args = parser.parse_args()     
    x.__dic__()
    x.versionDoneSort()
    with open(file_name, 'r') as cat:
        big_dict = json.load(cat)    
    date = time.strftime("%Y/%m/%d")
    dates_in_dict = set()
    for component in x.components:
        dates_in_dict = dates_in_dict | big_dict[component].keys()
    if date in dates_in_dict:
        for component in x.components:
            del big_dict[component][date]
    for component in x.components:
        big_dict[component][date] = x.json_dict(component)
    with open(file_name, 'w') as cat:
        cat.write(json.dumps(big_dict))    