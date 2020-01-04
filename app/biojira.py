import os
from jira import JIRA
from flask import current_app

def addCommentToIssues(biojira, comment, issues):
    '''
    Add a comment to a list of Jira tickets
    :param comment: Comment to add
    :param issues: List of Jira issues
    :return: List of Jira issue keys from issues
    '''
    issue_keys = []
    for issue in issues:
        biojira.add_comment(issue, comment)
        issue_keys.append(issue.key)
    return issue_keys

def getJira():
    # Connect to Jira
    '''
    options = { 'server': jira_config.server }
    privateKeyFile = jira_config.privateKeyFile
    key_cert_data = None
    with open(privateKeyFile, 'r') as key_cert_file:
            key_cert_data = key_cert_file.read()
    oauth_dict = {
        'access_token': jira_config.access_token,
        'access_token_secret': jira_config.access_token_secret,
        'consumer_key': jira_config.consumer_key,
        'key_cert': key_cert_data
    }
    return JIRA(options, oauth=oauth_dict)
    '''
    if current_app['JIRA_SERVER'] is not None and current_app['JIRA_USER'] is not None and \
       current_app['JIRA_PASSKEY'] is not None:
        return JIRA(options = {'server': current_app['JIRA_SERVER']},
                    basic_auth = (current_app['JIRA_USER'], current_app['JIRA_PASSKEY']))
    return None

def getTBioPMJiraIssues(biojira, projectid):
    '''
    Return Jira TBIOPM epic ticket associated with this project ID.
    If no epic ticket exists, return the tasks with this project ID.
    If no tasks exist, create one issue.
    '''
    if not biojira:
        return None

    jira_board = current_app['JIRA_BOARD']

    issues = biojira.search_issues('project="%s" and "Project ID"="%s" and issuetype="Epic"' % (jira_board, projectid))
    if not issues:
        issues = biojira.search_issues('project="%s" and "Project ID"="%s" and issuetype="Task"' % (jira_board, projectid))
    if not issues:
        issue = biojira.create_issue(project=jira_board,
                                     summary=projectid,
                                     description='Tracking NGS Data for %s' % projectid,
                                     issuetype={'name': 'Task'})
        if issue:
            issue.update(fields={current_app['JIRA_PROJECTID_FIELD']: [projectid]})
            issues = [issue]
    return issues

