import os

from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from appengine_utilities import sessions
from utilities import date_helper, users_helper
from utilities.user_expenses import UserExpenses
from datetime import datetime
import logging

class AccountHandler(webapp.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if user is None:
            self.redirect(users.create_login_url(self.request.uri))
            return

        dtnow = datetime.utcnow()
        try:
            month = int(self.request.get('mois'))
            year = int(self.request.get('annee'))
        except:
            month = dtnow.month
            year = dtnow.year
        session = sessions.Session()
        session["month"] = month
        session["year"] = year
        users_expenses = UserExpenses.get_user_expenses(month, year)
        months = date_helper.get_all_months()

        # for the moment the status is only computed when there are only 2 users
        status = {'maxuser': user, 'minuser': users_helper.get_other_nickname(), 'debt': 0}
        if len(users_expenses) == 2:
            status = UserExpenses.compute_balance(users_expenses, month, year)
            logging.info(status)

        template_values = {
            'logouturl': users.create_logout_url("/"),
            'currentuser': users.get_current_user().nickname(),
            'selectedmonth': month,
            'selectedmonthname': months[month-1]['Name'],
            'selectedyear': year,
            'month_range': months,
            'year_range': range(2009, dtnow.year + 1),
            'usersexpenses': users_expenses,
            'status_maxuser': status['maxuser'],
            'status_minuser': status['minuser'],
            'status_debt': '%.2f' % status['debt'],
            'nextmonth': date_helper.get_next_month(month),
            'nextyear': date_helper.get_year_of_next_month(month, year),
            'previousmonth': date_helper.get_previous_month(month),
            'previousyear': date_helper.get_year_of_previous_month(month, year)
        }
        session["monthname"] = months[month-1]['Name']
        path = os.path.join(os.path.dirname(__file__), '../templates/index.html')
        self.response.out.write(template.render(path, template_values))