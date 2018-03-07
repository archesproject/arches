'''
ARCHES - a program developed to inventory and manage immovable cultural heritage.
Copyright (C) 2013 J. Paul Getty Trust and World Monuments Fund

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
'''

# from datetime import datetime
from django.conf import settings
from django.template import RequestContext
from django.shortcuts import render_to_response
from arches.app.models import models
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.models import User
from arches.app.utils.JSONResponse import JSONResponse
import json
import logging

@permission_required('edit')
def group_activity(request, groupid):
    user_ids = []
    ret_summary = {}
    current = None
    index = -1
    start = request.GET.get('start', 0)
    limit = request.GET.get('limit', 99)

    if groupid != '':
        users = User.objects.filter(groups__id=groupid)
        for user in users:
            user_ids.append({'id': user.id, 'name': str(user)})

    return render_to_response('group_activity.htm', {
            'groupid': groupid,
            'user_ids': user_ids,
            'main_script': 'group-chart',
        }, 
        context_instance=RequestContext(request))
            
def group_activity_data(request, groupid):
    ret_summary = {}
    current = None
    index = -1
    start = request.GET.get('start', 0)
    limit = request.GET.get('limit', 99)

    if groupid != '':
        users = User.objects.filter(groups__id=groupid)
        for user in users:
            ret_summary[user.id] = {'id': user.id, 'name': str(user), 'startDate': "",'data': {}}
            for log in models.EditLog.objects.filter(userid = user.id).values().order_by('-timestamp', 'attributeentitytypeid'):
                ret_summary[user.id]['startDate'] = str(log['timestamp'].date())
                
                if str(log['timestamp'].date()) not in ret_summary[user.id]['data']:
                    ret_summary[user.id]['data'][str(log['timestamp'].date())] = {}
                
                if log['resourceid'] not in ret_summary[user.id]['data'][str(log['timestamp'].date())]:
                    ret_summary[user.id]['data'][str(log['timestamp'].date())][log['resourceid']] = {
                        'create': 0, 'update': 0, 'insert': 0, 'delete': 0
                    }
    
                ret_summary[user.id]['data'][str(log['timestamp'].date())][log['resourceid']][log['edittype']] = 1;
    
    return JSONResponse(ret_summary)
