This directory is used as the default directory for loading package system
settings data. This is also the default directory that will be used when exporting
system settings. Do not edit settings in this directory unless you are doing so for
development purposes. Instead, use the system settings manager in the Arches UI.
If you want to export your system settings from Arches, you can do so with the
following command:

> python manage.py packages -o save_system_settings
