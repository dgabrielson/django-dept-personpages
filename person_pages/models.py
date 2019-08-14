"""
Department Person Pages models.
"""
from __future__ import print_function, unicode_literals

from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.encoding import python_2_unicode_compatible
from people.models import Person  # people app is required.

from . import conf, handlers
from .managers import PageFileManager, PageSectionManager, PersonPageManager

#######################################################################

PERSON_PAGE_UPLOAD_PATH = conf.get("upload_path")
RST_HELP = conf.get("restructuredtext_help")
PHOTO_HELP = conf.get("photo_help")

#######################################################################


@python_2_unicode_compatible
class PersonPage(models.Model):
    """
    The web page for one person.
    Note that this is a container object -- people do not edit this themselves.
    Not every person has/needs a webpage.
    """

    active = models.BooleanField(default=True)
    created = models.DateTimeField(
        auto_now_add=True, editable=False, verbose_name="creation time"
    )
    modified = models.DateTimeField(
        auto_now=True, editable=False, verbose_name="last modification time"
    )

    person = models.OneToOneField(
        Person,
        on_delete=models.CASCADE,
        limit_choices_to={
            "active": True,
            "slug__isnull": False,
            "flags__slug": "directory",
        },
        help_text='Only people with slug fields and the "directory" flag are shown',
    )
    allow_owner_edits = models.BooleanField(
        default=False,
        help_text="If this is set, then the owner of the page can make their own updates",
    )

    objects = PersonPageManager()

    class Meta:
        ordering = ["person"]
        base_manager_name = "objects"

    def __str__(self):
        return "{}".format(self.person)

    def get_absolute_url(self):
        if not self.person.active:
            return None
        if not self.person.has_flag("directory"):
            return None
        if not self.person.slug:
            return None
        return reverse("person-page-detail", kwargs={"slug": self.person.slug})


#######################################################################


@python_2_unicode_compatible
class PageInfo(models.Model):
    """
    Core information for a single PersonPage -- user editiable.
    """

    created = models.DateTimeField(
        auto_now_add=True, editable=False, verbose_name="creation time"
    )
    modified = models.DateTimeField(
        auto_now=True, editable=False, verbose_name="last modification time"
    )

    page = models.OneToOneField(
        PersonPage, on_delete=models.CASCADE, limit_choices_to={"active": True}
    )

    photo = models.ImageField(
        upload_to=PERSON_PAGE_UPLOAD_PATH, help_text=PHOTO_HELP, blank=True
    )
    introduction = models.TextField(
        blank=True, help_text="Page introduction. " + RST_HELP
    )

    def __str__(self):
        return "PageInfo for " + "{}".format(self.page.person)


#######################################################################


@python_2_unicode_compatible
class PageSection(models.Model):
    """
    A section of one persons page -- user editable.
    """

    active = models.BooleanField(
        default=True,
        help_text="If this is checked, "
        + "the section will be shown, if not, it will be hidden.",
    )
    created = models.DateTimeField(
        auto_now_add=True, editable=False, verbose_name="creation time"
    )
    modified = models.DateTimeField(
        auto_now=True, editable=False, verbose_name="last modification time"
    )

    page = models.ForeignKey(
        PersonPage, on_delete=models.CASCADE, limit_choices_to={"active": True}
    )

    ordering = models.PositiveSmallIntegerField(
        default=0,
        help_text="This will determine the display order of the "
        + " sections on your page.",
    )
    title = models.CharField(max_length=250, help_text="The title for the section")
    content = models.TextField(help_text="The text for this section. " + RST_HELP)

    objects = PageSectionManager()

    class Meta:
        ordering = ["ordering"]
        base_manager_name = "objects"

    def __str__(self):
        return self.title


#######################################################################


@python_2_unicode_compatible
class PageFile(models.Model):
    """
    A way for people to upload files to use on their page.
    """

    page = models.ForeignKey(
        PersonPage, on_delete=models.CASCADE, limit_choices_to={"active": True}
    )
    slug = models.SlugField(help_text="A url fragment to identify this file")
    description = models.CharField(
        max_length=250,
        blank=True,
        help_text="(Optional) A short description of the file",
    )
    the_file = models.FileField(
        upload_to=PERSON_PAGE_UPLOAD_PATH, help_text="The file."
    )
    show_link = models.BooleanField(
        default=False,
        help_text="Select this to have a link to "
        + "this file at the bottom of your "
        + "personal page",
    )

    objects = PageFileManager()

    class Meta:
        unique_together = ("page", "slug")
        base_manager_name = "objects"

    def __str__(self):
        result = "PageFile"
        if self.description:
            result += " (" + self.description + ")" + self.the_file.url
        result += ": " + self.get_absolute_url()
        return result

    def get_absolute_url(self):
        """
        Return the url for this object
        """
        return self.the_file.url


#######################################################################
####
