"""
PersonPage URLS

(r'^people/', include('person_pages.urls')),

"""
from django.conf.urls import url

from .models import PersonPage
from .views import (
    PersonPageDetailView,
    PersonPageListView,
    person_calendar,
    personpage_update,
)

urlpatterns = [
    url(r"^$", PersonPageListView.as_view(), name="person-page-list"),
    url(
        r"(?P<slug>[\w-]+)/$", PersonPageDetailView.as_view(), name="person-page-detail"
    ),
    url(r"(?P<slug>[\w-]+)/update$", personpage_update, name="person-page-update"),
    url(r"(?P<slug>[\w-]+)/calendar$", person_calendar, name="person-page-calendar"),
]


# Conditional loading of mugshot handling.
#   requires django-face-detect.
try:
    from . import mugshot
except ImportError:
    pass
else:
    # load additional mugshot urls
    urlpatterns += [
        url(
            r"^(?P<slug>[\w-]+)/mugshot-preview$",
            mugshot.preview,
            name="person-page-mugshot-preview",
        ),
        url(
            r"^(?P<slug>[\w-]+)/mugshot-preview-img$",
            mugshot.preview_img,
            name="person-page-mugshot-preview-img",
        ),
        url(
            r"^(?P<slug>[\w-]+)/mugshot-save$",
            mugshot.save,
            name="person-page-mugshot-save",
        ),
    ]
