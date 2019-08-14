"""
QuerySets for the Person Pages application.
"""
#######################################################################

from django.db.models.query import QuerySet

#######################################################################


class BaseCustomQuerySet(QuerySet):
    """
    Base class for custom query sets.
    """

    def active(self):
        """
        Filter out non-active objects
        """
        return self.filter(active=True)


#######################################################################


class PersonPageQuerySet(BaseCustomQuerySet):
    """
    Custom QuerySet for PersonPage objects.
    """

    def active(self):
        return self.filter(
            active=True,
            person__active=True,
            person__slug__isnull=False,
            person__flags__slug="directory",
        )


#######################################################################


class PageSectionQuerySet(BaseCustomQuerySet):
    """
    Custom QuerySet for PageSection objects.
    """


#######################################################################


class PageFileQuerySet(QuerySet):
    """
    Custom QuerySet for PageFile objects.
    NOTE: This class **does not** inherit from ``BaseCustomQuerySet``.
    (This model does not have an ``active`` flag field.)
    """

    def public(self):
        """
        Returns only items with the show_link flag.
        """
        return self.filter(show_link=True)


#######################################################################
