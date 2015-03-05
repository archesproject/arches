from django.conf import settings
import os
import datetime
from arches.app.models.concept import Concept
import xml.etree.ElementTree as ET
from format import Writer

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

class KmlWriter(Writer):

    def __init__(self):
        self.resource_type_configs = settings.RESOURCE_TYPE_CONFIGS()
        self.default_mapping = {
            "NAME": "ArchesResourceExport",
            "SCHEMA": [
                {"field_name":"primary_name", "source":"primaryname"},
                {"field_name":"arches_id", "source":"entityid"},
                {"field_name":"arches_resource_type", "source":"resource_name"},
                {"field_name":"geometry", "source":"geometries"},
            ],
            "RESOURCE_TYPES" : {},
            "RECORDS":[]
        }  

    def create_kml(self, feature_collection, kml_name):
        """
        Takes a list of geojson dictionaries - with geometry still as a geos object and converts them to an ElementTree object with KML tags
        and attributes. Returns a kml version of the object.
        """
        root = ET.Element("kml", attrib={'xmlns':'http://earth.google.com/kml/2.0'})
        folder = ET.SubElement(root, "Folder")
        name = ET.SubElement(folder, "name")
        name.text = 'search-result-export'
        description = ET.SubElement(folder, 'description')
        description.text = 'Search Export Results'
        style = ET.SubElement(folder, 'Style', attrib={'id':'resource_style'})
        linestyle = ET.SubElement(style, 'LineStyle')
        width = ET.SubElement(linestyle, 'width')
        width.text = '2.0'
        line_color = ET.SubElement(linestyle, 'color')
        line_color.text = '7d0000ff'
        polystyle = ET.SubElement(style, 'PolyStyle')
        color = ET.SubElement(polystyle, 'color')
        color.text = '7d0000ff'
        colormode = ET.SubElement(polystyle, 'colorMode')
        colormode.text = 'normal'
        
        for feature in feature_collection['features']:
            placemark = ET.SubElement(folder,'Placemark')
            placemark_name = ET.SubElement(placemark, 'name')
            placemark_name.text = feature['properties']['primary_name']
            placemark_description = ET.SubElement(placemark, 'description')
            visibility = ET.SubElement(placemark, 'visibility')
            visibility.text = '1'
            style_url = ET.SubElement(placemark, 'styleUrl')
            style_url.text = '#resource_style'

            extended_data = ET.SubElement(placemark, 'ExtendedData')
            for k, v in feature['properties'].iteritems():
                data = ET.SubElement(extended_data, 'Data', attrib={'name':k})
                value = ET.SubElement(data, 'value')
                value.text = v
            geometry_element = ET.fromstring(feature['geometry'].kml)
            placemark.append(geometry_element)
        kml_output = ET.tostring(root, encoding='UTF-8', method='xml')
        dest = StringIO()
        dest.write(kml_output)
        return [{'name':kml_name, 'outputfile': dest}]

    def write_resources(self, resources, resource_export_configs):
        """Using resource_export_configs from either a resource_export_mappings.json
        or the default mapping (which includes only resource type, primaryname and entityid).
        """
        using_default_mapping = False
        if resource_export_configs == '':
            resource_export_configs = self.default_mapping
            using_default_mapping = True
        for resource in resources:
            if resource['_type'] in resource_export_configs['RESOURCE_TYPES']:
                resource_export_configs['RESOURCE_TYPES'][resource['_type']]['records'].append(resource)
            if using_default_mapping:
                resource_export_configs['RECORDS'].append(resource)

        schema = resource_export_configs['SCHEMA']
        resource_types = resource_export_configs['RESOURCE_TYPES']
        name_prefix = resource_export_configs['NAME']

        features = []

        for resource_type, data in resource_types.iteritems():
            field_map = data['FIELD_MAP']
            for resource in data['records']:
                if len(resource['_source']['geometries']) > 0:
                    template_properties = self.create_template_record(schema, resource, resource_type)
                    complete_properties = self.get_field_map_values(resource, template_properties, field_map)
                    properties = self.concatenate_value_lists(complete_properties)
                    feature = self.process_feature_geoms(properties, resource)
                    features.append(feature)

        if using_default_mapping:
            for resource in resource_export_configs['RECORDS']:
                if len(resource['_source']['geometries']) > 0:
                    properties = self.create_template_record(schema, resource, resource_type=None)
                    feature = self.process_feature_geoms(properties, resource)
                    features.append(feature)

        feature_collection = {'type':'FeatureCollection', 'features': features}
        iso_date = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        kml_name = os.path.join('{0}_{1}.{2}'.format(name_prefix, iso_date, 'kml'))

        return self.create_kml(feature_collection, kml_name)