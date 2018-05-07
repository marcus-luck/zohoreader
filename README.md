# zohoreader
This project is intended to create an easy way to get all timelogs from zoho projects API.

### Information

The package returns a list of all timelogs. Can easily be converted to a Pandas DataFrame.


### Using


Import the package

```
from zohoreader import ZohoReader
```

Use api key from wunderground.

```
zr = ZohoReader('authtoken', 'portal_id')
```

Get list of all all projects

```
project_list = zr.get_projects_list()
```

Get all Users

```
users_list = wr.get_users_list(self)
```

Get timelogs from project

```
output = zr.get_all_project_timelogs('project_id', 'project_name', 'created_date'):

```

Get all timelogs from all projects

```
timelogs = zr.get_all_timelogs(projects_list)
```

### License

This project is licensed under the MIT License
