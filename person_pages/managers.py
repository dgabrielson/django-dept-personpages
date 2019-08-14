"""
Managers for the Person Pages application.
"""
#######################################################################

from django.db.models import Manager
from django.db.models.query import QuerySet

from .querysets import PageFileQuerySet, PageSectionQuerySet, PersonPageQuerySet

#######################################################################
#######################################################################


class CustomQuerySetManager(Manager):
    """
    Custom Manager for an arbitrary model, just a wrapper for returning
    a custom QuerySet
    """

    queryset_class = QuerySet

    def get_queryset(self):
        """
        Return the custom QuerySet
        """
        return self.queryset_class(self.model)


#######################################################################
#######################################################################


class PersonPageManager(CustomQuerySetManager):
    """
    Manager for PersonPage objects.  Essentially just proxies
    back to the custom QuerySet.
    """

    queryset_class = PersonPageQuerySet


PersonPageManager = PersonPageManager.from_queryset(PersonPageQuerySet)

#######################################################################


class PageSectionManager(CustomQuerySetManager):
    """
    Manager for PageSection objects.  Essentially just proxies
    back to the custom QuerySet.
    """

    queryset_class = PageSectionQuerySet


PageSectionManager = PageSectionManager.from_queryset(PageSectionQuerySet)

#######################################################################


class PageFileManager(CustomQuerySetManager):
    """
    Manager for PageFile objects.  Essentially just proxies
    back to the custom QuerySet.
    """

    queryset_class = PageFileQuerySet


PageFileManager = PageFileManager.from_queryset(PageFileQuerySet)

#######################################################################
