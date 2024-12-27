import requests
import json
from datetime import datetime, timedelta
from calendar import monthrange

# Set your Zendesk API credentials
zendesk_subdomain = 'omshealthhelp'
zendesk_email = 'matthew.silbernagel@omshealth.com'
zendesk_password = 'RisenSan_@99'

# Get the current month and year
current_date = datetime.now()
current_month = current_date.strftime('%B')
current_year = current_date.strftime('%Y')

#calc prev month 
last_month_date = current_date - timedelta(days=current_date.day)
previous_month = last_month_date.strftime('%B')

#calc next month
first_day_next_month = current_date.replace(day=1) + timedelta(days=32)
next_month = first_day_next_month.strftime('%B')


#task define
tasks = [
    f'CIS - {current_month} - {current_year} | Unsigned Progress Note',
    f'MCI - {current_month} - {current_year} | Unsigned Progress Note',
    f'CIS - {current_month} - {current_year} | Missing Photo',
    f'MCI - {current_month} - {current_year} | Missing Photo',
    f'CIS - {current_month} - {current_year} | Patient Portal App',
    f'MCI - {current_month} - {current_year} | Patient Portal App',
    f'CIS - {current_month} - {current_year} | US and Echo Reports',
    f'MCI - {current_month} - {current_year} | US and Echo Reports',
    f'CIS - {current_month} - {current_year} | EKG Log',
    f'MCI - {current_month} - {current_year} | EKG Log',
    f'CIS - {current_month} - {current_year} | Active MD\'s List', 
    f'MCI - {current_month} - {current_year} | Active MD\'s List',
    f'CIS - {current_month} - {current_year} | Outstanding Diagnostic Reports',
    f'MCI - {current_month} - {current_year} | Outstanding Diagnostic Reports',
    f'CIS - {current_month} - {current_year} | SmartForm Report',
    f'MCI - {current_month} - {current_year} | SmartForm Report'  
]

# Authenticate with Zendesk API
auth = (zendesk_email, zendesk_password)

# Zendesk API endpoint for creating a ticket
zendesk_endpoint = f'https://{zendesk_subdomain}.zendesk.com/api/v2/tickets.json'

#Create tickets for each task
for task in tasks:
    print(f'Processing task: {task}')
    if task.startswith('CIS'):
        organization_id = '12003244978573'
    elif task.startswith('MCI'):
        organization_id = '12003240942221'
    else:
        organization_id = None

    # Create the ticket data
    report_data = {
        'subject': f'Monthly Report Request - {task}',
        'description': f'Please generate the monthly report for {task}.',
        'priority': 'normal',
        'status': 'open',
        'tags': ['monthly-report'],
        'group_id': 12794984274957,
        'assignee_id': 12038185622157,
        'collaborator_ids': [12715066125197],
        'requester_id': 12839787664141,
        'ticket_form_id': 11942014996109,
        'custom_fields': [
            {'id': 11945857165837, 'value': 'EHR'}
        ]
    }

    # Create a ticket in Zendesk
    response = requests.post(zendesk_endpoint, data=json.dumps({'ticket': report_data}), auth=auth, headers={'Content-Type': 'application/json'})

if response.status_code == 201:
    print(f"Zendesk ticket created successfully with ID: {response.json()['ticket']['id']}")
else:
    print(f"Failed to create Zendesk ticket. Status code: {response.status_code}, Error: {response.text}")
