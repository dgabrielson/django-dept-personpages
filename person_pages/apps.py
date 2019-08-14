#########################################################################

from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _

#########################################################################


class PersonPagesConfig(AppConfig):
    name = "person_pages"
    verbose_name = _("Personal Pages")


#########################################################################


class PersonPagesConfigAutoCreateWithSlug(PersonPagesConfig):
    def ready(self):
        """
        Any app specific startup code, e.g., register signals,
        should go here.
        """
        from django.db.models.signals import post_save
        from people.models import Person
        from .handlers import create_personal_page

        # Automatically create personal pages (when a person has a slug)
        post_save.connect(create_personal_page, sender=Person)


#########################################################################


class PersonPagesConfigAutoCreateWithDirectoryFlag(PersonPagesConfig):
    def ready(self):
        """
        Any app specific startup code, e.g., register signals,
        should go here.
        """
        from django.db.models.signals import m2m_changed
        from people.models import Person
        from .handlers import create_personal_page_if_directory_flag_loaddata_safe

        # Automatically create personal pages (when a person has a slug AND the directory flag)
        m2m_changed.connect(
            create_personal_page_if_directory_flag_loaddata_safe,
            sender=Person.flags.through,
        )


#########################################################################
