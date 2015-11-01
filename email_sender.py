from email_composer import EmailComposer

class EmailSender:
  
  def __init__(self):
    self.email_composer = EmailComposer()

  def send_first_email(self, service, people):
    thread_ids = []
    for i in range(len(people)):
      body = self.email_composer.first_email_body(people, i)
      message = self.send_email(service, body)
      thread_id = message['threadId']
      thread_ids.append(thread_id)
    return thread_ids

  def send_second_email(self, service, company):
    body = self.email_composer.second_email_body(company)    
    message = self.send_email(service, body)
    thread_id = message['threadId']
    return thread_id

  # TODO  
  def send_third_email(self, service, company):
    pass
    # ???
    # body = third_email_body(company)
    # message = send_email(service, body)
    # threadId = message['threadId']
    # return thread_id

  @staticmethod  
  def send_email(service, body):
    try:
      message = (service.users().messages().send(userId="me", body=body).execute())
      print('Message Id: %s' % message['id'])
      return message
    except Exception as error:
      print('An error occurred: %s' % error)
      return {}