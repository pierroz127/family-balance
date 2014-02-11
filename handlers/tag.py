from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext import ndb
from django.utils import simplejson
from models.expenses import Expenses
from models.tag import Tag


# Retrieve all categories for autocomplete input
class AllTagsHandler(webapp.RequestHandler):
    def get(self):
        #query = db.GqlQuery('SELECT * FROM Tag')
        query = Tag.query()
        tags = query.fetch(5000)
        jsonData = dict()
        tagnames = []
        for tag in tags:
            if tag == '':
                continue
            if tag.name not in tagnames:
                tagnames.append(tag.name)
        jsonData['source'] = tagnames
        self.response.out.write(simplejson.dumps(jsonData))


class TagsHandler(webapp.RequestHandler):
    def get(self):
        #print 'coucou'
        #query = db.GqlQuery('SELECT * FROM Expenses')
        query = Expenses.query()
        expenses = query.fetch(10000)
        self.jsonData = dict()
        self.jsonData['tags'] = dict()
        for exp in expenses:
            for tag in exp.tags:
                if tag != '':
                    self.update_tag(tag, exp.amount, exp.date)
        self.persist()
        self.response.out.write(simplejson.dumps(self.jsonData))

    def update_tag(self, tag, amount, dt):
        if tag not in self.jsonData['tags']:
            self.jsonData['tags'][tag] = dict()

        monthyear = 12 * dt.year + dt.month
        if monthyear not in self.jsonData['tags'][tag]:
            self.jsonData['tags'][tag][monthyear] = 0

        self.jsonData['tags'][tag][monthyear] += amount

    #persist the monthly amount associated with each tag
    def persist(self):
        for tagname in self.jsonData['tags']:
            for monthyear in self.jsonData['tags'][tagname]:
                tagmodel = self.retrieve(tagname, monthyear)
                tagmodel.amount = self.jsonData['tags'][tagname][monthyear]
                tagmodel.put()

    #retrieve a tag in data store if it exists or create it
    def retrieve(self, tagname, monthyear):
        query = Tag.query(Tag.monthyear == monthyear, ancestor=Tag.get_tag_parent_key(tagname))
        tagmodels = query.fetch(1)
        if len(tagmodels) == 0:
            tag = Tag(parent=Tag.get_tag_parent_key(tagname))
            tag.name = tagname
            tag.monthyear = monthyear
        else:
            tag = tagmodels[0]
        return tag