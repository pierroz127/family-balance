from datetime import date

from google.appengine.ext import ndb
from google.appengine.api import users
import logging

from models.balance import Balance
from models.expenses import Expenses, expenses_key
from models.tax_ratio import TaxRatio
from utilities import users_helper

class UserExpenses:
    def __init__(self, usr):
        self.user = usr
        self.expenses = []
        self.totalcommon = 0.0
        self.totalpersonal = 0.0
        self.totaladvance = 0.0
        self.totaltax = 0.0
        self.taxratio = 0.0

    def add(self, spending):
        self.expenses.append(spending)

        if spending.exptype == 1:
            # common expense
            self.totalcommon += spending.amount
        elif spending.exptype == 2:
            # expense as an advance
            self.totaladvance += spending.amount
        elif spending.exptype == 3:
            # personal expense
            self.totalpersonal += spending.amount
        elif spending.exptype == 4:
            # tax payment
            self.totaltax += spending.amount

    def total(self):
        return self.totaladvance + self.totalcommon + self.totalpersonal + self.totaltax

    @classmethod
    def getKey(expense):
        return expense.date

    @classmethod
    def compute_balance(cls, users_expenses, month, year):
        if len(users_expenses) == 0:
            # nothing to do
            return

        user_a = users_expenses[0]
        if len(users_expenses) == 2:
            user_b = users_expenses[1]
        else:
            user_b = UserExpenses(users_helper.get_other_nickname())
        debt = (user_a.totalcommon - user_b.totalcommon) / 2 + user_a.totaladvance - user_b.totaladvance

        if user_a.totaltax != 0.0 or user_b.totaltax != 0.0:
            debt += cls.compute_tax_balance(user_a, user_b, year)

        if debt > 0:
            min_user = user_b
            max_user = user_a
        else:
            debt = -debt
            min_user = user_a
            max_user = user_b

        # update the balance in DataStore
        query = Balance.query(Balance.month == month, Balance.year == year)
        balance = query.get()
        if balance is None:
            balance = Balance()
            balance.year = year
            balance.month = month

        balance.debtor = min_user.user
        balance.incredit = max_user.user
        balance.amount = debt
        balance.put()

        return {'year': year, 'month': month, 'maxuser': max_user.user, 'minuser': min_user.user, 'debt': debt}

    @classmethod
    def compute_tax_balance(cls, user_a, user_b, year):
        ratio_a = cls.get_tax_ratio(user_a.user, year)
        ratio_b = cls.get_tax_ratio(user_b.user, year)
        return (1 - ratio_a) * user_a.totaltax - (1 - ratio_b) * user_b.totaltax

    @classmethod
    def get_tax_ratio(cls, user, year):
        query = TaxRatio.query(TaxRatio.user == user, TaxRatio.year == year)
        tax_ratio = query.get()
        if tax_ratio is None:
            return 0.5
        return tax_ratio.ratio

    @classmethod
    def get_user_expenses(cls, month, year):
        """

        """
        first_day = date(year, month, 1)
        if month == 12:
            last_day = date(year + 1, 1, 1)
        else:
            last_day = date(year, month + 1, 1)

        logging.info("load user expenses between %s and %s" %
                     (first_day.strftime('%d %b %Y'), last_day.strftime('%d %b %Y')))

        q = Expenses.query(ancestor=expenses_key(month, year))
        q.filter(ndb.AND(Expenses.date >= first_day, Expenses.date < last_day))

        #query for old data that had no ancestor (before migration to High Replication Datastore)
        q_old = Expenses.query(ndb.AND(Expenses.date >= first_day, Expenses.date < last_day))

        users_expenses = dict()
        keys = set()
        if users_helper.is_autorized():
            # always start with the current user
            currentUser = users.get_current_user().nickname()
            users_expenses[currentUser] = UserExpenses(currentUser)

            x = 0
            #TODO Hem refactor this ugly code
            for exp in q.fetch(500):
                exp.update_urlsafe()
                keys.add(exp.urlsafe)
                user_nickname = exp.user.nickname()
                if user_nickname not in users_expenses.keys():
                    users_expenses[user_nickname] = UserExpenses(user_nickname)
                users_expenses[user_nickname].add(exp)
                x += 1
            logging.info('%d expenses with ancestor', x)

            x = 0
            for exp in q_old.fetch(500):
                exp.update_urlsafe()
                if exp.urlsafe not in keys:
                    user_nickname = exp.user.nickname()
                    if user_nickname not in users_expenses.keys():
                        users_expenses[user_nickname] = UserExpenses(user_nickname)
                    users_expenses[user_nickname].add(exp)
                    x += 1
            logging.info('%d expenses with no ancestor', x)

        for usr in users_expenses.keys():
            users_expenses[usr].taxratio = cls.get_tax_ratio(usr, year)
            users_expenses[usr].expenses = sorted(users_expenses[usr].expenses, key=lambda e: e.date)

        return users_expenses.values()

    @classmethod
    def compute_year_balances(cls, year):
        balances = []
        for i in range(1, 13):
            users_expenses = UserExpenses.get_user_expenses(i, year)
            balances.append(UserExpenses.compute_balance(users_expenses, i, year))
        return balances


