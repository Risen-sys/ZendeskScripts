import requests
import csv
import os
from datetime import datetime
import ttkbootstrap as ttkb
from ttkbootstrap.constants import *
from threading import Thread
from tkinter import messagebox

# Settings
auth = ('YOUR_EMAIL', 'PASS')
view_tickets = []
view_id = 'ticketViewID'

def get_requester_name(requester_id):
    response = requests.get(f'https://url.zendesk.com/api/v2/users/{requester_id}.json', auth=auth)
    if response.status_code == 200:
        user_data = response.json().get('user')
        return user_data.get('name', 'N/A')
    return 'N/A'

def get_ticket_form_name(ticket_form_id):
    response = requests.get(f'https://url.zendesk.com/api/v2/ticket_forms/{ticket_form_id}.json', auth=auth)
    if response.status_code == 200:
        form_data = response.json().get('ticket_form')
        return form_data.get('name', 'N/A')
    return 'N/A'

def get_organization_name(organization_id):
    response = requests.get(f'https://url.zendesk.com/api/v2/organizations/{organization_id}.json', auth=auth)
    if response.status_code == 200:
        org_data = response.json().get('organization')
        return org_data.get('name', 'N/A')
    return 'N/A'

def format_datetime(timestamp):
    if timestamp is not None:
        dt = datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%SZ')
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    return 'N/A'

from tkinter import messagebox

# Function to fetch and save tickets with messagebox notification
def fetch_and_save_tickets(progress_label, progress_bar):
    try:
        global view_tickets
        progress_label.config(text=f'Fetching tickets from view ID {view_id}...')
        url = f'https://url.zendesk.com/api/v2/views/{view_id}/tickets.json'

        while url:
            response = requests.get(url, auth=auth)
            if response.status_code != 200:
                progress_label.config(text=f'Error: Unable to fetch tickets. Status code: {response.status_code}')
                messagebox.showerror("Error", f"Unable to fetch tickets. Status code: {response.status_code}")
                return

            page_data = response.json()
            if 'tickets' in page_data:
                tickets = page_data['tickets']
                view_tickets.extend(tickets)
                url = page_data.get('next_page')
                if url is None:
                    break
            else:
                progress_label.config(text='Error: API response does not contain "tickets" key.')
                messagebox.showerror("Error", 'API response does not contain "tickets" key.')
                return

        if not view_tickets:
            progress_label.config(text=f'No tickets found for view ID {view_id}.')
            messagebox.showinfo("No Tickets", f"No tickets found for view ID {view_id}.")
            return

        rows = [('Ticket Status', 'ID', 'Ticket Form', 'Subject', 'Description', 'Requester', 'Requested', 'Last update', 'Organization')]

        for idx, ticket in enumerate(view_tickets):
            requester_id = int(ticket['requester_id'])
            requester_name = get_requester_name(requester_id)

            ticket_form_id = ticket.get('ticket_form_id')
            ticket_form_name = get_ticket_form_name(ticket_form_id) if ticket_form_id else 'N/A'

            organization_id = ticket.get('organization_id')
            organization_name = get_organization_name(organization_id) if organization_id else 'N/A'

            updated_at = format_datetime(ticket.get('updated_at'))

            row = (
                ticket['status'],
                ticket['id'],
                ticket_form_name,
                ticket['subject'],
                ticket['description'],
                requester_name,
                ticket['created_at'],
                updated_at,
                organization_name,
            )
            rows.append(row)

            progress_bar['value'] = (idx + 1) / len(view_tickets) * 100
            progress_label.config(text=f'Processing ticket {idx + 1} of {len(view_tickets)}')
            progress_bar.update()

        base_filename = 'all_tickets_for_view'
        file_extension = '.csv'
        desktop_path = os.path.expanduser("~/Desktop")
        output_path = os.path.join(desktop_path, base_filename + file_extension)

        counter = 1
        while os.path.exists(output_path):
            output_path = os.path.join(desktop_path, f'{base_filename}_{counter}' + file_extension)
            counter += 1

        with open(output_path, mode='w', newline='', encoding='utf-8') as csv_file:
            report_writer = csv.writer(csv_file, dialect='excel')
            for row in rows:
                report_writer.writerow(row)

        progress_label.config(text=f'CSV file saved as {output_path}')
        messagebox.showinfo("Success", f"Tickets saved to {output_path}")
    except Exception as e:
        progress_label.config(text=f'Error: {e}')
        messagebox.showerror("Error", str(e))


def start_fetching():
    fetch_thread = Thread(target=fetch_and_save_tickets, args=(progress_label, progress_bar))
    fetch_thread.start()

# GUI Setup
root = ttkb.Window(themename="darkly")
root.title("Ticket Fetcher")

frame = ttkb.Frame(root, padding=20)
frame.pack(fill=BOTH, expand=True)

header = ttkb.Label(frame, text="Zendesk Ticket Fetcher", font=("Helvetica", 18), anchor=CENTER)
header.pack(pady=10)

progress_label = ttkb.Label(frame, text="Ready", font=("Helvetica", 12), anchor=W)
progress_label.pack(fill=X, pady=5)

progress_bar = ttkb.Progressbar(frame, orient=HORIZONTAL, length=400, mode="determinate", bootstyle=INFO)
progress_bar.pack(pady=10)

start_button = ttkb.Button(frame, text="Start Fetching", bootstyle=SUCCESS, command=start_fetching)
start_button.pack(pady=20)

footer = ttkb.Label(frame, text="Powered by OMS", font=("Helvetica", 10), anchor=CENTER)
footer.pack(side=BOTTOM, pady=10)

root.mainloop()
