#!/usr/bin/env python
import sys
import os
try:
    from django.core.management import execute_manager
    OLD_DJANGO = True
except ImportError:
    from django.core.management import execute_from_command_line
    OLD_DJANGO = False

if OLD_DJANGO:
    try:
        import settings  # Assumed to be in the same directory.
    except ImportError:
        sys.stderr.write("Error: Can't find the file 'settings.py' in the directory containing %r. It appears you've customized things.\nYou'll have to run django-admin.py, passing it your settings module.\n(If the file settings.py does indeed exist, it's causing an ImportError somehow.)\n" % __file__)
        sys.exit(1)

BASEDIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, BASEDIR)

if __name__ == "__main__":
    os.environ["DJANGO_SETTINGS_MODULE"] = "testproject.settings"
    if OLD_DJANGO:
        execute_manager(settings)
    else:
        execute_from_command_line(sys.argv)
