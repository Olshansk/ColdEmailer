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

  def send_second_email(self, service, people, thread_id):
    body = self.email_composer.second_email_body(people, thread_id)    
    message = self.send_email(service, body)
    return message['threadId']

  def send_third_email(self, service, people, thread_id):
    body = self.email_composer.third_email_body(people, thread_id)
    message = self.send_email(service, body)
    return message['threadId']

  @staticmethod  
  def send_email(service, body):
    try:
      message = (service.users().messages().send(userId="me", body=body).execute())
      print('Message Id: %s' % message['id'])
      return message
    except Exception as error:
      print('An error occurred: %s' % error)
      return {}