"""
PersonPages user editing form.
"""
#######################################################################
#######################
from __future__ import print_function, unicode_literals

from collections import OrderedDict

from django import forms
from django.contrib.staticfiles.storage import staticfiles_storage
from django.db.utils import IntegrityError
from django.forms.models import inlineformset_factory
from django.forms.utils import ErrorDict
from django.template.defaultfilters import slugify
from markuphelpers.forms import (
    LinedTextAreaMediaMixin,
    LinedTextareaWidget,
    ReStructuredTextFormMixin,
)

from .models import PageFile, PageInfo, PageSection, PersonPage

#######################


#######################################################################


class PersonPageForm(forms.ModelForm):
    """
    This form has no fields -- it is an anchor for the associated formsets.
    """

    class Meta:
        model = PersonPage
        fields = []

    class Media:
        css = {
            "all": (
                staticfiles_storage.url("css/forms.css"),
                staticfiles_storage.url("css/twoColumn.css"),
            )
            + LinedTextAreaMediaMixin.Media.css["all"]
        }
        js = (
            staticfiles_storage.url("js/jquery.formset.js"),
        ) + LinedTextAreaMediaMixin.Media.js


#######################################################################


class AdminPageInfoForm(ReStructuredTextFormMixin, forms.ModelForm):
    """
    The form for page info.
    """

    restructuredtext_fields = [("introduction", True)]

    class Meta:
        model = PageInfo
        widgets = {"introduction": LinedTextareaWidget}
        exclude = []


class PageInfoForm(AdminPageInfoForm):
    """
    The form for page info.
    """

    class Meta(AdminPageInfoForm.Meta):
        exclude = ("active",)

    class Media:
        css = {
            "all": (
                staticfiles_storage.url("css/forms.css"),
                staticfiles_storage.url("css/twoColumn.css"),
            )
        }
        js = (staticfiles_storage.url("js/jquery.formset.js"),)


# even though there is only one, doing a formset is easiest for PageInfo
PageInfoFormset = inlineformset_factory(
    PersonPage, PageInfo, form=PageInfoForm, can_delete=False, max_num=1
)


def get_pageinfo_formset_class(
    form=PageInfoForm, formset=forms.BaseInlineFormSet, **kwargs
):
    if "can_delete" not in kwargs:
        kwargs["can_delete"] = False
    if "max_num" not in kwargs:
        kwargs["max_num"] = 1
    return inlineformset_factory(PersonPage, PageInfo, form, formset, **kwargs)


#######################################################################


class PageSectionForm(ReStructuredTextFormMixin, forms.ModelForm):
    """
    The form for page sections.
    """

    restructuredtext_fields = [("content", True)]

    class Meta:
        model = PageSection
        widgets = {
            "ordering": forms.TextInput(attrs={"size": 6}),
            "title": forms.TextInput(attrs={"size": 50}),
            "content": LinedTextareaWidget,
        }
        exclude = []


def get_pagesection_formset_class(
    form=PageSectionForm, formset=forms.BaseInlineFormSet, **kwargs
):
    if "can_delete" not in kwargs:
        kwargs["can_delete"] = True
    if "extra" not in kwargs:
        kwargs["extra"] = 0
    return inlineformset_factory(PersonPage, PageSection, form, formset, **kwargs)


#######################################################################


class PageFileForm(forms.ModelForm):
    """
    The form for page files.
    """

    class Meta:
        model = PageFile
        exclude = ["active"]
        widgets = {"description": forms.TextInput(attrs={"size": 35})}


def get_pagefile_formset_class(
    form=PageFileForm, formset=forms.BaseInlineFormSet, **kwargs
):
    if "can_delete" not in kwargs:
        kwargs["can_delete"] = True
    if "extra" not in kwargs:
        kwargs["extra"] = 0
    return inlineformset_factory(PersonPage, PageFile, form, formset, **kwargs)


#######################################################################
#######################################################################
#######################################################################


class PersonPagePersonSubForm(forms.ModelForm):
    """
    The sub form for the person form.
    """

    subform_title = "Personal page"

    class Meta:
        model = PersonPage
        fields = ["active", "allow_owner_edits"]

    def __init__(self, data=None, *args, **kwargs):
        """
        If instance is passed, then we must resolve this: it is a person!
        """
        self.person = None
        instance = kwargs.pop("instance", None)
        if instance is not None:
            self.person = instance
            try:
                kwargs["instance"] = self.person.personpage
            except PersonPage.DoesNotExist:
                kwargs["instance"] = None

        result = super(PersonPagePersonSubForm, self).__init__(data, *args, **kwargs)
        if self.person is not None and self.instance is not None:
            self.instance.person = self.person

        # allow for this sub-object to *not* be created:
        if self.instance.pk is None:
            f = forms.BooleanField(
                label="Create personal page",
                required=False,
                help_text="Personal pages are automatically created if a slug is set (regardless of this value); if this checkbox is set a slug will automatically be generated if needed.",
            )
            self.fields = OrderedDict([("_do_create", f)] + list(self.fields.items()))
            self.initial["_do_create"] = True
            del self.fields["active"]  # of course it will be active, if created.
            if data and not data.get(self.get_do_create_field_name(), False):
                for key in self.fields:
                    self.fields[key].required = False

        return result

    def get_do_create_field_name(self):
        if self.prefix:
            prefix_field = self.prefix + "-" + "_do_create"
        else:
            prefix_field = "_do_create"
        return prefix_field

    def full_clean(self, *args, **kwargs):
        """
        Override clean behaviour when _do_create is *not* set.
        """
        self._errors = ErrorDict()
        if not self.is_bound:  # Stop further processing.
            return
        if "_do_create" in self.fields and not self.data.get(
            self.get_do_create_field_name(), False
        ):
            self.cleaned_data = {"_do_create": False}
        else:
            return super(PersonPagePersonSubForm, self).full_clean(*args, **kwargs)

    def save(self, person, *args, **kwargs):
        """
        Each save() must reinsert the person, along with any other required
        fields that are not shown.
        """
        # allow for this sub-object to *not* be created:
        if "_do_create" in self.fields and not self.cleaned_data.get(
            "_do_create", False
        ):
            print("NOT CREATING PERSON PAGE")
            return None
        original_commit = kwargs.get("commit", None)
        kwargs["commit"] = False
        obj = super(PersonPagePersonSubForm, self).save(*args, **kwargs)
        obj.person = person

        if original_commit is not None:
            kwargs["commit"] = original_commit
        else:
            del kwargs["commit"]

        if original_commit != False:  # None \equiv True
            # do not modify the purse of ``commit=False``
            person.add_flag_by_name("directory")
            if not person.slug:
                base_slug = slugify(person.cn)
                slug = base_slug
                n = 0
                while True:
                    person.slug = slug
                    try:
                        person.save()
                    except IntegrityError:
                        n += 1
                        slug = base_slug + "-{0}".format(n)
                    else:
                        break

        # it may already exist; depending on the configuration.
        if not obj.pk:
            try:
                person_page = PersonPage.objects.get(person=person)
            except PersonPage.DoesNotExist:
                pass
            else:
                for f in self._meta.fields:
                    v = getattr(obj, f)
                    setattr(person_page, f, v)
                if original_commit != False:
                    person_page.save()
                return person_page
        return super(PersonPagePersonSubForm, self).save(*args, **kwargs)


#######################################################################
#######################################################################
#######################################################################
