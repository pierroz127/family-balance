from google.appengine.ext import ndb

class Balance(ndb.Model):
    debtor = ndb.StringProperty()
    incredit = ndb.StringProperty()
    amount = ndb.FloatProperty()
    month = ndb.IntegerProperty()
    year = ndb.IntegerProperty()
