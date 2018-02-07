import uuid
from django.core.exceptions import ValidationError
from arches.app.functions.base import BaseFunction
from arches.app.models import models
from arches.app.models.tile import Tile
from arches.app.models.system_settings import settings
import json
import psycopg2

details = {
    'name': 'Spatial Join',
    'type': 'node',
    'description': 'perform attribute transfer based on comparison to local PostGIS table',
    # 'defaultconfig': {"spatial_node_id":"","table_field_one":"","target_node_id_one":"","table_field_two":"","target_node_id_two":""},
    'defaultconfig': {"spatial_node_id":"", "inputs":[{"table_field":"","target_node_id":""}] },

    'classname': 'SpatialJoin',
    'component': 'views/components/functions/spatial-join'
}

def attribute_from_postgis(table,field,geojson):
    """uses the settings credentials to connect to the local postgis db and
    then makes an intersection query on the specified table using the input
    geojson object, and returns the values of the specified field for any
    feature that the intersection query returns."""

    ## add crs property which is required by postgis (without this, you will
    ## get an error about mixed coordinate systems, even if they are not mixed.
    geojson['crs'] = {"type":"name","properties":{"name":"EPSG:4326"}}

    ## transform to string
    geojson_str = json.dumps(geojson)

    ## make connection to postgis database
    db = settings.DATABASES['default']
    db_conn = "dbname = {} user = {} host = {} password = {}".format(
        db['NAME'],db['USER'],db['HOST'],db['PASSWORD'])
    conn = psycopg2.connect(db_conn)
    cur = conn.cursor()

    ## create and execute SQL statement for intersection
    sql = '''
    SELECT {0} FROM {1}
        WHERE
        ST_Intersects(
          ST_GeomFromGeoJSON('{2}'),
          {1}.geom
        );
    '''.format(field,table,geojson_str)
    cur.execute(sql)
    rows = cur.fetchall()

    ## transform all matches to a simple list of strings
    result = [i[0] for i in rows]

    ## remove crs property because for some reason it gets added to
    ## the actual tile data and then it breaks mapbox :(
    del geojson['crs']

    return result

def get_valueid_from_preflabel(preflabel):
    """this function will get the valueid for a concept's preflabel.
    you need only enter the preflabel, not the concept itself. the logic
    is naive, and will return none if there are more than one match for
    this prefLabel."""
    vs = models.Value.objects.filter(value=preflabel)


    if len(vs) == 0:
        print "no match for this preflabel:",preflabel
        return None
    if len(vs) > 1:
        concept_ids = [i.concept_id for i in vs]
        if len(set(concept_ids)) > 1:
            print "too many values for this preflabel:", preflabel
            return None

    return str(vs[0].valueid)

class SpatialJoin(BaseFunction):

    def save(self,tile,request):

        ## return early if there is no spatial data to use for a comparison
        spatial_node_id = self.config['spatial_node_id']
        if tile.data[spatial_node_id] == None:
            ## apparently if there is nothing in the triggering nodegroup,
            ## an error will occur AFTER this function has returned. So,
            ## for now, setting the value to an empty list to handle this.
            tile.data[spatial_node_id] = []
            return

        ## get geoms from the current tile
        geoms = [feature['geometry'] for feature in tile.data[spatial_node_id]['features']]

        ## create and iterate list of input table/field/target sets
        ## the UI should produce "table_name.field_name" strings

        table_field_targets = self.config['inputs']

        for table_field_target in table_field_targets:

            ## skip if the table_name.field_name input is not valid
            if not "." in table_field_target['table_field']:
                continue

            ## parse input sets
            table,field = table_field_target['table_field'].split(".")[0],table_field_target['table_field'].split(".")[1]
            target_node_id = table_field_target['target_node_id']
            target_ng_id = models.Node.objects.filter(nodeid=target_node_id)[0].nodegroup_id

            # process each geom and create a list of all values
            vals = []
            for geom in geoms:
                val = attribute_from_postgis(table,field,geom)
                vals+=val
            attributes = list(set(vals))

            ## get the datatype of the target node, and if necessary convert the
            ## attributes to value ids. note that prefLabels are expected here,
            ## NOT actual concept ids. what actually gets passed to the tile data
            ## are valueids for the preflabels, not UUIDs for the concept.
            node = models.Node.objects.get(pk=target_node_id)
            target_node_datatype = node.datatype
            if target_node_datatype in ["concept","concept-list"]:
                print "converting values to valueids"
                vals = [get_valueid_from_preflabel(v) for v in attributes]
                attributes = [v for v in vals if v]

            ## if the target node is inside of the currently edited node group,
            ## just set the new value right here
            if str(target_ng_id) == str(tile.nodegroup_id):
                print "  modifying the tile in place"

                ## set precedent for correlating new values with target node
                ## datatype. the following will work on a limited basis
                if target_node_datatype == "concept-list":
                    tile.data[target_node_id] = attributes
                elif target_node_datatype == "concept":
                    tile.data[target_node_id] = attributes[0]
                else:
                    tile.data[target_node_id] = attributes[0]

                tile.dirty = False
                return

            ## here is a start on changing a value in a tile in a different nodegroup
            ## it works, however, there must already be a tile to overwrite, this
            ## code won't create a new tile at the moment.
            previously_saved_tiles = Tile.objects.filter(nodegroup_id=target_ng_id)
            match = False
            for t in previously_saved_tiles:
                print " ",t.resourceinstance_id
                if str(t.resourceinstance_id) == str(tile.resourceinstance_id):
                    match = True
                    if target_node_datatype == "concept-list":
                        t.data[target_node_id] = attributes
                    elif target_node_datatype == "concept":
                        t.data[target_node_id] = attributes[0]
                    else:
                        t.data[target_node_id] = attributes[0]
                    t.save()

        return

    def on_import(self):
        print 'calling on import'

    def get(self):
        print 'calling get'

    def delete(self):
        print 'calling delete'
