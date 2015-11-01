from company import Company
from person import Person

import pickle
import re

class CompanyIO:

  def load_companies(self):
    try:
      with open('companies.pickle', 'rb') as handle:
        return pickle.load(handle)
    except Exception, e:
      return []

  def load_new_companies(self, filename):
    companies = []

    regex = re.compile("[><]")
    try:
      f = open(filename, 'r')
    except Exception, e:
      return companies

    for line in f:
      people = []
      data = regex.split(line.strip())
      for i in xrange(0, len(data) - 1, 2):
        full_name = data[i].strip()
        email = data[i + 1].strip()
        person = Person(full_name, email)
        people.append(person)
      company = Company(people)
      companies.append(company)

    return companies

  def save_companies(self, companies):
    with open('companies.pickle', 'wb') as handle:
      pickle.dump(companies, handle)