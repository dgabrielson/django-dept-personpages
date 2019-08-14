"""
Special routines for saving mugshot files using facial detection.
"""
######################################################################
import os

import face_detect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render

from .models import PageInfo
from .views import PersonPageDetailView, permission_check

######################################################################

preview = login_required(
    PersonPageDetailView.as_view(template_name="person_pages/mugshot_preview.html")
)


######################################################################


@login_required
def preview_img(request, slug):
    pageinfo = get_object_or_404(PageInfo, page__active=True, page__person__slug=slug)

    if not permission_check(request, pageinfo.page):
        return forbidden_response(
            request, "You do not have permission to access this page."
        )

    if pageinfo.photo is None:
        msg = "Image not found"
        messages.error(request, msg, fail_silently=True)
        raise Http404(msg)

    im = face_detect.detect_face_preview(pageinfo.photo)
    if im is None:
        msg = "No face detected in this image"
        # messages.error(request, msg, fail_silently=True)
        return HttpResponseRedirect(pageinfo.photo.url)
        raise Http404(msg)

    return face_detect.HttpImageResponse(im)


######################################################################


@login_required
def save(
    request, slug, template_name="person_pages/mugshot_save.html", extra_context={}
):

    pageinfo = get_object_or_404(PageInfo, page__active=True, page__person__slug=slug)

    page = pageinfo.page
    if not permission_check(request, page):
        return forbidden_response(
            request, "You do not have permission to access this page."
        )

    context = {}
    context.update(extra_context)
    context["page"] = page

    person = page.person
    if not hasattr(person, "directoryentry_set"):
        context["error"] = "The directory application is not installed."
        messages.error(request, context["error"], fail_silently=True)
        return render(request, template_name, context)

    entry_list = person.directoryentry_set.all()
    if len(entry_list) == 0:
        context["error"] = "There are no directory entries to update."
        messages.error(request, context["error"], fail_silently=True)
        return render(request, template_name, context)

    if pageinfo.photo is None:
        context["error"] = "There is no image to crop."
        messages.error(request, context["error"], fail_silently=True)
        return render(request, template_name, context)

    im = face_detect.detect_face_crop(pageinfo.photo)
    if im is None:
        # context['error'] = "No face detected in this image"
        context["error"] = "There was a problem automatically detecting a mugshot."
        messages.error(request, context["error"], fail_silently=True)
        return render(request, template_name, context)

    format = os.path.splitext(pageinfo.photo.name)[-1][1:].upper()
    image = face_detect.image_as_djangofile(im, basename=person.slug, format=format)
    for entry in entry_list:
        entry.mugshot = image
        entry.save()

    if len(entry_list) == 1:
        msg = "Mugshot updated"
    else:
        msg = "All mugshots updated ({} total)".format(len(entry_list))
    messages.success(request, msg, fail_silently=True)
    return HttpResponseRedirect(page.get_absolute_url())


######################################################################
