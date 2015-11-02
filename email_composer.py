import base64

from datetime import datetime as dt

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import random

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
    msg['To'] = people[i].email
    msg['From'] = OLSHANSKY_EMAIL
    # msg['From'] = IGORS_EMAIL
    msg['Subject'] = "Appropriate Person"
    msg.attach(MIMEText(html, 'html'))

    return {'raw': base64.urlsafe_b64encode(msg.as_string())}

  def second_email_body(self, people, thread_id, thread):
    emails = [person.email for person in people]
    names = [person.first_name for person in people]
    concatted_names = self.concat_names(names)

    f = open('templates/template2', 'r')
    html = f.read().format(concatted_names, random.random())
    html += self.get_quoted_text([thread['messages'][-1]])

    msg = MIMEMultipart()
    msg['To'] = ', '.join(emails)
    msg['From'] = OLSHANSKY_EMAIL
    # msg['From'] = IGORS_EMAIL
    msg['Subject'] = "Re: Appropriate Person"
    msg.attach(MIMEText(html, 'html'))

    return {'raw': base64.urlsafe_b64encode(msg.as_string()), 'threadId': thread_id}

  def third_email_body(self, people, thread_id, thread):
    emails = [person.email for person in people]
    name = people[0].first_name # TODO: make sure you use the right person's name here

    f = open('templates/template3', 'r')
    html = f.read().format(name, random.random())
    html += self.get_quoted_text([thread['messages'][-1]])

    msg = MIMEMultipart()
    msg['To'] = ', '.join(emails)
    msg['From'] = OLSHANSKY_EMAIL
    # msg['From'] = IGORS_EMAIL
    msg['Subject'] = "Permission to Close Your File"    
    msg.attach(MIMEText(html, 'html'))

    return {'raw': base64.urlsafe_b64encode(msg.as_string()), 'threadId': thread_id}

  # I did not realize that the last message will have everything prior already quoted,
  # so in the meantiome, you have to alle this method as so: self.get_quoted_text([thread['messages'][-1]])
  # rather than self.get_quoted_text(thread['messages'])
  # TODO: fix ^^ later
  def get_quoted_text(self, messages):
    if len(messages) == 0:
      return ""

    message = messages.pop(0)
    headers = message['payload']['headers']

    # TODO: Get the right name without hard coding
    name = "Daniel Olshansky"
    
    # Get the right email
    email = self.get_value_from_headers_for_key(headers, 'From')

    # Get the rigth date
    date_raw = self.get_value_from_headers_for_key(headers, 'Date')
    date_raw_split = date_raw.split(' ')
    time_raw = date_raw_split[4]
    time_object = dt.strptime(time_raw, '%H:%M:%S')
    time_reformatted = dt.strftime(time_object, '%I:%M %p')
    day_and_month = ' '.join(date_raw_split[0:4])
    date_reformatted = "On {} {}, {}".format(day_and_month, time_reformatted, name)

    # Get html from current message
    html_from_message = base64.urlsafe_b64decode(message['payload']['parts'][0]['body']['data'].encode("utf-8"))

    # Format the quoted text
    html = ""

    html += '<div class="im" style="color:#500050">'
    html += '<div class="gmail_extra">'
    html += '<div class="gmail_quote">'
    html += '<br>'

    html += date_reformatted
    html += '<span dir="ltr">&lt;<a href="mailto:{}" target="_blank">{}</a>&gt;</span> wrote:<br>'.format(email, email)

    html += '<blockquote class="gmail_quote" style="margin:0 0 0 .8ex;border-left:1px #ccc solid;padding-left:1ex">'
    html += html_from_message
    html += self.get_quoted_text(messages)
    html += '</blockquote>'

    html += '</div>'
    html += '</div>'
    html += '</div>'

    return html

  def get_value_from_headers_for_key(self, headers, key):
    return [header for header in headers if header['name'] == key][0]['value']

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