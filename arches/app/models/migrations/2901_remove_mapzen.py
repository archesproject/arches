# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
from django.db import migrations, models
from django.core import management

class Migration(migrations.Migration):

    dependencies = [
        ('models', '2385_resource_instance_multiselect'),
    ]

    operations = [
        migrations.RunSQL(
        """
            DELETE FROM public.geocoders WHERE geocoderid = '10000000-0000-0000-0000-010000000001';
            DELETE FROM public.map_sources WHERE name = 'mapzen';
            DELETE FROM public.map_layers WHERE name = 'mapzen';
        """,
        """
            INSERT INTO public.geocoders(geocoderid, name, component) VALUES ('10000000-0000-0000-0000-010000000001', 'Mapzen', 'views/components/geocoders/mapzen');
            INSERT INTO map_sources(name, source)
               VALUES ('mapzen', '{
                           "type": "vector",
                           "tiles": ["https://vector.mapzen.com/osm/all/{z}/{x}/{y}.mvt?api_key=vector-tiles-LM25tq4"]
                   }');
            INSERT INTO map_layers(maplayerid, name, layerdefinitions, isoverlay, icon, activated, addtomap)
               VALUES (public.uuid_generate_v1mc(), 'mapzen', '
                 [
                 {
                     "id": "background",
                     "type": "background",
                     "paint": {
                       "background-color": "#ededed"
                     }
                   }, {
                     "id": "water-line",
                     "source": "mapzen",
                     "source-layer": "water",
                     "type": "line",
                     "filter": ["==", "$type", "LineString"],
                     "paint": {
                       "line-color": "#7acad0",
                       "line-width": {
                         "base": 1.2,
                         "stops": [[8, 0.5], [20, 15]]
                       }
                     }
                   }, {
                     "id": "water-polygon",
                     "source": "mapzen",
                     "source-layer": "water",
                     "type": "fill",
                     "filter": ["==", "$type", "Polygon"],
                     "paint": {
                       "fill-color": "#7acad0"
                     }
                   }, {
                     "id": "park",
                     "type": "fill",
                     "source": "mapzen",
                     "source-layer": "landuse",
                     "minzoom": 6,
                     "filter": ["in", "kind", "park", "forest", "garden", "grass", "farm", "meadow", "playground", "golf_course", "nature_reserve", "wetland", "wood", "cemetery"],
                     "paint": {
                       "fill-color": "#c2cd44"
                     }
                   }, {
                     "id": "river",
                     "source": "mapzen",
                     "source-layer": "water",
                     "type": "line",
                     "minzoom": 6,
                     "filter": ["all", ["==", "$type", "LineString"], ["==", "kind", "river"]],
                     "layout": {
                         "line-cap": "round",
                         "line-join": "round"
                       },
                     "paint": {
                       "line-color": "#7acad0",
                       "line-width": {
                         "base": 1.2,
                         "stops": [[8, 0.75], [20, 15]]
                       }
                     }
                   }, {
                     "id": "stream-etc",
                     "source": "mapzen",
                     "source-layer": "water",
                     "type": "line",
                     "minzoom": 11,
                     "filter": ["all", ["==", "$type", "LineString"], ["==", "kind", "stream"]],
                     "layout": {
                         "line-cap": "round",
                         "line-join": "round"
                       },
                     "paint": {
                       "line-color": "#7acad0",
                       "line-width": {
                         "base": 1.4,
                         "stops": [[10, 0.5], [20, 15]]
                       }
                     }
                   }, {
                       "id": "country-boundary",
                       "source": "mapzen",
                       "source-layer": "places",
                       "type": "line",
                       "filter": ["==", "admin_level", "2"],
                       "maxzoom": 4,
                       "layout": {
                         "line-cap": "round",
                         "line-join": "round"
                       },
                       "paint": {
                         "line-color": "#afd3d3",
                       "line-width": {
                         "base": 2,
                         "stops": [[1, 0.5], [7, 3]]
                         }
                       }
                     }, {
                       "id": "state-boundary",
                       "source": "mapzen",
                       "source-layer": "places",
                       "type": "fill",
                       "filter": ["==", "admin_level", "4"],
                       "maxzoom": 10,
                       "paint": {
                         "fill-color": "#ededed",
                         "fill-outline-color": "#cacecc"
                       }
                     }, {
                     "id": "subways",
                     "source": "mapzen",
                     "source-layer": "roads",
                     "type": "line",
                     "paint": {
                       "line-color": "#ef7369",
                       "line-dasharray": [2, 1]
                     },
                     "filter": ["==", "railway", "subway"]
                   }, {
                     "id": "link-tunnel",
                     "source": "mapzen",
                     "source-layer": "roads",
                     "type": "line",
                     "filter": ["any",["==", "is_tunnel", "yes"]],
                     "layout": {
                       "line-join": "round",
                       "line-cap": "round"
                     },
                     "paint": {
                       "line-color": "#afd3d3",
                       "line-width": {
                         "base": 1.55,
                         "stops": [[4, 0.25], [20, 30]]
                       },
                       "line-dasharray": [1, 2]
                     }
                   }, {
                     "id": "buildings",
                     "type": "fill",
                     "source": "mapzen",
                     "source-layer": "buildings",
                     "paint": {
                     "fill-outline-color": "#afd3d3",
                     "fill-color": "#ededed"
                     }
                   }, {
                     "id": "road",
                     "source": "mapzen",
                     "source-layer": "roads",
                     "type": "line",
                     "filter": ["any",["==", "kind", "minor_road"],["==", "kind", "major_road"]],
                     "layout": {
                       "line-join": "round",
                       "line-cap": "round"
                     },
                     "paint": {
                       "line-color": "#c0c4c2",
                       "line-width": {
                         "base": 1.55,
                         "stops": [[4, 0.25], [20, 30]]
                       }
                     }
                   }, {
                     "id": "link-bridge",
                     "source": "mapzen",
                     "source-layer": "roads",
                     "type": "line",
                     "filter": ["any",["==", "is_link", "yes"], ["==", "is_bridge", "yes"]],
                     "layout": {
                       "line-join": "round",
                       "line-cap": "round"
                     },
                     "paint": {
                       "line-color": "#c0c4c2",
                       "line-width": {
                         "base": 1.55,
                         "stops": [[4, 0.5], [8, 1.5], [20, 40]]
                       }
                     }
                   }, {
                     "id": "highway",
                     "source": "mapzen",
                     "source-layer": "roads",
                     "type": "line",
                     "filter": ["==", "kind", "highway"],
                     "layout": {
                       "line-join": "round",
                       "line-cap": "round"
                     },
                     "paint": {
                       "line-color": "#5d6765",
                       "line-width": {
                         "base": 1.55,
                         "stops": [[4, 0.5], [8, 1.5], [20, 40]]
                       }
                     }
                   }, {
                     "id": "path",
                     "source": "mapzen",
                     "source-layer": "roads",
                     "type": "line",
                     "filter": ["==", "kind", "path"],
                     "layout": {
                       "line-join": "round",
                       "line-cap": "round"
                     },
                     "minzoom": 12,
                     "paint": {
                       "line-color": "#5d6765",
                       "line-width": {
                         "base": 1.8,
                         "stops": [[10, 0.15], [20, 15]]
                       },
                       "line-dasharray": [2, 2]
                     }
                   }, {
                     "id": "ocean-label",
                     "source": "mapzen",
                     "source-layer": "places",
                     "type": "symbol",
                     "minzoom": 2,
                     "maxzoom": 6,
                     "filter": ["==", "kind", "ocean"],
                     "layout": {
                         "text-field": "{name}",
                         "text-font": ["Open Sans Italic", "Arial Unicode MS Regular"],
                         "text-max-width": 14,
                         "text-letter-spacing": 0.1
                       },
                     "paint": {
                       "text-color": "#ededed",
                       "text-halo-color": "rgba(0,0,0,0.2)"
                     }
                   }, {
                       "id": "other-label",
                       "source": "mapzen",
                       "source-layer": "places",
                       "filter": ["all", ["==", "$type", "Point"], ["==", "kind", "neighbourhood"]],
                       "minzoom": 12,
                       "type": "symbol",
                       "layout": {
                         "text-field": "{name}",
                         "text-font": ["Open Sans Semibold", "Arial Unicode MS Bold"],
                         "text-max-width": 10
                       },
                       "paint": {
                         "text-color": "#cb4b49",
                         "text-halo-color": "rgba(255,255,255,0.5)"
                       }
                     }, {
                       "id": "city-label",
                       "source": "mapzen",
                       "source-layer": "places",
                       "filter": ["all", ["==", "$type", "Point"], ["==", "kind", "city"]],
                       "minzoom": 10,
                       "maxzoom": 14,
                       "type": "symbol",
                       "layout": {
                         "text-field": "{name}",
                         "text-font": ["Open Sans Semibold", "Arial Unicode MS Bold"],
                         "text-max-width": 10,
                         "text-letter-spacing": 0.1
                       },
                       "paint": {
                         "text-color": "#384646",
                         "text-halo-color": "rgba(255,255,255,0.5)"
                       }
                     }, {
                       "id": "state-label",
                       "source": "mapzen",
                       "source-layer": "places",
                       "filter": ["all", ["==", "$type", "Point"], ["==", "kind", "state"]],
                       "minzoom": 6,
                       "maxzoom": 12,
                       "type": "symbol",
                       "layout": {
                         "text-field": "{name}",
                         "text-font": ["Open Sans Regular", "Arial Unicode MS Regular"],
                         "text-max-width": 8
                       },
                       "paint": {
                         "text-color": "#f27a87",
                         "text-halo-color": "rgba(255,255,255,0.5)"
                       }
                     }, {
                       "id": "country-label",
                       "source": "mapzen",
                       "source-layer": "places",
                       "filter": ["all", ["==", "$type", "Point"], ["==", "kind", "country"]],
                       "maxzoom": 7,
                       "type": "symbol",
                       "layout": {
                         "text-field": "{name}",
                         "text-font": ["Open Sans Semibold", "Arial Unicode MS Bold"],
                         "text-max-width": 4
                       },
                       "paint": {
                         "text-color": "#cb4b49",
                         "text-halo-color": "rgba(255,255,255,0.5)"
                       }
                     }
                   ]

                 ', FALSE, '', TRUE, FALSE);
        """),
    ]
