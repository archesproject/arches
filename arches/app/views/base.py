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


from arches.app.models import models
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer
from django.views.generic import TemplateView

class BaseManagerView(TemplateView):

    template_name = ''

    def get_default_nav(self):
        ''' returns a default set values to configure the nav bar. some of
        these values will be overwritten at the individual view level.'''

        return  {
            'page_icon':'fa-question',
            'page_title':'',
            'help_title':'',
            'help_template':'',
            'resource_manage_menu':False,
            'graph_manage_menu':False,
            'search':True,
            'edit_history':False,
            'login':True,
        }

    def get_context_data(self, **kwargs):
        context = super(BaseManagerView, self).get_context_data(**kwargs)
        context['graph_models'] = models.GraphModel.objects.all()
        context['graphs'] = JSONSerializer().serialize(context['graph_models'])

        return context
