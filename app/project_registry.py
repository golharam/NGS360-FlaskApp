'''
Interface to Project Registry
'''
from urllib.request import urlopen
from urllib.error import URLError
import json

def get_projects(project_registry_url, fields=None):
    '''
    Returns a list of projects from Project Registry as dictionaries.
    :param fields: list of fields to return.   If None, return everything.
    :return: list of project dicts
    '''
    project_list = []
    if project_registry_url is None:
        return project_list

    projects = dict(data=[])
    try:
        response = urlopen(project_registry_url)
    except URLError:
        return project_list

    projects = json.load(response)

    if fields is None:
        return projects['data']

    for project in projects['data']:
        project_json = {}
        for field in fields:
            project_json[field] = project[field]
        project_list.append(project_json)
    return project_list

def get_project(project_registry_url, project):
    ''' Returns a dict of a specific project '''
    if project_registry_url is None:
        return None

    projects = dict(data=[])
    try:
        url = "%s?mode=get&func=project&format=json&projectid=%s" % (project_registry_url, project)
        response = urlopen(url)
    except:
        pass

    projects = json.load(response)
    if 'data' in projects:
        project = projects['data']
        if project:
            return project
    return None
