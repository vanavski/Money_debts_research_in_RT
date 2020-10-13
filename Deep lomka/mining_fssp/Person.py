class Person(object):
    # region = None
    firstName = None
    lastName = None
    secondName = None
    birthday = None

    def __init__(self, firstName, lastName, secondName = None, birthday = None):
        # self.region = region
        self.firstName = firstName
        self.lastName = lastName
        self.secondName = secondName
        self.birthday = birthday