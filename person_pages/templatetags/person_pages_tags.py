"""
Activate in your template by putting
{% load person_pages_extras %}
near the top.


Available Filters:
prerender - Evaluate as a django template
restructuredtext - Evaulate as ReST, ala django.contrib.markup.


Available Commands:
personalfile_url - provide an href to a pagefile by slug.
"""
#######################
from __future__ import print_function, unicode_literals

import os

#######################
import re

from django import template
from django.conf import settings
from django.template import Context, Template
from django.urls import reverse
from django.utils.encoding import force_text, smart_str
from django.utils.safestring import mark_safe
from docutils.core import publish_parts

from ..models import PageFile

#####################################################################

register = template.Library()

#####################################################################


class PageFile_Url_Node(template.Node):
    def __init__(
        self,
        tag_name,
        person_slug,
        person_literal,
        file_slug,
        file_literal,
        context_name,
    ):
        self.tag_name = tag_name
        self.person_slug = person_slug
        self.person_literal = person_literal
        self.file_slug = file_slug
        self.file_literal = file_literal
        self.context_name = context_name

    def _resolve_slug(self, slug, literal, context):
        "Resolve a slug appropraitely"
        if literal:
            return slug
        else:
            if slug not in context:
                raise template.TemplateSyntaxError(
                    "%r tag: variable %r not defined in this block"
                    % (self.tag_name, slug)
                )
            return context[slug]

    def render(self, context):
        "Render this tag"
        person_slug = self._resolve_slug(self.person_slug, self.person_literal, context)
        file_slug = self._resolve_slug(self.file_slug, self.file_literal, context)

        try:
            o = PageFile.objects.get(
                page__active=True,
                page__person__slug__iexact=person_slug,
                slug__iexact=file_slug,
            )
            url = o.get_absolute_url()
        except PageFile.DoesNotExist:
            url = ""

        if self.context_name is not None:
            context[self.context_name] = url
            return ""
        else:
            return url


@register.tag
def personalfile_url(parser, token):
    """
    Usage:
        {% personalfile_url "person-slug" "file-slug" %}
        -or-
        {% personalfile_url "person-slug" "file-slug" as link_url %}

    """
    token_contents = token.split_contents()

    tag_name = token_contents[0]

    if len(token_contents) < 3:
        raise template.TemplateSyntaxError("%r tag requires arguments" % tag_name)

    if len(token_contents) not in [3, 5]:
        raise template.TemplateSyntaxError("%r tag: invalid syntax" % tag_name)

    def _get_slug(slug):
        """returns slug, literal pair"""
        if slug[0] in "'\"":
            if slug[0] != slug[-1]:
                raise template.TemplateSyntaxError(
                    "mismatched quotes for %r tag" % tag_name
                )
            slug = slug[1:-1]
            literal = True
        else:
            literal = False
        return slug, literal

    person_slug, person_literal = _get_slug(token_contents[1])
    file_slug, file_literal = _get_slug(token_contents[2])

    context_name = None
    if len(token_contents) == 5:
        if token_contents[3] != "as":
            raise template.TemplateSyntaxError("invalid syntax for %r tag" % tag_name)
        context_name = token_contents[4]

    return PageFile_Url_Node(
        tag_name, person_slug, person_literal, file_slug, file_literal, context_name
    )


#####################################################################


@register.filter(name="prerender")
def render_as_template(text):
    """
    """
    this_file = os.path.splitext(os.path.split(__file__)[-1])[0]
    template_text = "{% load " + this_file + " %}\n" + text
    t = Template(template_text)
    output = t.render(Context({}))
    return output


render_as_template.is_safe = True


#####################################################################


def restructuredtext(value):
    """
    Copied from django.contrib.markup.templatetags.markup
    """
    docutils_settings = getattr(settings, "RESTRUCTUREDTEXT_FILTER_SETTINGS", {})
    parts = publish_parts(
        source=smart_str(value),
        writer_name="html4css1",
        settings_overrides=docutils_settings,
    )
    return mark_safe(force_text(parts["fragment"]))


restructuredtext.is_safe = True

register.filter(restructuredtext)

#####################################################################
