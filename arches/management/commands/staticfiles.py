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

import inspect
import os
from django.db import connection
from cStringIO import StringIO
from django.conf import settings
import utils
from arches import version
import arches.app.models.models as archesmodels
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer
from arches.app.utils import dictfetchall

def generate_files(rootpath):
    cur = connection.cursor()
    #cur.execute("SELECT table_schema, table_name, column_name, column_default, is_nullable, data_type, udt_name, is_updatable," 
	#    "CASE WHEN app.is_primary_key(table_schema||'.'||table_name) = column_name THEN 'YES'"
    #          	    "ELSE 'NO'"
    #   			    "END as is_pk "
	#   "FROM information_schema.columns "
	#   "WHERE table_schema = 'app_metadata' AND "
	#   "table_name = 'app_strings' AND "
	#   "column_name != 'key';")
    
    cur.execute("""SELECT distinct languageid
                    FROM app_metadata.i18n;""")

    languages = cur.fetchall()

    sb = StringIO()

    i18ndir = os.path.join(rootpath, 'media','js','i18n')

    for language in languages:
        lang =  language[0]
        i18nFileName = os.path.join(i18ndir, lang + ".js")
        

        sb.writelines(["if (typeof Arches.i18n != 'object') {Arches.i18n = {};}\n"])
        utils.write_to_file(i18nFileName, sb.getvalue())
        sb.truncate(0)

        create_namespace(sb, i18nFileName)
        
        write_localized_text_strings(cur, sb, lang, i18nFileName)
        write_forms(cur,sb, lang, i18nFileName)
        write_information_themes(cur,sb, lang, i18nFileName)
        write_entity_types(cur,sb, lang, i18nFileName)
        #write_properties(cur,sb, lang, i18nFileName)
        #write_localized_displays(cur,sb, lang, i18nFileName)
        write_map_layers(cur,sb, lang, i18nFileName)

    write_app_config(cur, sb, os.path.join(rootpath, 'media','js','debug', 'config', 'app.js'))


# write out all data from the app_metadata.i18n table
def write_localized_text_strings(cur, sb, lang, filename):
    cur.execute("SELECT key, languageid, value, widgetname "
		"FROM app_metadata.i18n "
        "WHERE languageid =  '" + lang + "' "
		"ORDER BY languageid, widgetname;")

    rows = cur.fetchall()    

    widgetName = ""
    properties = []

    for row in rows:
        # write out a namespace for each new widget
        if (widgetName != row[3].strip()):
            if (widgetName != ''):
                create_ext_override(sb, filename, widgetName, ",".join(properties))
            properties = []
            widgetName = row[3].strip()

        # write out the json string value
        if row[2].strip() != "":
            properties.append("'" + row[0].strip() + "' : '" + row[2].strip().replace("'","\\'") + "'")

    create_ext_override(sb, filename, widgetName, ",".join(properties))


def write_forms(cur, sb, lang, filename):
    cur.execute("SELECT formid, app_metadata.get_i18n_value(name_i18n_key, '" + lang + "', widgetname) as name, widgetname "
                "FROM app_metadata.forms;")

    rows = cur.fetchall()

    sb.writelines(["Arches.createNamespace('Arches.i18n.DomainData.Forms');\n"])
    data = []
    for row in rows:
        a = Form()
        a.id = row[0]
        a.name = row[1]
        a.widgetname = row[2]
        data.append(a)

    ret = "Arches.i18n.DomainData.Forms=" + JSONSerializer().serialize(data, ensure_ascii=False) + ";\n"
    sb.writelines(ret)

    utils.write_to_file(filename, sb.getvalue(), 'a')
    sb.truncate(0)


