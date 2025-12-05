"""
File: sqtool.py
Author: Joshua Pollaci
Date Created: 10-17-2025
Last Modified: 11-10-2025
Version: 2.2.4
Description: 
Script to manage suspended tickets from a Zendesk subdomain.
It retrieves all tickets currently in the suspended queue and filters them
based on predefined lists of sender email addresses. Tickets are either recovered
or deleted depending on whether the sender's email or email domain matches an entry in the
"ALLOW_LIST", "ALLOW_DOMAIN", "DENY_LIST" or "DENY_DOMAIN" lists found in allow_or_deny_lists.py. 
This helps automate the cleanup and restorationof legitimate support requests while removing spam or irrelevant messages.

"""

import requests
from requests.auth import HTTPBasicAuth
import os
#Imports the allow and deny lists from allow_or_deny.py
from allow_or_deny_lists import ALLOW_LIST, DENY_LIST, ALLOW_DOMAIN, DENY_DOMAIN

#Zendesk subdomain 
ZENDESK_SUBDOMAIN = os.getenv('ZENDESK_SUBDOMAIN')
#Headers
HEADERS = {
	"Content-Type": "application/json",
}
#Credentials: email and token 
EMAIL = os.getenv('ZENDESK_EMAIL')
TOKEN = os.getenv('ZENDESK_TOKEN')
#Authentication necessary for API calls
AUTH = HTTPBasicAuth(f'{EMAIL}/token', TOKEN)

#Maximum amount of tickets you can recover or delete at a time
MAX_CAPACITY = 100
#Cause ID for the suspended queue for blocklisted emails
BLOCKLIST_ID = 13

def recoverTickets(recover_list):
    '''
    Sends PUT request in order to recover all tickets created by allowlisted emails
    
    Args:
        recover_list: The list of ticket id's to recover
    '''
    if not all([ZENDESK_SUBDOMAIN, EMAIL, TOKEN]):
        print("Error: Zendesk credentials not fully configured.")
        return []
    rec_url = f"https://{ZENDESK_SUBDOMAIN}.zendesk.com/api/v2/suspended_tickets/recover_many?ids={','.join([str(num) for num in recover_list])}"
    try:
        rec_response = requests.request("PUT", rec_url, auth = AUTH, headers=HEADERS)
        print(rec_response.text)
        print("Recovered Tickets Successfully")
    except requests.exceptions.RequestException as e:
            print(f"Error making API request: {e}")
            
def deleteTickets(delete_list):
    '''
    Sends DELETE request in order to delete all tickets created by blocklisted emails
    
    Args:
        delete_list: The list of ticket id's to delete
    '''   
    del_url = f"https://{ZENDESK_SUBDOMAIN}.zendesk.com/api/v2/suspended_tickets/destroy_many?ids={','.join([str(num) for num in delete_list])}"
    try:
        del_response = requests.request("DELETE", del_url, auth = AUTH, headers=HEADERS)
        print("Deleted Tickets Successfully")
        print(del_response.text)
    except requests.exceptions.RequestException as e:
            print(f"Error making API request: {e}")

def update_recover(recovery_list, id):
    '''
    Updates the recovery_list by appending the ticket id. if the length of the list reaches MAX_CAPACITY, 
    the function recoverTickets will be called and the list will be cleared

    
    Args:
        recovery_list: The list of ticket id's to recover
        id: the id of the ticket to append
    Return:
        100 if MAX_CAPACITY is reached, else return 0
    ''' 
    recovery_list.append(id)
    if len(recovery_list) == MAX_CAPACITY:
        recoverTickets(recovery_list)
        recovery_list.clear()
        return 100
    return 0

def update_delete(delete_list, id):
    '''
    Updates the delete_list by appending the ticket id. if the length of the list reaches MAX_CAPACITY, 
    the function deleteTickets will be called and the list will be cleared

    Args:
        delete_list: The list of ticket id's to recover
        id: the id of the ticket to append
    Return:
        100 if MAX_CAPACITY is reached, else return 0
    ''' 
    delete_list.append(id)
    if len(delete_list) == MAX_CAPACITY:
        deleteTickets(delete_list)
        delete_list.clear()
        return 100
    return 0
  
def main():
    #url to make GET API call for suspended tickets
    url = f"https://{ZENDESK_SUBDOMAIN}.zendesk.com/api/v2/suspended_tickets"
    #List to store suspended tickets
    suspended_tickets = []
    #Checks if all necessary components to make API call are present
    if not all([ZENDESK_SUBDOMAIN, EMAIL, TOKEN]):
        print("Error: Zendesk credentials not fully configured.")
        return []
    #Loops until all suspended queue pages are stored in suspended_tickets 
    while url:
        try:
            response = requests.request("GET", url, auth=AUTH, headers=HEADERS)
            response.raise_for_status()
            data = response.json()
            suspended_tickets.extend(data['suspended_tickets'])
            url = data['next_page']
        except requests.exceptions.RequestException as e:
            print(f"Error making API request: {e}")
            break
        except KeyError as e:
            print(f"Error parsing API response: Missing Key {e}")
            break
    print(suspended_tickets)
    #Variables to track how many tickets are recovered or deleted
    recovered, deleted = 0, 0
    #Lists of ticket ids to recover or delete
    recover_list, delete_list = [], []
    #Loops through suspended_tickets to filter whether the ticket needs to be deleted or recovered
    for ticket in suspended_tickets:
        author = ticket['author']
        if ticket['cause_id'] == BLOCKLIST_ID or author['email'] in DENY_LIST:
            count = update_delete(delete_list, ticket['id'])
            deleted += count
        elif author['email'] in ALLOW_LIST:
            count = update_recover(recover_list, ticket['id'])
            recovered += count
        else:
            #Loops through domains to check if email's domain is in the allow or deny list for domains
            for email in ALLOW_DOMAIN:
                if email in author['email']:
                    print(f"\n{author['email']} contains {email}\n")
                    count = update_recover(recover_list, ticket['id'])
                    recovered += count
            for email in DENY_DOMAIN:
                if email in author['email']:
                    print(f"\n{author['email']} contains {email}\n")
                    count = update_delete(delete_list, ticket['id'])
                    deleted += count
    #Recovers or deletes the remaining tickets
    if len(recover_list) < MAX_CAPACITY and len(recover_list) > 0:
        recoverTickets(recover_list)
        recovered += len(recover_list)
    if len(delete_list) < MAX_CAPACITY and len(delete_list) > 0:
        deleteTickets(delete_list)
        deleted += len(delete_list)
    #Prints out total deleted and recovered tickets
    with open('log.txt', 'a') as file:
        file.write(f"\tRecovered: {recovered} Tickets\n\tDeleted: {deleted} Tickets\n")
    print(f"\nRecovered: {recovered} Tickets\nDeleted: {deleted} Tickets\n")
    
if __name__ == '__main__':
    main()