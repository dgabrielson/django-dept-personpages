# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("person_pages", "0001_initial")]

    operations = [
        migrations.AlterField(
            model_name="personpage",
            name="person",
            field=models.OneToOneField(
                on_delete=models.deletion.CASCADE,
                to="people.Person",
                help_text=b'Only people with slug fields and the "directory" flag are shown',
            ),
        )
    ]
