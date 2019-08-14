"""
PersonPage views extend class-based generic views.
"""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponseForbidden, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.template import TemplateDoesNotExist
from django.utils.decorators import method_decorator
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView
from django.views.generic.list import ListView
from webcal.views import icalendar_feed

from .forms import (
    PersonPageForm,
    get_pagefile_formset_class,
    get_pageinfo_formset_class,
    get_pagesection_formset_class,
)
from .models import PersonPage

######################################################################


class PersonPageMixin(object):
    queryset = PersonPage.objects.active().filter(
        person__active=True, person__slug__isnull=False, person__flags__slug="directory"
    )

    def get_object(self):
        slug = self.kwargs["slug"]
        try:
            return self.get_queryset().get(person__slug=slug)
        except PersonPage.DoesNotExist:
            raise Http404


######################################################################


class PersonPageListView(PersonPageMixin, ListView):
    """
    Does a list of jobs, and a list of additional resources.
    """

    context_object_name = "page_list"


######################################################################


class PersonPageDetailView(PersonPageMixin, DetailView):
    """
    A view showing details for a particular PersonPage.
    """

    context_object_name = "page"


######################################################################


def permission_check(request, page):
    if request.user.is_superuser:
        return True
    if request.user.has_perm("person_pages.change_personpage"):
        return True
    if page.allow_owner_edits and request.user.username == page.person.username:
        return True
    return False


def forbidden_response(request, content):
    try:
        resp = render(request, "403.html", {"test_fail_msg": content})
        resp.status_code = 403
        return resp
    except TemplateDoesNotExist:
        return HttpResponseForbidden(content)


######################################################################


class PersonPageUpdateView(PersonPageMixin, UpdateView):
    """
    Class for updating person pages.
    """

    form_class = PersonPageForm
    formset_initial = None
    formset_name_list = ["info", "sections", "files"]
    queryset = PersonPage.objects.active()
    template_name = "person_pages/personpage_form.html"

    def get_formset_class(self, formset_name):
        if formset_name == "info":
            return get_pageinfo_formset_class()
        if formset_name == "sections":
            return get_pagesection_formset_class()
        if formset_name == "files":
            return get_pagefile_formset_class()
        raise ImplementationError(
            'The formset name "{}" is not known'.format(formset_name)
        )

    def get_formset_initial(self, formset_name):
        """
        Returns the initial data to use for forms on this view.
        """
        if self.formset_initial is None:
            self.formset_initial = {}
        return self.formset_initial.get(formset_name, {}).copy()

    def get_formset_prefix(self, formset_name):
        """
        Returns the prefix to use for forms on this view
        """
        return formset_name

    def get_formset_kwargs(self, formset_name):
        kwargs = {
            "initial": self.get_formset_initial(formset_name),
            "prefix": self.get_formset_prefix(formset_name),
            "instance": self.object,
        }

        if self.request.method in ("POST", "PUT"):
            kwargs.update({"data": self.request.POST, "files": self.request.FILES})
        return kwargs

    def get_formset(self, formset_name, formset_class=None):
        """
        Returns an instance of the form to be used in this view.
        """
        if formset_class is None:
            formset_class = self.get_formset_class(formset_name)
        return formset_class(**self.get_formset_kwargs(formset_name))

    def get_formset_list(self):
        return [self.get_formset(name) for name in self.formset_name_list]

    def get_context_data(self, **kwargs):
        """
        Insert the form into the context dict.
        """
        context = super(PersonPageUpdateView, self).get_context_data(**kwargs)
        if "formset_list" not in context:
            context["formset_list"] = self.get_formset_list()
        if "page" not in context:
            context["page"] = self.object
        return context

    def form_valid(self, form, formset_list):
        """
        If the form is valid, save the associated model.
        """
        result = super(PersonPageUpdateView, self).form_valid(form)
        for formset in formset_list:
            formset.save()
        return result

    def form_invalid(self, form, formset_list):
        """
        If the form is invalid, re-render the context data with the
        data-filled form and errors.
        """
        return self.render_to_response(
            self.get_context_data(form=form, formset_list=formset_list)
        )

    def post(self, request, *args, **kwargs):
        """
        Handles POST requests, instantiating a form instance with the passed
        POST variables and then checked for validity.
        """
        self.object = self.get_object()
        form = self.get_form()
        formset_list = self.get_formset_list()
        if form.is_valid() and all((formset.is_valid() for formset in formset_list)):
            return self.form_valid(form, formset_list)
        else:
            return self.form_invalid(form, formset_list)


personpage_update = login_required(PersonPageUpdateView.as_view())

######################################################################


def person_calendar(request, slug):
    """
    Provide a calendar feed for this person.
    """
    page = get_object_or_404(PersonPage, active=True, person__slug=slug)
    return icalendar_feed(request, page.person)


#


######################################################################
######################################################################
