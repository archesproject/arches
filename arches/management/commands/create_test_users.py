# uncompyle6 version 2.13.2
# Python bytecode 2.7 (62211)
# Decompiled from: Python 2.7.10 (default, Feb  7 2017, 00:08:15) 
# [GCC 4.2.1 Compatible Apple LLVM 8.0.0 (clang-800.0.34)]
# Embedded file name: /Users/cyrus/Documents/projects/GCI/arches_v4/arches/arches/management/commands/create_test_users.py
# Compiled at: 2017-06-06 11:18:30
from django.contrib.auth.models import User, Group
from arches.app.models.system_settings import settings
from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    """
    Command for adding users
    
    """

    def add_arguments(self, parser):
        parser.add_argument('operation', nargs='?')

    def handle(self, *args, **options):
        print 'Creating users'

    user_group_lookup = {'application_administrator': 'Application Administrator',
       'crowdsource_editor': 'Crowdsource Editor',
       'graph_editor': 'Graph Editor',
       'guest': 'Guest',
       'mobile_project_administrator': 'Mobile Project Administrator',
       'rdm_administrator': 'RDM Administrator',
       'resource_editor': 'Resource Editor',
       'system_administrator': 'System Administrator'
       }
    users = [
     ('application_administrator', 'test'),
     ('crowdsource_editor', 'test'),
     ('graph_editor', 'test'),
     ('guest', 'test'),
     ('mobile_project_administrator', 'test'),
     ('rdm_administrator', 'test'),
     ('resource_editor', 'test'),
     ('system_administrator', 'test')]
    for u in users:
        try:
            user = User.objects.create_user(username=u[0], password=u[1])
            user.groups.add(Group.objects.filter(name=user_group_lookup[u[0]])[0])
            user.save()
        except:
            print u