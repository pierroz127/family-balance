from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext import ndb
from django.utils import simplejson
from models.expenses import Expenses, expenses_key
from models.tax_ratio import TaxRatio
from utilities import users_helper
import datetime
import logging
from utilities.user_expenses import UserExpenses

class AddOrUpdateHandler(webapp.RequestHandler):
    def post(self):
        try:
            selected_month = int(self.request.get('mois'))
            selected_year = int(self.request.get('annee'))
        except:
            dtnow = datetime.utcnow()
            selected_month = dtnow.month
            selected_year = dtnow.year

        if users.get_current_user():
            urlsafe = self.request.get('urlsafe')
            if urlsafe != '':
                logging.info('get expense from key ' + urlsafe)
                new_expense = Expenses.get_from_key(ndb.Key(urlsafe=urlsafe))
                if new_expense is None:
                    raise Exception("unable to retrieve expense for key " + urlsafe)
            else:
                new_expense = Expenses(parent=expenses_key(selected_month, selected_year))

            new_expense.update(users.get_current_user(), selected_month, selected_year, self.request)
        else:
            raise Exception('bad user')

        self.redirect('/comptes?mois=%d&annee=%d' % (selected_month, selected_year))

class RemoveHandler(webapp.RequestHandler):
    def get(self):
        logging.info('coucou')
        if users_helper.is_autorized():
            urlsafe = self.request.get('urlsafe')
            if urlsafe != '' and urlsafe is not None:
                try:
                    key = ndb.Key(urlsafe=urlsafe)
                    logging.info(key)
                    if key is not None:
                        key.delete()
                except:
                    logging.error('ouch... this %s is not a valid value for urlsafe' % urlsafe)
            month = self.request.get('mois')
            year = self.request.get('annee')
            self.redirect('/comptes?mois=%s&annee=%s'%(month, year))

class TaxRatioHandler(webapp.RequestHandler):
    def post(self):
        logging.debug("taxratio: " + str(self.request.params['taxratio']))
        logging.debug("year: " + str(self.request.params['year']))
        ratio = float(self.request.params['taxratio'])
        year = int(self.request.params['year'])
        user = users.get_current_user().nickname()
        self.update_tax_ratio(ratio, year, user)
        #TODO: update all the balances of the year...
        new_balances = UserExpenses.compute_year_balances(year)
        self.response.out.write(simplejson.dumps({"taxratio": ratio, "year": year, "newbalances": new_balances}))

    def update_tax_ratio(self, ratio, year, user):
        query = TaxRatio.query(TaxRatio.year == year)
        update = False
        for taxratio in query.fetch(2):
            if taxratio.user == user:
                taxratio.ratio = ratio
            else:
                taxratio.ratio = 1 - ratio
            logging.debug("saving ratio %s for user %s"%(str(taxratio), user))
            taxratio.put()
            update = True

        if not update:
            taxratioa = TaxRatio(user=user, ratio=ratio, year=year)
            logging.debug("saving %s" % str(taxratioa))
            taxratioa.put()
            taxratiob = TaxRatio(user=users_helper.get_other_nickname(), ratio=1 - ratio, year=year)
            logging.debug("saving %s" % str(taxratiob))
            taxratiob.put()
        else:
            #update balance with this new tax ratio
            for month in range(1, 12):
                user_expenses = UserExpenses.get_user_expenses(month, year)
                UserExpenses.compute_balance(user_expenses, month, year)


