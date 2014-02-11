from google.appengine.ext import ndb

class TaxRatio(ndb.Model):
    user = ndb.StringProperty()
    ratio = ndb.FloatProperty()
    year = ndb.IntegerProperty()

    def __str__(self):
        return 'user "%s" ratio %f year %d' % (self.user, self.ratio, self.year)
