# References:
# https://console.developers.google.com/project/igors-emails-1087
# https://developers.google.com/apis-explorer/?hl=en_US#p/gmail/v1/

import getopt
import sys
import httplib2
import os
from apiclient import discovery
import time
import re
import base64

import oauth2client
from oauth2client import client
from oauth2client import tools

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import pickle

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

SCOPES = "https://mail.google.com"
CLIENT_SECRET_FILE = "client_secret.json"
APPLICATION_NAME = "Igor's emails"
OLSHANSKY_EMAIL = "olshansky.daniel@gmail.com"
IGORS_EMAIL = ""

NO_EMAIL = 0
FIRST_EMAIL_SENT = 1
SECOND_EMAIL_SENT = 2
THIRD_EMAIL_SENT = 3
GOT_RESPONSE = 4
NO_RESPONSE = 5

SECONDS_ONE_HOUR = 3600
SECONDS_ONE_DAY = SECONDS_ONE_HOUR * 24
SECONDS_ONE_WEEK = SECONDS_ONE_DAY * 7
SECONDS_ONE_MONTH = SECONDS_ONE_WEEK * 4

DEBUG = True

# Data structures
# ===============

class CompanyState:
    def __init__(self, people):
        self.people = people
        self.company_state = NO_EMAIL
        self.last_updated = time.time()

    def increment_company_state(self, service):
        if (self.company_state == NO_EMAIL):
            thread_ids = send_first_email(service, self.people)
            self.thread_ids = thread_ids
            self.company_state = FIRST_EMAIL_SENT
        elif self.company_state == FIRST_EMAIL_SENT:
            if self.should_send_followup_email(service):
                if self.did_enough_time_pass():
                    thread_id = send_second_email(service, self.people)
                    self.thread_ids.append(thread_id)
                    self.company_state = SECOND_EMAIL_SENT
            else:
                self.company_state = GOT_RESPONSE
        elif self.company_state == SECOND_EMAIL_SENT:
            if self.should_send_followup_email(service):
                if self.did_enough_time_pass():
                    thred_id = send_third_email(service, self.people)
                    # TODO: what to do with thread id?
                    self.company_state = THIRD_EMAIL_SENT
            else:
                self.company_state = GOT_RESPONSE
        elif self.company_state == THIRD_EMAIL_SENT:
            if self.should_send_followup_email(service):
                self.company_state = NO_RESPONSE
            else:
                self.company_state = GOT_RESPONSE

    def did_enough_time_pass(self):
        if DEBUG:
            return True

        if self.company_state == NO_EMAIL:
            self.last_updated = time.time()
            return True
        elif self.company_state == FIRST_EMAIL_SENT:
            if time.time() - self.last_updated > SECONDS_ONE_WEEK:
                self.last_updated = time.time()
                return True
        elif self.company_state == SECOND_EMAIL_SENT:
            if time.time() - self.last_updated > SECONDS_ONE_MONTH:
                self.last_updated = time.time()
                return True
        return False


    def should_send_followup_email(self, service):
        for thread_id in self.thread_ids:
            if self.did_email_get_response(service, thread_id):
                return False
        return True
    
    def did_email_get_response(self, service, thread_id):
        thread = service.users().threads().get(userId="me", id=thread_id).execute()
        if len(thread['messages']) > 1:
            return True
        else:
            return False    

class Person:
    def __init__(self, full_name, email):
        split_name = full_name.split(' ')
        self.first_name = split_name[0]
        self.last_name = split_name[1]
        self.full_name = full_name
        self.email = email

# IO files
# ===============

def save_company_states(company_states):
    with open('company_states.pickle', 'wb') as handle:
        pickle.dump(company_states, handle)

def load_company_states():
    try:
        with open('company_states.pickle', 'rb') as handle:
            return pickle.load(handle)
    except Exception, e:
        return []

def get_company_contacts(filename):
    companies = []

    regex = re.compile("[><]")
    try:
        f = open(filename, 'r')
    except Exception, e:
        return companies

    for line in f:
        company = []
        data = regex.split(line.strip())
        for i in xrange(0, len(data) - 1, 2):
            full_name = data[i].strip()
            email = data[i + 1].strip()
            person = Person(full_name, email)
            company.append(person)
        companies.append(company)

    return companies