def write_information_themes(cur, sb, lang, filename):
    cur.execute("""
        SELECT a.informationthemeid, 
            app_metadata.get_i18n_value(a.name_i18n_key, '""" + lang + """', '') as name, 
            a.displayclass, 
            a.entitytypeid,
            d.formid, 
            d.sortorder
        FROM app_metadata.information_themes a
        LEFT JOIN app_metadata.information_themes_x_forms d ON a.informationthemeid = d.informationthemeid
        order by informationthemeid;
    """)

    rows = cur.fetchall()

    sb.writelines(["Arches.createNamespace('Arches.i18n.DomainData.InformationThemes');\n"])

    a = None
    data = []
    currententitytypeid = ''

    for row in rows:
        if currententitytypeid != row[0] and currententitytypeid != '':
            data.append(a)
        if currententitytypeid != row[0]:
            currententitytypeid = row[0]
            a = InformationTheme()
            a.id = row[0]
            a.name = row[1]
            a.displayclass = row[2]
            a.entitytypeid = row[3]
        if currententitytypeid == row[0]:
            a.forms.append({'formid': row[4], 'sortorder': row[5]})
    if a != None: 
        data.append(a)

    ret = "Arches.i18n.DomainData.InformationThemes=" + JSONSerializer().serialize(data, ensure_ascii=False) + ";\n"
    sb.writelines(ret)

    utils.write_to_file(filename, sb.getvalue(), 'a')
    sb.truncate(0)


def write_entity_types(cur, sb, lang, filename):
    cur.execute("""
        SELECT 
            a.entitytypeid, 
            lbl.value AS entitytypename, 
            (SELECT n.value
                FROM concepts.values n
                WHERE n.conceptid = a.conceptid AND n.languageid = lbl.languageid
                AND valuetype = 'scopeNote'
                LIMIT 1) AS description,  
            lbl.languageid, 
            (SELECT r.widgetname
                FROM app_metadata.reports r
                LEFT JOIN app_metadata.entity_type_x_reports bb ON a.entitytypeid = bb.entitytypeid
                LEFT JOIN app_metadata.reports cc ON r.reportid = cc.reportid
                WHERE bb.entitytypeid = a.entitytypeid
                LIMIT 1) AS reportwidget, 
             a.icon, 
             a.isresource, 
             a.conceptid,
             a.groupid,
             (SELECT value
                FROM app_metadata.i18n
                WHERE languageid =  '""" + lang + """'
                AND key = rg.name_i18n_key) AS groupname,
             rg.displayclass AS groupdisplayclass
        FROM data.entity_types a
        LEFT JOIN concepts.concepts dv ON a.conceptid = dv.conceptid
        LEFT JOIN concepts.values lbl ON dv.conceptid = lbl.conceptid
        LEFT JOIN app_metadata.resource_groups rg on a.groupid = rg.groupid
		WHERE 1=1
		 and lbl.valuetype = 'prefLabel'
        order by entitytypeid;
   """)


    rows = cur.fetchall()

    sb.writelines(["Arches.createNamespace('Arches.i18n.DomainData.EntityTypes');\n"])

    a = None
    data = []
    currententitytypeid = ''

    for row in rows:
        if currententitytypeid != row[0] and currententitytypeid != '':
            data.append(a)
        if currententitytypeid != row[0]:
            currententitytypeid = row[0]
            a = EntityType()
            a.entitytypeid = row[0]
            a.entitytypename = row[1]
            a.description = row[2]
            a.reportwidget = row[4]
            a.icon = row[5]
            a.isresource = row[6]
            a.groupname = row[9]
            a.groupdisplayclass = row[10]
    if a != None: 
        data.append(a)

    ret = "Arches.i18n.DomainData.EntityTypes=" + JSONSerializer().serialize(data, ensure_ascii=False) + ";\n"
    sb.writelines(ret)

    utils.write_to_file(filename, sb.getvalue(), 'a')
    sb.truncate(0)


def write_properties(cur, sb, lang, filename):
    cur.execute("SELECT properties.propertyid, properties.propertyname, properties.propertydisplay " 
                "FROM ontology.properties;")

    rows = cur.fetchall()

    sb.writelines(["Arches.createNamespace('Arches.i18n.DomainData.Properties');\n"])

    a = None
    data = []
    for row in rows:
        a = Property()
        a.propertyid = row[0]
        a.propertyname = row[1]
        a.displayvalue = row[2]
        data.append(a)

    ret = "Arches.i18n.DomainData.Properties=" + JSONSerializer().serialize(data, ensure_ascii=False) + ";\n"
    sb.writelines(ret)

    utils.write_to_file(filename, sb.getvalue(), 'a')
    sb.truncate(0)


