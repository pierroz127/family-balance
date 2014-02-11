from google.appengine.ext import webapp

# get registry, we need it to register our filter later. 
register = webapp.template.create_template_register() 

def dlookup(value, key):
    return value[key]

register.filter(dlookup)
