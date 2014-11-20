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

from django.conf import settings
from arches.app.models.entity import Entity
from django.utils.translation import ugettext as _

class Resource(Entity):
    # def __new__(cls, *args, **kwargs):
    #     kwargs['mod'] = ''
    #     return super(Resource, cls).__new__(cls, *args, **kwargs)
    """ 
    Used for managing Resrouce type entities

    This class will return an instance of the class defined in settings.RESOURCE_MODEL
    The class defined in settings.ENTITY_MODEL must be a subclass of this class (arches.app.models.entity.Entity)

    """
    def __new__(cls, *args, **kwargs):
        modulename = kwargs.get('mod', 'default')
        if modulename == '':
            return super(Entity, cls).__new__(cls)
        else:
            fully_qualified_modulename = settings.RESOURCE_MODEL.get(modulename)
            components = fully_qualified_modulename.split('.')
            classname = components[len(components)-1]
            modulename = ('.').join(components[0:len(components)-1])
            kwargs['mod'] = ''
            mod = __import__(modulename, globals(), locals(), [classname], -1)
            if issubclass(getattr(mod, classname), Entity):
                return getattr(mod, classname)(*args, **kwargs)
            else:
                raise Exception('The class "%s" defined in settings.RESOURCE_MODEL must be a subclass of arches.app.models.resource.Resource' % fully_qualified_modulename)


    def __init__(self, *args, **kwargs):
        super(Resource, self).__init__(*args, **kwargs)

        self.form_groups = []
    

    def get_form(self, form_id):
        selected_form = None
        forms = [form for group in self.form_groups for form in group['forms']]
        for form in forms:
            if form.id == form_id:
                selected_form = form
        return selected_form(self)

    def get_type_name(self):
        resource_name = ''
        for resource_type in self.get_resource_types():
            if resource_type['resourcetypeid'] == self.entitytypeid:
                return resource_type['name']
        return resource_name


    def get_name(self):
        return _('Unnamed Resource')


    @staticmethod
    def get_resource_types():
        raise NotImplementedError



# # Here's what I'd like to be able to do

# resource = Resource('0538a60a-2816-3b0b-9415-124e2aad65cd') # a heritage resource guid, populates the Resource with data from the db
# resource = Resource(Entity({entitytypeid: 'HeritageResource.E32'})) # a heritage resource type id, returns a blank resource
# # now we have a resource that "knows" it's a heritage resource
# # forms aren't populated until we access them

# # resource has specific methods to perform CRUD on specific portions of itself as view models (for forms etc..)
# summary_form = resource.forms.get('summary')
# resource.forms.set('summary', formdata)
# resource.save() # this method calls save on the forms themselves


# class Form(object):
#     self.icon = ''
#     self.displayname = ''
#     ....
#     pass


# class SummaryForm(Form):  # this form is specific to a certain resource graph shape (could be used across multiple entitytypes)
#     def __init__(self, *args, **kwargs):
#         self.names = []
#         self.importantdates = []
#         self.subjects = []
#         self.resource = None
    
#     def get():
#         # populates itself based on its Entity
#         # here's where we parse a enitty into it's constitutant parts
#         return self

#     def set(data):
#         pass

# class DescriptionForm(Form):  # this form is specific to a certain resource graph shape (could be used across multiple entitytypes)
#     def __init__(self, *args, **kwargs):
#         self.description = []
    
#     def get():
#         # populates itself based on its Entity
#         # here's where we parse a enitty into it's constitutant parts
#         for item in self.find_entities_by_type_id('DESCRIPTION.E83')
#             self.description['type'] = item.get_entity_value # here's where we populate the actual value
#             self.description['description'] = item.get_entity_value
#         return self

#     def set(data):
#         pass

# class InformationResourceSummaryForm(Form):
#     pass

# class FormManager():
#     def get(formname):
#         form = self.forms[formname]
#         return form.get()

#     def set(formname, data):
#         form = self.forms[formname]
#         form.set(data)
#         return form


# class HeritageDistrictForms(FormManager):
#     forms = {
#         'summary': SummaryForm(),
#         'description': DescriptionForm(),
#         ....
#     }

# class ActorForms(FormManager):
#     forms = {
#         'summary': ActorSummaryForm(),
#         'description': DescriptionForm(),
#         ....
#     }

