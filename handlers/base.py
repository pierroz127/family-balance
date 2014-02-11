from google.appengine.ext import webapp
from datetime import datetime

#TODO: all the handler should inherit this one...
class BaseHandler(webapp.RequestHandler):
    def get(self):
        dt = datetime.today()
        self.redirect('/comptes?mois=%d&annee=%d'%(dt.month,dt.year))

