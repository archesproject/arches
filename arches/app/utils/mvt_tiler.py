from arches.app.models import models
from arches.app.models.system_settings import settings
from arches.app.search.search_engine_factory import SearchEngineFactory
from django.core.cache import cache
from django.db import connection

from arches.app.utils.permission_backend import (
    get_filtered_instances,
)


class MVTTiler:
    se = SearchEngineFactory().create()
    EARTHCIRCUM = 40075016.6856
    PIXELSPERTILE = 256

    def __init__(self):
        pass

    def createTile(
        self,
        nodeid: str,
        viewable_nodegroups: list[str],
        user: any,
        zoom: int,
        x: int,
        y: int,
    ) -> bytes | None:
        try:
            node = models.Node.objects.get(
                nodeid=nodeid, nodegroup_id__in=viewable_nodegroups
            )
        except models.Node.DoesNotExist:
            return None
        search_geom_count = 0
        config = node.config
        cache_key = self.create_mvt_cache_key(node, zoom, x, y, user)
        tile = cache.get(cache_key)
        if tile is None:
            with connection.cursor() as cursor:
                resource_query = """
                    SELECT resourceinstanceid::text
                    FROM geojson_geometries
                    WHERE 
                    ST_Intersects(geom, TileBBox(%s, %s, %s, 3857))
                    AND
                    nodeid = %s
                    """

                # get all of the resources in this bbox
                cursor.execute(resource_query, [zoom, x, y, nodeid])
                resources = [record[0] for record in cursor.fetchall()]

                exclusive_set, resource_ids = get_filtered_instances(
                    user, search_engine=self.se, resources=resources
                )
                permission_framework_filter = (
                    "resourceinstanceid in %s"
                    if exclusive_set
                    else "resourceinstanceid not in %s"
                )
                if len(resource_ids) == 0:
                    resource_ids.append(
                        "10000000-0000-0000-0000-000000000001"
                    )  # This must have a uuid that will never be a resource id.
                resource_ids = tuple(resource_ids)

                if int(zoom) <= int(config["clusterMaxZoom"]):
                    arc = self.EARTHCIRCUM / ((1 << int(zoom)) * self.PIXELSPERTILE)
                    distance = arc * float(config["clusterDistance"])
                    min_points = int(config["clusterMinPoints"])
                    distance = (
                        settings.CLUSTER_DISTANCE_MAX
                        if distance > settings.CLUSTER_DISTANCE_MAX
                        else distance
                    )

                    count_query = """
                    SELECT count(*) FROM geojson_geometries
                    WHERE
                    ST_Intersects(geom, TileBBox(%s, %s, %s, 3857))
                    AND
                    nodeid = %s and {filter}
                    """.format(
                        filter=permission_framework_filter
                    )

                    # get the count of matching geometries
                    cursor.execute(
                        count_query,
                        [
                            zoom,
                            x,
                            y,
                            nodeid,
                            resource_ids,
                        ],
                    )
                    search_geom_count = cursor.fetchone()[0]

                    if search_geom_count >= min_points:
                        cursor.execute(
                            """WITH clusters(tileid, resourceinstanceid, nodeid, geom, cid)
                            AS (
                                SELECT m.*,
                                ST_ClusterDBSCAN(geom, eps := %s, minpoints := %s) over () AS cid
                                FROM (
                                    SELECT tileid,
                                        resourceinstanceid,
                                        nodeid,
                                        geom
                                    FROM geojson_geometries
                                    WHERE 
                                    ST_Intersects(geom, TileBBox(%s, %s, %s, 3857))
                                    AND
                                    nodeid = %s and {filter}
                                ) m
                            )
                            SELECT ST_AsMVT(
                                tile,
                                %s,
                                4096,
                                'geom',
                                'id'
                            ) FROM (
                                SELECT resourceinstanceid::text,
                                    row_number() over () as id,
                                    1 as total,
                                    ST_AsMVTGeom(
                                        geom,
                                        TileBBox(%s, %s, %s, 3857)
                                    ) AS geom,
                                    '' AS extent
                                FROM clusters
                                WHERE cid is NULL
                                UNION
                                SELECT NULL as resourceinstanceid,
                                    row_number() over () as id,
                                    count(*) as total,
                                    ST_AsMVTGeom(
                                        ST_Centroid(
                                            ST_Collect(geom)
                                        ),
                                        TileBBox(%s, %s, %s, 3857)
                                    ) AS geom,
                                    ST_AsGeoJSON(
                                        ST_Extent(geom)
                                    ) AS extent
                                FROM clusters
                                WHERE cid IS NOT NULL
                                GROUP BY cid
                            ) as tile;""".format(
                                filter=permission_framework_filter
                            ),
                            [
                                distance,
                                min_points,
                                zoom,
                                x,
                                y,
                                nodeid,
                                resource_ids,
                                nodeid,
                                zoom,
                                x,
                                y,
                                zoom,
                                x,
                                y,
                            ],
                        )
                    elif search_geom_count:
                        cursor.execute(
                            """SELECT ST_AsMVT(tile, %s, 4096, 'geom', 'id') FROM (SELECT tileid,
                                id,
                                resourceinstanceid,
                                nodeid,
                                featureid::text AS featureid,
                                ST_AsMVTGeom(
                                    geom,
                                    TileBBox(%s, %s, %s, 3857)
                                ) AS geom,
                                1 AS total
                            FROM geojson_geometries
                            WHERE nodeid = %s and {filter} and (geom && ST_TileEnvelope(%s, %s, %s))) AS tile;""".format(
                                filter=permission_framework_filter
                            ),
                            [nodeid, zoom, x, y, nodeid, resource_ids, zoom, x, y],
                        )
                    else:
                        tile = ""
                else:
                    query = """SELECT ST_AsMVT(tile, %s, 4096, 'geom', 'id') FROM (SELECT tileid,
                            id,
                            resourceinstanceid,
                            nodeid,
                            featureid::text AS featureid,
                            ST_AsMVTGeom(
                                geom,
                                TileBBox(%s, %s, %s, 3857)
                            ) AS geom,
                            1 AS total
                        FROM geojson_geometries
                        WHERE nodeid = %s and {filter} and (geom && ST_TileEnvelope(%s, %s, %s))) AS tile;""".format(
                        filter=permission_framework_filter
                    )
                    cursor.execute(
                        """SELECT ST_AsMVT(tile, %s, 4096, 'geom', 'id') FROM (SELECT tileid,
                            id,
                            resourceinstanceid,
                            nodeid,
                            featureid::text AS featureid,
                            ST_AsMVTGeom(
                                geom,
                                TileBBox(%s, %s, %s, 3857)
                            ) AS geom,
                            1 AS total
                        FROM geojson_geometries
                        WHERE nodeid = %s and {filter} and (geom && ST_TileEnvelope(%s, %s, %s))) AS tile;""".format(
                            filter=permission_framework_filter
                        ),
                        [nodeid, zoom, x, y, nodeid, resource_ids, zoom, x, y],
                    )
                tile = bytes(cursor.fetchone()[0]) if tile is None else tile
                cache.set(cache_key, tile, settings.TILE_CACHE_TIMEOUT)
        return tile

    def create_mvt_cache_key(self, node, zoom, x, y, user):
        return f"mvt_{str(node.nodeid)}_{zoom}_{x}_{y}_{user.id}"
