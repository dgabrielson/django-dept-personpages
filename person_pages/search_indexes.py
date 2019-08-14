"""
Haystack search indexes for PersonPages application.
"""
###############################################################

from haystack import indexes

from .models import PersonPage

###############################################################


class PersonPageIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    pub_date = indexes.DateTimeField(model_attr="modified")
    author = indexes.CharField(model_attr="person", boost=10.0)
    title = indexes.CharField(model_attr="person", boost=10.0)

    def get_model(self):
        return PersonPage

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.active()

    def prepare(self, obj):
        """
        Do document boosting.
        """
        data = super(PersonPageIndex, self).prepare(obj)
        data["boost"] = 1.5
        return data


###############################################################
