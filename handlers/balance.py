import os
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext import ndb
from google.appengine.ext.webapp import template
from appengine_utilities import sessions
from models.balance import Balance
from utilities import users_helper

class BalancesHandler(webapp.RequestHandler):
    def get(self):
        if users_helper.is_autorized():
            session = sessions.Session()
            month = session["month"]
            monthname = session["monthname"]
            year = session["year"]
            template_values = {
                'allbalances': self.getAllBalances(),
                'selectedmonth': month,
                'selectedmonthname': monthname,
                'selectedyear': year,
                'debtor': self.debtor,
                'incredit': self.incredit,
                'balance': self.balance
            }

        path = os.path.join(os.path.dirname(__file__), '../templates/bilan.html')
        self.response.out.write(template.render(path, template_values))

    def getAllBalances(self):
        #query = ndb.GqlQuery("SELECT * FROM Balance ORDER BY year, month")
        query = Balance.query().order(Balance.year, Balance.month)
        balances = query.fetch(120)
        if not len(balances):
            self.debtor = ''
            self.incredit = ''
            self.balance = 0
        else:
            self.debtor = balances[0].debtor
            self.incredit = balances[0].incredit
            self.balance = 0
            for b in balances:
                if self.debtor == b.debtor:
                    self.balance += b.amount
                else:
                    self.balance -= b.amount
            if self.balance < 0:
                self.balance = -self.balance
                tmp = self.debtor
                self.debtor = self.incredit
                self.incredit = tmp
        return balances