def write_localized_displays(cur, sb, lang, filename):
    cur.execute("SELECT labelid, label "
                "FROM concepts.labels "
                "WHERE languageid =  '" + lang + "';")

    rows = cur.fetchall()

    a = None
    data = {}
    for row in rows:
        data[row[0]] = row[1]

    ret = "Arches.i18n.DomainData.ConceptSchemaLabels=" + JSONSerializer().serialize(data, ensure_ascii=True) + ";\n"
    sb.writelines(ret)

    utils.write_to_file(filename, sb.getvalue(), 'a')
    sb.truncate(0)

def write_map_layers(cur, sb, lang, filename):
    """ Writes out all the layers in the maplayers table to the localized text files (en-us.js for example).
        If there is more then 1 language defined for the app then all layers will be 
        written to every localized file regardless of whether the name of the of the MapLayer
        has been locaized or not.  

        This is to make sure that all the layers are available in all languages regardless of
        the status of the localization effort.

    """
    basemaps = []
    layergroups = []

    sb.writelines(["Arches.createNamespace('Arches.i18n.MapLayers');\n"])

    # first get the list of all layer ids
    cur.execute("SELECT id FROM app_metadata.maplayers ORDER BY layergroup_i18n_key")
    layerids = cur.fetchall()

    for layerid in layerids:
        # try and get the localized layer info
        cur.execute("""SELECT id, active, on_map as \"onMap\", selectable, 
                        basemap, app_metadata.get_i18n_value(name_i18n_key, %s, '') as name, icon, symbology, thumbnail, 
                        app_metadata.get_i18n_value(description_i18n_key, %s, '') as description, 
                        app_metadata.get_i18n_value(layergroup_i18n_key, %s, '') as layergroup, layer, sortorder 
                    FROM app_metadata.maplayers 
                    WHERE maplayers.id =  %s """, [lang, lang, lang, layerid])

        rows = dictfetchall(cur)

        # if the layer name hasn't been localized fall back to the default language
        if len(rows) == 0:
            cur.execute("SELECT id, active, on_map as \"onMap\", selectable, "
                            "basemap, app_metadata.get_i18n_value(name_i18n_key, %s, '') as name, icon, symbology, thumbnail, "
                            "app_metadata.get_i18n_value(description_i18n_key, %s, '') as description, "
                            "app_metadata.get_i18n_value(layergroup_i18n_key, %s, '') as layergroup, layer, sortorder "
                        "FROM app_metadata.maplayers "
                        "WHERE maplayers.id =  %s ", [lang, lang, lang, layerid])

            rows = dictfetchall(cur)          

        # write out basemaps first
        for row in rows:
            if row['basemap'] == True:
                basemaps.append(row)

        # write out all other layers next
        for row in rows:
            if row['basemap'] == False:
                if has_name(layergroups, row['layergroup']):
                    get_layergroup_by_name(layergroups, row['layergroup']).layers.append(row)
                else:
                    layergroups.append(LayerGroup(row['layergroup']))
                    get_layergroup_by_name(layergroups, row['layergroup']).layers.append(row)


    ret = "Arches.i18n.MapLayers.basemaps=" + JSONSerializer().serialize(basemaps, ensure_ascii=False) + ";\n"
    sb.writelines(ret)
    utils.write_to_file(filename, sb.getvalue(), 'a')
    sb.truncate(0)    

    ret = "Arches.i18n.MapLayers.layerGroups=" + JSONSerializer().serialize(layergroups, ensure_ascii=False) + ";\n"
    sb.writelines(ret)
    utils.write_to_file(filename, sb.getvalue(), 'a')
    sb.truncate(0)    

