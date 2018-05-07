# -*- coding: utf-8 -*-

# Imports ##############################################
from requests import get
import json
import datetime
from datetime import date
import time
from time import sleep

from dateutil.relativedelta import *

class ZohoReader():
    def __init__(self, authtoken, portal_id):
        self.authtoken = authtoken
        self.portal_id = portal_id

        self.request_range = 100
        self.SLEEP_TIME = 3


    def get_projects_list(self):
        '''
        Extract a list of active projects from zoho and save to database
        '''
        request_index = 1

        project_list = []
        # Url to zoho projects API
        url = "https://projectsapi.zoho.com/restapi/portal/{}/projects/".format(self.portal_id)

        while True:
            params = {"authtoken":self.authtoken,
                    "index":request_index,
                    "range":self.request_range,
                    'status':'active'}

            # Make the request
            r_p = get(url, params=params)

            # Reply contains data
            if r_p.status_code == 200:

                # Get the next 100 in the next loop
                request_index += self.request_range

                contents = json.loads(r_p.content)['projects']

                for content in contents:

                    project_list.append({'id':content['id'],
                                   'name':content['name'],
                                   'created_date':content['created_date'],
                                   'updated_date':content['updated_date'],
                                   'owner_id':content['owner_id']})

                # Don't overload zoho's fragile API...
                time.sleep(self.SLEEP_TIME)

            elif r_p.status_code == 204:
                # If reply is empty, just end the while loop
                break

            else:
                print("Bad request: %s" % r_p.status_code) # Error could be more informative, but meh...
                break


        return project_list


    def get_users_list(self):
        '''
        Go through all projects in list, return a list of unique users
        '''
        user_list = []

        request_index=1

        url = "https://projectsapi.zoho.com/restapi/portal/{}/users/".format(
                self.portal_id)

        # Run loop until nothing is returned or bad request.
        while True:
            # Each request need a token, an index and a range for each request.
            params = {"authtoken":self.authtoken,
                    "index":request_index,
                    "range":self.request_range}

            # Get content from zoho
            r_p = get(url, params=params)

            # IMPORTANT, don't flood the API, max 100 request / 120 sec.
            sleep(self.SLEEP_TIME)

            # status code 200 means a result is returned, 204 is an empty reply.
            if r_p.status_code == 200:
                # After each request increase the starting point
                request_index += self.request_range

                # Define columns to save
                cols=['id', 'name', 'email']
                users = json.loads(r_p.content)['users']

                # Append all users to the user_list
                for user in users:
                    user_list.append({'name':user['name'],
                        'id':user['id'],
                        'email':user['email'],
                        'role':user['role'],
                        'active':user['active']})

            elif r_p.status_code == 204:
                # If reply is empty, just end the while loop
                break
            else:
                print("Bad request: {}".format(r_p.content)) # Error could be more informative, but meh...
                break

        return user_list

    def convert_timelog_data(self, day, project_id, project_name):
        timelogs_list = []

        def internal_taskloop(index, f):
            rows = []

            rows.append({'id':f['id'],
                       'project_id':project_id,
                       'project_name':project_name,
                       'date':day['date'], #[index],
                       'user':f['owner_name'],
                       'user_id':f['owner_id'],
                       'total_minutes':f['total_minutes'],
                       'task_id':f['task']['id'],
                       'task_name':f['task']['name'],
                       'notes':f['notes'],
                       'bill_status':f['bill_status']})

            return rows

        def internal_generalloop(index, e):
            rows=[]

            rows.append({'id':f['id'],
                       'project_id':project_id,
                       'project_name':project_name,
                       'date':day['date'], #[index],
                       'user':f['owner_name'],
                       'user_id':f['owner_id'],
                       'total_minutes':f['total_minutes'],
                       'task_id':'0001', # fake task_id
                       'task_name':f['name'],
                       'notes':f['notes'],
                       'bill_status':f['bill_status']})

            return rows

        # Check if day is not empty, the adjust for general vs task
        if day:
            if 'tasklogs' in day:
                for index, e in enumerate(day['tasklogs']):
                    timelogs_list.extend(internal_taskloop(index, e))

            elif 'generallogs' in day:
                for index, e in enumerate(day['generallogs']):
                    timelogs_list.extend(internal_generalloop(index, e))
            else:
                print('unknown timelog, check debug')
                pass

        return timelogs_list


    def get_all_project_timelogs(self, project_id, project_name, created_date):
        '''
        Get all timelogs for a single project
        '''

        timelog_list = []

        # go through each type
        component_types = ['task', 'general']

        # Go through different component types
        for comp_type in component_types:
            loop_date = datetime.datetime.strptime(created_date, '%m-%d-%Y') # Set start date for date loop

            # Loop through dates
            while loop_date < datetime.datetime.today():
                # Reset req. index
                request_index = 1

                #Update the loop date
                loop_date += relativedelta(months=1)

                # Request range of projects list
                while True:

                    url = "https://projectsapi.zoho.com/restapi/portal/{}/projects/{}/logs/".format(self.portal_id, project_id)

                    params = {"authtoken":self.authtoken,
                            "index":request_index,
                            "range":self.request_range,
                            'users_list':'all',
                            'view_type': 'month',
                            'date': datetime.datetime.strftime(loop_date, '%m-%d-%Y'),
                            'bill_status': 'all',
                            'component_type': comp_type
                            }

                    # Make the request
                    r_p = get(url, params=params)

                    if r_p.status_code == 200:

                        request_index += self.request_range

                        days = json.loads(r_p.content)['timelogs']['date']

                        for day in days:

                            timelog_list.extend(self.convert_timelog_data(day, project_id, project_name))

                    elif r_p.status_code == 204:
                        # If reply is empty, just end the while loop
                        break
                    else:
                        "Bad request: %s" % r_p.status_code  # Error could be more informative, but meh...
                        break

                    sleep(self.SLEEP_TIME)

            return timelog_list


    def get_all_timelogs(self, projects_list):

        total_timelogs = []

        # Get all timelogs from all projects
        for index, project in enumerate(projects_list):

            total_timelogs.extend(self.get_all_project_timelogs(project['id'],
                                                           project['name'],
                                                           project['created_date']))

        return total_timelogs # total_timelogs
