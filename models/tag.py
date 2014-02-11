from google.appengine.ext import ndb


class Tag(ndb.Model):
    name = ndb.StringProperty()
    monthyear = ndb.IntegerProperty()
    amount = ndb.FloatProperty()

    @classmethod
    def get_tag_parent_key(cls, tag_name):
        return ndb.Key('category_tags', tag_name)
