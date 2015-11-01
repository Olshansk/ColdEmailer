import base64

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

OLSHANSKY_EMAIL = "olshansky.daniel@gmail.com"
IGORS_EMAIL = ""

class EmailComposer:

  def first_email_body(self, people, i):
    people_mentioned = self.list_with_elem_at_index_i_removed(people, i)
    names = [person.full_name for person in people_mentioned]
    concatted_names = self.concat_names(names)

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

  def second_email_body(self, people, thread_id):
    emails = [person.email for person in people]
    names = [person.first_name for person in people]
    concatted_names = self.concat_names(names)

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

    return {'raw': base64.urlsafe_b64encode(msg.as_string()), 'threadId': thread_id}

  # TODO
  def third_email_body(self, people, thread_id):
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

  @staticmethod
  def concat_names(names):
    if len(names) == 1:
        return names[0]
    elif len(names) == 2:
        return "{} and {}".format(names[0], names[1])
    else:
        return "{} and {}".format(', '.join(names[0:-1]), names[-1])

  # Note, call to this method assumes list size is > 1
  @staticmethod
  def list_with_elem_at_index_i_removed(l, i):
    return l[:i] + l[i+1:]