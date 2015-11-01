from email_sender import EmailSender

import time

SECONDS_ONE_HOUR = 3600
SECONDS_ONE_DAY = SECONDS_ONE_HOUR * 24
SECONDS_ONE_WEEK = SECONDS_ONE_DAY * 7
SECONDS_ONE_MONTH = SECONDS_ONE_WEEK * 4

NO_EMAIL = 0
FIRST_EMAIL_SENT = 1
SECOND_EMAIL_SENT = 2
THIRD_EMAIL_SENT = 3
GOT_RESPONSE = 4
NO_RESPONSE = 5

DEBUG = True

class Company:

  def __init__(self, people):
    self.people = people
    self.company_state = NO_EMAIL
    self.last_updated = time.time()
    self.email_sender = EmailSender()

  def increment_state(self, service):
    if self.company_state == NO_EMAIL:
      self.handle_no_email_sent(service)
    elif self.company_state == FIRST_EMAIL_SENT:
      self.handle_first_email_sent(service)
    elif self.company_state == SECOND_EMAIL_SENT:
      self.handle_second_email_sent(service)
    elif self.company_state == THIRD_EMAIL_SENT:
      self.handle_third_email_sent(service)

  def handle_no_email_sent(self, service):
    self.thread_ids = self.email_sender.send_first_email(service, self.people)
    self.company_state = FIRST_EMAIL_SENT

  def handle_first_email_sent(self, service):
    if not self.did_get_response(service):
      if self.did_enough_time_pass():
        thread_id = self.email_sender.send_second_email(service, self.people, self.thread_ids[-1])
        self.thread_ids.append(thread_id)
        self.company_state = SECOND_EMAIL_SENT
    else:
      self.company_state = GOT_RESPONSE

  def handle_second_email_sent(self, service):
    if True: #not self.did_get_response(service):
      if self.did_enough_time_pass():
        thread_id = self.email_sender.send_third_email(service, self.people, self.thread_ids[-1])
        self.thread_ids.append(thread_id)
        self.company_state = THIRD_EMAIL_SENT
    else:
      self.company_state = GOT_RESPONSE

  def handle_third_email_sent(self, service):
    if not self.did_get_response(service):
      if self.did_enough_time_pass():
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
    elif self.company_state == THIRD_EMAIL_SENT:
      if time.time() - self.last_updated > SECONDS_ONE_MONTH:
        self.last_updated = time.time()
        return True
    return False

  def did_get_response(self, service):
    for thread_id in self.thread_ids:
      if self.did_get_response_for_thread_id(service, thread_id):
        return True
    return False
  
  def did_get_response_for_thread_id(self, service, thread_id):
    thread = service.users().threads().get(userId="me", id=thread_id).execute()
    return len(thread['messages']) > 1
