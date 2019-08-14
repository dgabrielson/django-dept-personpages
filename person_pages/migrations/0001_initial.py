# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("people", "0001_initial")]

    operations = [
        migrations.CreateModel(
            name="PageFile",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                (
                    "slug",
                    models.SlugField(help_text=b"A url fragment to identify this file"),
                ),
                (
                    "description",
                    models.CharField(
                        help_text=b"(Optional) A short description of the file",
                        max_length=250,
                        blank=True,
                    ),
                ),
                (
                    "the_file",
                    models.FileField(
                        help_text=b"The file.", upload_to=b"personal/%Y/%m/%d"
                    ),
                ),
                (
                    "show_link",
                    models.BooleanField(
                        default=False,
                        help_text=b"Select this to have a link to this file at the bottom of your personal page",
                    ),
                ),
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="PageInfo",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                (
                    "created",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name=b"creation time"
                    ),
                ),
                (
                    "modified",
                    models.DateTimeField(
                        auto_now=True, verbose_name=b"last modification time"
                    ),
                ),
                (
                    "photo",
                    models.ImageField(
                        help_text=b"This should be a picture of yourself,\nbetween 250 and 400 pixels wide (no more).",
                        upload_to=b"personal/%Y/%m/%d",
                        blank=True,
                    ),
                ),
                (
                    "introduction",
                    models.TextField(
                        help_text=b'Page introduction. This will be processed as\n<a href="http://docutils.sourceforge.net/docs/user/rst/quickref.html" target="_blank">\nReStructuredText</a>.',
                        blank=True,
                    ),
                ),
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="PageSection",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                (
                    "active",
                    models.BooleanField(
                        default=True,
                        help_text=b"If this is checked, the section will be shown, if not, it will be hidden.",
                    ),
                ),
                (
                    "created",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name=b"creation time"
                    ),
                ),
                (
                    "modified",
                    models.DateTimeField(
                        auto_now=True, verbose_name=b"last modification time"
                    ),
                ),
                (
                    "ordering",
                    models.PositiveSmallIntegerField(
                        default=0,
                        help_text=b"This will determine the display order of the  sections on your page.",
                    ),
                ),
                (
                    "title",
                    models.CharField(
                        help_text=b"The title for the section", max_length=250
                    ),
                ),
                (
                    "content",
                    models.TextField(
                        help_text=b'The text for this section. This will be processed as\n<a href="http://docutils.sourceforge.net/docs/user/rst/quickref.html" target="_blank">\nReStructuredText</a>.'
                    ),
                ),
            ],
            options={"ordering": ["ordering"]},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="PersonPage",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ("active", models.BooleanField(default=True)),
                (
                    "created",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name=b"creation time"
                    ),
                ),
                (
                    "modified",
                    models.DateTimeField(
                        auto_now=True, verbose_name=b"last modification time"
                    ),
                ),
                (
                    "allow_owner_edits",
                    models.BooleanField(
                        default=False,
                        help_text=b"If this is set, then the owner of the page can make their own updates",
                    ),
                ),
                (
                    "person",
                    models.ForeignKey(
                        on_delete=models.deletion.CASCADE,
                        to="people.Person",
                        help_text=b'Only people with slug fields and the "directory" flag are shown',
                        unique=True,
                    ),
                ),
            ],
            options={"ordering": ["person"]},
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name="pagesection",
            name="page",
            field=models.ForeignKey(
                on_delete=models.deletion.CASCADE, to="person_pages.PersonPage"
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="pageinfo",
            name="page",
            field=models.OneToOneField(
                on_delete=models.deletion.CASCADE, to="person_pages.PersonPage"
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="pagefile",
            name="page",
            field=models.ForeignKey(
                on_delete=models.deletion.CASCADE, to="person_pages.PersonPage"
            ),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name="pagefile", unique_together=set([("page", "slug")])
        ),
    ]
