from google.appengine.ext import ndb
from datetime import datetime, date
from config import app_config
import logging

def expenses_key(month, year):
    """Constructs a Datastore key for a expenses entity with year and month."""
    return ndb.Key('monthly_expenses', str(year) + '#' + str(month))


class Expenses(ndb.Model):
    user = ndb.UserProperty()
    amount = ndb.FloatProperty()
    category = ndb.StringProperty()
    exptype = ndb.IntegerProperty()
    date = ndb.DateProperty()
    tags = ndb.StringProperty(repeated=True)
    lastmodification = ndb.DateProperty()

    def update_urlsafe(self):
        self.urlsafe = self.key.urlsafe()

    @classmethod
    def get_from_key(cls, key):
        logging.info("get expense from key %s" % str(key))
        return key.get()


    def update(self, user, selectedmonth, selectedyear, request):
        res = 1
        self.user = user
        logging.info('update expense category=%s type=%s' % (request.get('category'), request.get('type')))
        self.category = request.get('category')
        self.exptype = int(request.get('type'))
        # an expense needs a non-empty category    
        if self.category == '':
            res = 0

        # set expense amount
        try:
            self.amount = float(request.get('amount'))
        except:
            res = 0

        #Set expense date
        try:
            self.date = datetime.strptime(request.get('date'), '%d/%m/%Y').date()
        except:
            self.date = date(selectedyear, selectedmonth, 1)

        #set tags
        self.update_tag(request.get('tags').split(';'))

        #set last modification date
        self.lastmodification = date.today()

        if res == 1:
            self.put()

    def update_tag(self, tags):
        category_tags = app_config['category_tags']
        if self.category in category_tags.keys():
            self.tags = category_tags[self.category]
            return

        updated_tags = []
        for x in tags:
            x = x.strip()
            if x == '':
                continue
            updated_tags.append(x)
        self.tags = updated_tags