def write_app_config(cur, sb, filename):
    cur.execute("SELECT name, defaultvalue, datatype "
                "FROM app_metadata.app_config "
                "WHERE isprivate = False;")

    rows = cur.fetchall()

    sb.writelines(["Ext.namespace('Arches.config.App');\n"])
    sb.writelines(["Arches.config.App = {\n"])

    data = []
    currententitytypeid = ''
    for row in rows:
        if row[2] == 'text':
            data.append("\t" + row[0] + ": '" + row[1] + "'")
        else:
            data.append("\t" + row[0] + ": " + row[1] + "")  

    pname_info = {}
    # find primary name information
    for pname_key in settings.PRIMARY_DISPLAY_NAME_LOOKUPS:
        entitytypes = archesmodels.EntityTypes.objects.filter(pk = settings.PRIMARY_DISPLAY_NAME_LOOKUPS[pname_key]['entity_type'])
        if len(entitytypes) == 1:
            concept = entitytypes[0].conceptid
            concept_graph = concept.graph()
            
            def findLabel(concept, labelToFind):
                for label in concept.labels:
                    if label.value == labelToFind:
                        return label
                
                if(len(concept.subconcepts) > 0):
                    for subconcept in concept.subconcepts:
                        return findLabel(subconcept, labelToFind)
            
            concept_label = findLabel(concept_graph, settings.PRIMARY_DISPLAY_NAME_LOOKUPS[pname_key]['lookup_value']);
            pname_info[pname_key] = concept_label
            
    data.append("\tprimaryNameInfo:%s" % (JSONSerializer().serialize(pname_info, ensure_ascii=False, indent=8)))        
        
    data.append("\tarches_version:'%s'" % version.__VERSION__) 

    sb.writelines(",\n".join(data) + "\n};")

    utils.write_to_file(filename, sb.getvalue(), 'w')
    sb.truncate(0)

# writes out a javascript fuction to create a namespace
def create_namespace(sb,filename):
    sb.writelines([
        "Arches.createNamespace = function(stringToParse) {"
            "var parts = [], root = window, part, i, j, ln, subLn;"
            "parts = parts.concat(stringToParse.split('.'));"

            "for (j = 0, subLn = parts.length; j < subLn; j++) {"
                "part = parts[j];"

                "if (typeof part !== 'string') {"
                    "root = part;"
                "} else {"
                    "if (!root[part]) {"
                        "root[part] = {};"
                    "}"

                    "root = root[part];"
                "}"
            "}"
            "return root;"
        "}\n"])
    utils.write_to_file(filename, sb.getvalue(), 'a')
    sb.truncate(0)

# writes out a javascript function to create and Ext.override of i18n object within a widget
def create_ext_override(sb, filename, widgetname, object):
    sb.writelines(["Ext.merge(" + widgetname + ".prototype , {i18n: {" + object + "}});\n"])
    utils.write_to_file(filename, sb.getvalue(), 'a')
    sb.truncate(0)

class AssetClass(object):
    def __init__(self):
        self.name = ''
        self.description = ''
        self.icon = ''

class Form(object):
    def __init__(self):
        self.id = ''
        self.name = ''
        self.widgetname = ''

class InformationTheme(object):
    def __init__(self):
        self.id = ''
        self.name = ''
        self.displayclass = ''
        self.entitytypeid = ''
        self.forms = []

class EntityType(object):
    def __init__(self):
        self.entitytypeid = ''
        self.entitytypename = ''
        self.description = ''
        self.forms = []
        self.reportwidget = ''
        self.icon = ''
        self.isresource = None
        self.groupdisplayclass = ''
        self.groupname = ''

class Property(object):
    def __init__(self):
        self.propertyid = ''
        self.propertyname = ''
        self.displayvalue = ''

class LocalizedDisplay(object):
    def __init__(self):
        self.recordid = ''
        self.displayvalue = ''

class LayerGroup(object):
    def __init__(self, name):
        self.name = name
        self.layers = []
    def addLayer(layer):
        self.layers.append(layer)

def has_name(layergroups, name):
    ret = False
    for layergroup in layergroups:
        if layergroup.name == name:
            ret = True
    return ret

def get_layergroup_by_name(layergroups, name):
    ret = None
    for layergroup in layergroups:
        if layergroup.name == name:
            return layergroup
    return ret
