"""
Signal handlers for PersonPages application.
"""
#######################################################################
# Source: https://code.djangoproject.com/ticket/8399
# Retreived: 2017-May-9
# Reason: disable m2m changed handling in loaddata/raw scenarios.

try:
    from functools import wraps
except ImportError:
    from django.utils.functional import wraps

import inspect


def disable_for_loaddata(signal_handler):
    @wraps(signal_handler)
    def wrapper(*args, **kwargs):
        for fr in inspect.stack():
            if inspect.getmodulename(fr[1]) == "loaddata":
                return
        signal_handler(*args, **kwargs)

    return wrapper


#######################################################################


def create_personal_page(sender, instance, created, raw, **kwargs):
    """
    A signal for automatically creating ``PersonPage`` when a person has
    a slug.
    This handler also adds the directory flag to the person, if they do not
    have it already.
    
    Register with:
    models.signals.post_save.connect(handlers.create_personal_page, sender=Person)
    
    NOTE: Only one of the create_person_page handlers should be registered.
    """
    if raw:
        return
    person = instance
    if not person.slug:
        return
    from .models import PersonPage

    PersonPage.objects.get_or_create(person=person)
    person.add_flag_by_name("directory")


#######################################################################


def create_personal_page_if_directory_flag(
    sender, instance, action, reverse, model, **kwargs
):
    """
    A signal for automatically creating ``PersonPage`` when a person has
    a slug *and* has the ``directory`` flag.
    
    Register with:
    models.signals.m2m_changed.connect(handlers.create_personal_page_if_directory_flag, sender=Person.flags.through)

    NOTE: Only one of the create_person_page handlers should be registered.
    """
    #     if raw:
    #         return
    # ignore changes to PersonFlag objects
    if reverse:
        return
    # ignore pre_* actions
    if not action.startswith("post_"):
        return
    person = instance
    if person.slug and person.has_flag("directory"):
        from .models import PersonPage

        PersonPage.objects.get_or_create(person=person)


create_personal_page_if_directory_flag_loaddata_safe = disable_for_loaddata(
    create_personal_page_if_directory_flag
)

#######################################################################
