import os

from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
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
        users_expenses = UserExpenses.get_user_expenses(month, year)
        #months = date_helper.get_all_months()
        months = range(1, 13)

        # for the moment the status is only computed when there are only 2 users
        status = {'maxuser': user, 'minuser': users_helper.get_other_nickname(), 'debt': 0}
        if len(users_expenses) == 2:
            status = UserExpenses.compute_balance(users_expenses, month, year)
            logging.info(status)

        #month_name = months[month-1]['Name']
        template_values = {
            'logouturl': users.create_logout_url("/"),
            'currentuser': users.get_current_user().nickname(),
            'selectedmonth': month,
            #'selectedmonthname': month_name,
            'selectedyear': year,
            'month_range': months,
            'year_range': range(2009, dtnow.year + 6),
            'usersexpenses': users_expenses,
            'status_maxuser': status['maxuser'],
            'status_minuser': status['minuser'],
            'status_debt': '%.2f' % status['debt'],
            'nextmonth': date_helper.get_next_month(month),
            'nextyear': date_helper.get_year_of_next_month(month, year),
            'previousmonth': date_helper.get_previous_month(month),
            'previousyear': date_helper.get_year_of_previous_month(month, year)
        }
        #session["monthname"] = months[month-1]['Name']
        path = os.path.join(os.path.dirname(__file__), '../templates/index.html')
        cookie_value = "%d#%d"%(month, year)
        logging.info("_balanceSession = "+ cookie_value)
        self.response.headers.add_header('Set-Cookie', '_balanceSession=' + cookie_value + ';path=/;max-age=' + str(7*24*3600) + ';')
        self.response.out.write(template.render(path, template_values))

