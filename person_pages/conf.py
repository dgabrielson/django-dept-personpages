"""
The DEFAULT configuration is loaded when the CONFIG_NAME dictionary
is not present in your settings.

All valid application settings must have a default value.
"""

CONFIG_NAME = "PERSONPAGE_CONFIG"  # must be uppercase!


DEFAULT = {
    # where personal files are loaded -- note that these are not
    # broken out for individuals.
    "upload_path": "personal/%Y/%m/%d",
    "restructuredtext_help": """This will be processed as
<a href="http://docutils.sourceforge.net/docs/user/rst/quickref.html" target="_blank">
ReStructuredText</a>.""",
    "photo_help": """This should be a picture of yourself,
between 250 and 400 pixels wide (no more).""",
}


from django.conf import settings


def get(setting):
    """
    get(setting) -> value

    setting should be a string representing the application settings to
    retrieve.
    """
    assert setting in DEFAULT, "the setting %r has no default value" % setting
    app_settings = getattr(settings, CONFIG_NAME, DEFAULT)
    return app_settings.get(setting, DEFAULT[setting])


def get_all():
    """
    Return all current settings as a dictionary.
    """
    app_settings = getattr(settings, CONFIG_NAME, DEFAULT)
    return dict(
        [(setting, app_settings.get(setting, DEFAULT[setting])) for setting in DEFAULT]
    )
