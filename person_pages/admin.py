"""
Person Pages admin
"""
from django.contrib import admin

from .forms import AdminPageInfoForm, PageFileForm, PageSectionForm
from .models import PageFile, PageInfo, PageSection, PersonPage

######################################################################


class PageInfoInline(admin.TabularInline):
    model = PageInfo
    extra = 0
    form = AdminPageInfoForm


class PageSectionInline(admin.TabularInline):
    model = PageSection
    extra = 0
    form = PageSectionForm


class PageFileInline(admin.TabularInline):
    model = PageFile
    extra = 0
    form = PageFileForm


class PersonPageAdmin(admin.ModelAdmin):
    inlines = [PageInfoInline, PageSectionInline, PageFileInline]
    list_display = ["person", "active", "allow_owner_edits"]
    list_filter = ["active", "created", "modified", "allow_owner_edits"]
    search_fields = ["person__cn", "person__slug"]
    ordering = ["person"]
    save_on_top = True


admin.site.register(PersonPage, PersonPageAdmin)


######################################################################