# Helpers
# =======

def get_credentials():
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir, 'gmail-python-quickstart.json')

    store = oauth2client.file.Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatability with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

def list_with_elem_at_index_i_removed(l, i):
    return l[:i] + l[i+1:]

def concat_names(names):
    if len(names) == 1:
        return names[0]
    elif len(names) == 2:
        return "{} and {}".format(names[0], names[1])
    else:
        return "{} and {}".format(', '.join(names[0:-1]), names[-1])

# First Email
# ===========

def first_email_body(people, i):
    # Note, the call immidiately below assumes there's > 1 person in a company
    people_mentioned = list_with_elem_at_index_i_removed(people, i)
    names = [person.full_name for person in people_mentioned]
    concatted_names = concat_names(names)

    f = open('templates/template1', 'r')
    html = f.read().format(concatted_names)

    msg = MIMEMultipart()
    # msg['To'] = people[i].email
    # msg['From'] = IGORS_EMAIL
    print "would be sending to: {}".format(people[i].email)
    msg['To'] = OLSHANSKY_EMAIL
    msg['From'] = OLSHANSKY_EMAIL
    msg['Subject'] = "Appropriate Person"
    msg.attach(MIMEText(html, 'html'))

    return {'raw': base64.urlsafe_b64encode(msg.as_string())}

def send_first_email(service, people):
    thread_ids = []
    for i in range(len(people)):
        body = first_email_body(people, i)
        message = send_email(service, body)
        thread_id = message['threadId']
        thread_ids.append(thread_id)
    return thread_ids

# Second Email
# ===========

def second_email_body(company):
    emails = [person.email for person in company] 
    names = [person.first_name for person in company]
    concatted_names = concat_names(names)

    f = open('templates/template2', 'r')
    html = f.read().format(concatted_names)

    msg = MIMEMultipart()
    # msg['To'] = ', '.join(emails)
    # msg['From'] = IGORS_EMAIL
    print "would be sending to: {}".format(', '.join(emails))
    msg['To'] = OLSHANSKY_EMAIL
    msg['From'] = OLSHANSKY_EMAIL
    msg['Subject'] = "Re: Appropriate Person"
    msg.attach(MIMEText(html, 'html'))

    return {'raw': base64.urlsafe_b64encode(msg.as_string())}

def send_second_email(service, company):    
    body = second_email_body(company)    
    message = send_email(service, body)
    thread_id = message['threadId']
    return thread_id

# Third Email
# ===========

def third_email_body(company):
    f = open('templates/template3', 'r')
    html = f.read()

    msg = MIMEMultipart()
    # msg['To'] = ???
    # msg['From'] = IGORS_EMAIL
    msg['To'] = OLSHANSKY_EMAIL
    msg['From'] = OLSHANSKY_EMAIL
    msg['Subject'] = "Permission to Close Your File"
    
    msg.attach(MIMEText(html, 'html'))

    return {'raw': base64.urlsafe_b64encode(msg.as_string())}        

def send_third_email(service, company):
    pass
    # ???
    # body = third_email_body(company)
    # message = send_email(service, body)
    # threadId = message['threadId']
    # return thread_id

# Sending email
# =============

def send_email(service, body):
    try:
        message = (service.users().messages().send(userId="me", body=body).execute())
        print('Message Id: %s' % message['id'])
        return message
    except Exception as error:
        print('An error occurred: %s' % error)
        return {}

# Main
# ====

def main():
    # Setup authentication with gmail
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('gmail', 'v1', http=http)

    company_states = load_company_states()
    
    new_companies = get_company_contacts('new_companies')
    for new_company in new_companies:
        company_states.append(CompanyState(new_company))

    for company_state in company_states:
        company_state.increment_company_state(service)

    try:
        os.rename('new_companies', 'old_companies')
    except Exception, e:
        pass

    save_company_states(company_states)

if __name__ == '__main__':
    main()