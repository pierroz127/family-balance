import logging

from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db
from google.appengine.ext.webapp import template
from handlers.account import AccountHandler
from handlers.balance import BalancesHandler
from handlers.base import BaseHandler
from handlers.chart import ChartHandler
from handlers.edit import AddOrUpdateHandler, RemoveHandler, TaxRatioHandler
from handlers.tag import AllTagsHandler, TagsHandler
from handlers.upload import BankStatementUploadFormHandler
from django.utils import simplejson

webapp.template.register_template_library('common.templatefilters')

application = webapp.WSGIApplication(
                                     [('/', BaseHandler),
                                      ('/telecharger', BankStatementUploadFormHandler),
                                      ('/comptes', AccountHandler),
                                      ('/depense', AddOrUpdateHandler),
                                      ('/supprimer', RemoveHandler),
                                      ('/bilans', BalancesHandler),
                                      ('/alltags', AllTagsHandler),
                                      ('/graphique', ChartHandler),
                                      ('/computetags', TagsHandler),
                                      ('/impots', TaxRatioHandler)],
                                     debug=True)


def main():
    logging.getLogger().setLevel(logging.DEBUG)
    run_wsgi_app(application)

if __name__ == "__main__":
    main()


