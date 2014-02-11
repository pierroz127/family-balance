from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext import ndb
from google.appengine.ext.webapp import template
from datetime import date
import os
from models.expenses import Expenses
from models.tag import Tag
from utilities import date_helper
import logging

class ChartHandler(webapp.RequestHandler):
    def get(self):
        self.category = self.request.get('categorie')
        charttype = self.request.get('charttype')
        self.stramounts = ''
        self.labels = ''
        self.maxamount = 5
        self.totalamount = 0
        if charttype == 'tag':
            self.get_last_twelve_months_tag_expenses()
        else:
            self.get_last_twelve_months_category_expenses()
        templateValues = {
            'category': self.category,
            'amounts': self.stramounts,
            'maxamount': self.maxamount,
            'categorywithamount': self.category + ': ' + str(self.totalamount) + ' euros',
            'labels': self.labels
        }
        path = os.path.join(os.path.dirname(__file__), '../templates/chart.html')
        self.response.out.write(template.render(path, templateValues))

    def get_last_twelve_months_tag_expenses(self):
        last_year = date_helper.get_last_year_date()
        logging.info("last year = %d" % last_year.year)
        month_year = last_year.year * 12 + last_year.month
        logging.info("month year = %d" % month_year)
        self.compute_labels(last_year)
        q = Tag.query(ancestor=Tag.get_tag_parent_key(self.category))
        tags = q.fetch(1000)
        amounts = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        for tag in tags:
            if tag.amount is not None:
                index = tag.monthyear - month_year
                if index not in range(0, 12):
                    continue
                logging.info("tag=%s amount=%f index=%d" % (tag.name, tag.amount, index))
                amounts[index] += tag.amount
                self.totalamount += tag.amount

        self.compute_max_amount(amounts)

    def get_last_twelve_months_category_expenses(self):
        last_year = date_helper.get_last_year_date()
        self.compute_labels(last_year)

        #TODO refactor
        #query = db.GqlQuery("SELECT * FROM Expenses WHERE category = :1 AND date >= :2 AND exptype = 1", self.category, last_year)
        #expenses = query.fetch(5000)
        q = Expenses.query()
        q.filter(ndb.AND(Expenses.category == self.category, Expenses.date >= last_year, Expenses.exptype == 1))
        expenses = q.fetch(5000)
        amounts = []
        for i in range(0, 12):
            amounts.append(0)

        for exp in expenses:
            index = date_helper.get_month_index(exp.date)
            if index != -1:
                amounts[index] += exp.amount
                self.totalamount += exp.amount

        self.compute_max_amount(amounts)

    def compute_max_amount(self, amounts):
        self.maxamount = amounts[0]
        self.stramounts = str(amounts[0])
        for i in range(1,12):
            self.stramounts = self.stramounts + ',' + str(amounts[i])
            if self.maxamount < amounts[i]:
                self.maxamount = amounts[i]
        self.maxamount += 5

    def compute_labels(self, dt):
        self.labels = ''
        for i in range(0, 12):
            self.labels = self.labels + '|' + date_helper.get_month_label(dt.month) + str(dt.year%100)
            if dt.month == 12:
                dt = date(dt.year + 1, 1, 1)
            else:
                dt = date(dt.year, dt.month + 1, 1)
