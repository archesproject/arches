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

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.cache import never_cache
from django.contrib.auth import authenticate, login, logout
from arches.app.utils.betterJSONSerializer import JSONSerializer


@csrf_exempt
@never_cache
def Login(request):
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(username=username, password=password)
    ret = user
    if user is not None:
        if user.is_active:
            login(request, user)
        else:
            # Return a 'disabled account' error message
            ret = {'error': 'account disabled'}

        # don't send the password even if it is hashed
        user.password = ''
    else:
        # Return an 'invalid login' error message.
        ret = {'error': 'invalid login'}

    return HttpResponse(JSONSerializer().serialize(ret))


@never_cache
def Logout(request):
    logout(request)
    ret = {'message': 'Logout successful'}

    return HttpResponse(JSONSerializer().serialize(ret))


@never_cache
def GetUser(request):
    if request.user.is_authenticated():
        ret = request.user
    else:
        ret = {'message': 'User not authenticated'}

    return HttpResponse(JSONSerializer().serialize(ret))
