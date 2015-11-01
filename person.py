class Person:
  def __init__(self, full_name, email):
    split_name = full_name.split(' ')
    self.first_name = split_name[0]
    self.last_name = split_name[1]
    self.full_name = full_name
    self.email = email