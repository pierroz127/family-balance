from config import app_config
from google.appengine.api import users

def is_autorized():
    current_user = users.get_current_user()
    if current_user:
        return current_user.nickname() in app_config['authorized_users']
    return False

def get_other_nickname():
    current_user_email = users.get_current_user().nickname()
    return filter(lambda u : u != current_user_email, app_config['authorized_users'])[0]