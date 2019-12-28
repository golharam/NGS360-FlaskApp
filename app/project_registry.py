'''
Interface to Project Registry
'''
from urllib.request import urlopen
from urllib.error import URLError
import json

from flask import current_app

def get_projects(project_registry_url, fields=None):
    '''
    Returns a list of projects from Project Registry as dictionaries.
    :param fields: list of fields to return.   If None, return everything.
    :return: list of project dicts
    '''
    project_list = []
    if project_registry_url is None:
        return project_registry_url

    projects = dict(data=[])
    try:
        response = urlopen(project_registry_url)
    except URLError:
        #current_app.logger.error(error)
        #current_app.logger.error("Unable to open %s", project_registry_url)
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
