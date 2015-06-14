from google.appengine.api import users
from google.appengine.ext import blobstore, webapp
from google.appengine.ext.webapp import blobstore_handlers, template
import logging
import os
from models.expenses import Expenses, expenses_key


class BankStatementUploadFormHandler(webapp.RequestHandler):
    def get(self):
        # [START upload_url]
        upload_url = blobstore.create_upload_url('/upload_bank_statement')
        # [END upload_url]
        # [START upload_form]
        # The method must be "POST" and enctype must be set to "multipart/form-data".
        template_values = {
            'upload_url': upload_url,
            'logouturl': users.create_logout_url("/"),
            'currentuser': users.get_current_user().nickname() 
        }
        path = os.path.join(os.path.dirname(__file__), '../templates/upload.html')
        self.response.out.write(template.render(path, template_values))
        #self.response.out.write('<html><body>')
        #self.response.out.write('<form action="%s" method="POST" enctype="multipart/form-data">' % upload_url)
        #self.response.out.write('''Upload File: <input type="file" name="file"><br> <input type="submit"
        #    name="submit" value="Submit"> </form></body></html>''')
        # [END upload_form]

class BankStatementUploadHandler(blobstore_handlers.BlobstoreUploadHandler):
    def post(self):
        try:
            bank_statement = self.get_uploads()[0]
            from ofxparse import OfxParser
            ofx = OfxParser.parse(bank_statement.open())
            user = users.get_current_user()
            logging.info(ofx.account.number)                  # The account number
            logging.info(ofx.account.routing_number)          # The transit id (sometimes called branch number)
            #logging.info(ofx.account.statement               # Account information for a period of time
            logging.info(ofx.account.statement.start_date)    # The start date of the transactions
            logging.info(ofx.account.statement.end_date)      # The end date of the transactions
            #ofx.account.statement.transactions  # A list of account activities
            logging.info(ofx.account.statement.balance)       # The money in the account as of the statement 
            for tx in ofx.account.statement.transactions:
                logging.info(vars(tx))
                if tx.type == 'debit':
                    # new expense:
                    new_expense = Expenses(parent=expenses_key(tx.date.month, tx.date.year))
                    new_expense.user = user
                    new_expense.date = tx.date
                    new_expense.amount = -float(str(tx.amount))
                    new_expense.category = tx.payee
                    new_expense.exptype = 3
                    new_expense.put()
        finally:
            self.redirect('comptes')
