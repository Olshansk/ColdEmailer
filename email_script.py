# References:
# https://console.developers.google.com/project/igors-emails-1087
# https://developers.google.com/apis-explorer/?hl=en_US#p/gmail/v1/

from company import Company
from company_io import CompanyIO

import httplib2
import os
from apiclient import discovery

import oauth2client
from oauth2client import client
from oauth2client import tools

try:
  import argparse
  flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
  flags = None

SCOPES = "https://mail.google.com"
CLIENT_SECRET_FILE = "client_secret.json"
APPLICATION_NAME = "Igor's emails"

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
    credentials = tools.run_flow(flow, store, flags)
    print('Storing credentials to ' + credential_path)
  return credentials

def main():
  credentials = get_credentials()
  http = credentials.authorize(httplib2.Http())
  service = discovery.build('gmail', 'v1', http=http)

  company_io = CompanyIO()

  existing_companies = company_io.load_companies()
  new_companies = company_io.load_new_companies('new_companies')
  companies = existing_companies + new_companies
  
  for company in companies:
    company.increment_state(service)

  company_io.save_companies(companies)

  # To make sure that the same company doesn't recieve the email twice
  try:
    os.rename('new_companies', 'old_companies')
  except Exception, e:
    pass

if __name__ == '__main__':
  main()