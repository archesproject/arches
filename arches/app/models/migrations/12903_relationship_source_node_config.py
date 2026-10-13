import re
from django.db import migrations

RESOURCE_INSTANCE_DATATYPES = ("resource-instance", "resource-instance-list")
UUID_PATTERN = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", re.IGNORECASE
)


def _update_published_graphs(apps, graph_transformer):
    PublishedGraph = apps.get_model("models", "PublishedGraph")
    batch_size = 25
    graphs_to_update = []

    queryset = PublishedGraph.objects.exclude(serialized_graph__isnull=True)
    for published_graph in queryset.iterator(chunk_size=batch_size):
        if graph_transformer(published_graph.serialized_graph):
            graphs_to_update.append(published_graph)
            if len(graphs_to_update) == batch_size:
                PublishedGraph.objects.bulk_update(
                    graphs_to_update, ["serialized_graph"]
                )
                graphs_to_update = []

    if graphs_to_update:
        PublishedGraph.objects.bulk_update(graphs_to_update, ["serialized_graph"])


def _resource_instance_graph_configs(serialized_graph):
    for node in serialized_graph.get("nodes") or []:
        if node.get("datatype") not in RESOURCE_INSTANCE_DATATYPES:
            continue
        graphs = (node.get("config") or {}).get("graphs")
        if isinstance(graphs, list):
            for graph_config in graphs:
                if isinstance(graph_config, dict):
                    yield graph_config


def convert_published_graph_configs(serialized_graph):
    changed = False
    for graph_config in _resource_instance_graph_configs(serialized_graph):
        if "relationshipSource" in graph_config:
            continue

        use_ontology = graph_config.get("useOntologyRelationship") is True
        ontology_property = graph_config.pop("ontologyProperty", None)
        inverse_ontology_property = graph_config.pop("inverseOntologyProperty", None)
        relationship_concept = graph_config.pop("relationshipConcept", None)
        inverse_relationship_concept = graph_config.pop(
            "inverseRelationshipConcept", None
        )
        graph_config.pop("useOntologyRelationship", None)

        if use_ontology:
            relationship_source = "ontology"
            relationship = ontology_property
            inverse_relationship = inverse_ontology_property
        else:
            relationship = relationship_concept
            inverse_relationship = inverse_relationship_concept
            value = relationship_concept or inverse_relationship_concept
            relationship_source = (
                "concept" if not value or UUID_PATTERN.match(value) else "reference"
            )

        graph_config["relationshipSource"] = relationship_source
        graph_config["relationship"] = relationship
        graph_config["inverseRelationship"] = inverse_relationship
        changed = True
    return changed


def revert_published_graph_configs(serialized_graph):
    changed = False
    for graph_config in _resource_instance_graph_configs(serialized_graph):
        if "relationshipSource" not in graph_config:
            continue

        use_ontology = graph_config.pop("relationshipSource") == "ontology"
        relationship = graph_config.pop("relationship", None)
        inverse_relationship = graph_config.pop("inverseRelationship", None)

        graph_config["useOntologyRelationship"] = use_ontology
        graph_config["ontologyProperty"] = relationship if use_ontology else None
        graph_config["inverseOntologyProperty"] = (
            inverse_relationship if use_ontology else None
        )
        graph_config["relationshipConcept"] = None if use_ontology else relationship
        graph_config["inverseRelationshipConcept"] = (
            None if use_ontology else inverse_relationship
        )
        changed = True
    return changed


# Renames the relationship keys on each entry of every resource-instance value in
# a tile. Each tile is rewritten once, however many resource-instance nodes its
# nodegroup has, rather than once per node.
def rename_tile_data_keys(old_key, new_key, old_inverse_key, new_inverse_key):
    return f"""
        WITH ri_nodes AS (
            SELECT nodegroupid, array_agg(nodeid::text) AS nodeids
            FROM nodes
            WHERE datatype IN ('resource-instance', 'resource-instance-list')
            GROUP BY nodegroupid
        )
        UPDATE tiles t SET tiledata = (
            SELECT jsonb_object_agg(
                tile_value.key,
                CASE WHEN tile_value.key = ANY(ri.nodeids)
                    AND jsonb_typeof(tile_value.value) = 'array'
                THEN (
                    SELECT COALESCE(jsonb_agg(
                        CASE WHEN jsonb_typeof(element) = 'object' THEN
                            (element - '{old_key}' - '{old_inverse_key}')
                            || CASE WHEN element ? '{old_key}'
                                THEN jsonb_build_object('{new_key}', element->'{old_key}')
                                ELSE '{{}}'::jsonb END
                            || CASE WHEN element ? '{old_inverse_key}'
                                THEN jsonb_build_object('{new_inverse_key}', element->'{old_inverse_key}')
                                ELSE '{{}}'::jsonb END
                        ELSE element END
                        ORDER BY ordinality
                    ), '[]'::jsonb)
                    FROM jsonb_array_elements(tile_value.value)
                        WITH ORDINALITY AS elements(element, ordinality)
                )
                ELSE tile_value.value END
            )
            FROM jsonb_each(t.tiledata) tile_value
        )
        FROM ri_nodes ri
        WHERE t.nodegroupid = ri.nodegroupid
        AND EXISTS (
            SELECT 1
            FROM unnest(ri.nodeids) nodeid,
                jsonb_array_elements(
                    CASE WHEN jsonb_typeof(t.tiledata->nodeid) = 'array'
                        THEN t.tiledata->nodeid ELSE '[]'::jsonb END
                ) element
            WHERE jsonb_typeof(element) = 'object'
            AND (element ? '{old_key}' OR element ? '{old_inverse_key}')
        );
    """


class Migration(migrations.Migration):
    dependencies = [
        ("models", "13001_spatialview_dbroles"),
    ]

    # Collapse the four relationship keys on each entry of a resource-instance node's
    # config.graphs into a single discriminator plus one pair of values, so that a
    # relationship type can also be drawn from a controlled list:
    #   useOntologyRelationship  -> relationshipSource ('ontology'|'concept'|'reference')
    #     (when not using the ontology, the relationship is a 'concept' if its value is a
    #     UUID (RDM value id), and a 'reference' if it is anything else, i.e. a URI from a
    #     controlled list)
    #   ontologyProperty         -> relationship
    #   inverseOntologyProperty  -> inverseRelationship
    #   relationshipConcept      -> relationship
    #   inverseRelationshipConcept -> inverseRelationship
    update_node_configs = """
        UPDATE nodes SET config = jsonb_set(config, '{graphs}', (
            SELECT jsonb_agg(
                (element
                    - 'useOntologyRelationship'
                    - 'ontologyProperty'
                    - 'inverseOntologyProperty'
                    - 'relationshipConcept'
                    - 'inverseRelationshipConcept'
                ) || jsonb_build_object(
                    'relationshipSource',
                    CASE
                        WHEN element->>'useOntologyRelationship' = 'true' THEN 'ontology'
                        WHEN COALESCE(
                            NULLIF(element->>'relationshipConcept', ''),
                            NULLIF(element->>'inverseRelationshipConcept', '')
                        ) ~* '^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
                        OR COALESCE(
                            NULLIF(element->>'relationshipConcept', ''),
                            NULLIF(element->>'inverseRelationshipConcept', '')
                        ) IS NULL THEN 'concept'
                        ELSE 'reference'
                    END,
                    'relationship',
                    CASE WHEN element->>'useOntologyRelationship' = 'true'
                        THEN element->'ontologyProperty' ELSE element->'relationshipConcept' END,
                    'inverseRelationship',
                    CASE WHEN element->>'useOntologyRelationship' = 'true'
                        THEN element->'inverseOntologyProperty' ELSE element->'inverseRelationshipConcept' END
                )
            )
            FROM jsonb_array_elements(config -> 'graphs') element
        ))
        WHERE datatype IN ('resource-instance', 'resource-instance-list')
        AND jsonb_typeof(config -> 'graphs') = 'array'
        AND jsonb_array_length(config -> 'graphs') > 0
        AND EXISTS (
            SELECT * FROM jsonb_array_elements(config -> 'graphs')
            WHERE value->'relationshipSource' IS NULL
        );
    """

    # Lossy: the unused side of each pair was discarded going forward. 'concept' and
    # 'reference' both restore to useOntologyRelationship false, with the relationship
    # (a UUID or a URI respectively) kept in relationshipConcept.
    reverse_node_configs = """
        UPDATE nodes SET config = jsonb_set(config, '{graphs}', (
            SELECT jsonb_agg(
                (element
                    - 'relationshipSource'
                    - 'relationship'
                    - 'inverseRelationship'
                ) || jsonb_build_object(
                    'useOntologyRelationship',
                    element->>'relationshipSource' = 'ontology',
                    'ontologyProperty',
                    CASE WHEN element->>'relationshipSource' = 'ontology'
                        THEN element->'relationship' ELSE 'null'::jsonb END,
                    'inverseOntologyProperty',
                    CASE WHEN element->>'relationshipSource' = 'ontology'
                        THEN element->'inverseRelationship' ELSE 'null'::jsonb END,
                    'relationshipConcept',
                    CASE WHEN element->>'relationshipSource' = 'ontology'
                        THEN 'null'::jsonb ELSE element->'relationship' END,
                    'inverseRelationshipConcept',
                    CASE WHEN element->>'relationshipSource' = 'ontology'
                        THEN 'null'::jsonb ELSE element->'inverseRelationship' END
                )
            )
            FROM jsonb_array_elements(config -> 'graphs') element
        ))
        WHERE datatype IN ('resource-instance', 'resource-instance-list')
        AND jsonb_typeof(config -> 'graphs') = 'array'
        AND jsonb_array_length(config -> 'graphs') > 0
        AND EXISTS (
            SELECT * FROM jsonb_array_elements(config -> 'graphs')
            WHERE value->'relationshipSource' IS NOT NULL
        );
    """

    update_relationship_function = """
        CREATE OR REPLACE FUNCTION public.__arches_create_resource_x_resource_relationships(IN tile_id uuid)
        RETURNS boolean
        LANGUAGE 'plpgsql'
        VOLATILE
        PARALLEL UNSAFE
        COST 100

        AS $BODY$
        DECLARE
            resourceinstancefrom_id uuid;
            from_graphid uuid;
            relational_count text;
            val boolean = true;
        BEGIN
            select count(*) into relational_count from tiles where tiledata::text like '%resourceX%' and tileid = tile_id;

            IF relational_count = '0'
                THEN
                RETURN false;
            END IF;

            --https://dbfiddle.uk/?rdbms=postgres_12&fiddle=21e25754f355a492dfd7b4a134182d2e

            SELECT resourceinstanceid INTO resourceinstancefrom_id FROM tiles WHERE tileid = tile_id;
            SELECT graphid INTO from_graphid FROM resource_instances WHERE resourceinstanceid = resourceinstancefrom_id;

            DELETE FROM resource_x_resource WHERE tileid = tile_id;

            WITH updated_tiles as (
                select * from tiles t
                WHERE
                    t.tileid = tile_id
            )
            , relationships AS (
                SELECT n.nodeid, n.config,
                    jsonb_array_elements(tt.tiledata->n.nodeid::text) AS relationship
                FROM updated_tiles tt
                    LEFT JOIN nodes n ON tt.nodegroupid = n.nodegroupid
                WHERE n.datatype IN ('resource-instance-list', 'resource-instance')
                    AND tt.tiledata->>n.nodeid::text IS NOT null
            )
            , relationships2 AS (
                SELECT r.nodeid, r.config, r.relationship, (SELECT ri.graphid
                    FROM resource_instances ri
                    WHERE (r.relationship->>'resourceId')::uuid = ri.resourceinstanceid) AS to_graphid
                FROM relationships r
            )
            , relationships3 AS (
                SELECT fr.nodeid, fr.relationship, fr.to_graphid,
                (
                    SELECT graphs->>'relationship'
                    FROM jsonb_array_elements(fr.config->'graphs') AS graphs
                    WHERE graphs->>'graphid' = fr.to_graphid::text
                ) AS defaultOntologyProperty,
                (
                    SELECT graphs->>'inverseRelationship'
                    FROM jsonb_array_elements(fr.config->'graphs') AS graphs
                    WHERE graphs->>'graphid' = fr.to_graphid::text
                ) AS defaultInverseOntologyProperty
                FROM relationships2 fr
            )

            INSERT INTO resource_x_resource (
                resourcexid,
                notes,
                relationshiptype,
                inverserelationshiptype,
                resourceinstanceidfrom,
                resourceinstanceidto,
                resourceinstancefrom_graphid,
                resourceinstanceto_graphid,
                tileid,
                nodeid,
                created,
                modified
            ) (SELECT
                CASE relationship->>'resourceXresourceId'
                    WHEN '' THEN uuid_generate_v4()
                    ELSE (relationship->>'resourceXresourceId')::uuid
                END,
                '',
                CASE COALESCE(relationship->>'relationship', relationship->>'ontologyProperty')
                    WHEN '' THEN defaultOntologyProperty
                    ELSE COALESCE(relationship->>'relationship', relationship->>'ontologyProperty')
                END,
                CASE COALESCE(relationship->>'inverseRelationship', relationship->>'inverseOntologyProperty')
                    WHEN '' THEN defaultInverseOntologyProperty
                    ELSE COALESCE(relationship->>'inverseRelationship', relationship->>'inverseOntologyProperty')
                END,
                resourceinstancefrom_id,
                (relationship->>'resourceId')::uuid,
                from_graphid,
                to_graphid,
                tile_id,
                nodeid,
                now(),
                now()
            FROM relationships3);
            RETURN val;
        END;
        $BODY$;
    """

    reverse_relationship_function = """
        CREATE OR REPLACE FUNCTION public.__arches_create_resource_x_resource_relationships(IN tile_id uuid)
        RETURNS boolean
        LANGUAGE 'plpgsql'
        VOLATILE
        PARALLEL UNSAFE
        COST 100

        AS $BODY$
        DECLARE
            resourceinstancefrom_id uuid;
            from_graphid uuid;
            relational_count text;
            val boolean = true;
        BEGIN
            select count(*) into relational_count from tiles where tiledata::text like '%resourceX%' and tileid = tile_id;

            IF relational_count = '0'
                THEN
                RETURN false;
            END IF;

            --https://dbfiddle.uk/?rdbms=postgres_12&fiddle=21e25754f355a492dfd7b4a134182d2e

            SELECT resourceinstanceid INTO resourceinstancefrom_id FROM tiles WHERE tileid = tile_id;
            SELECT graphid INTO from_graphid FROM resource_instances WHERE resourceinstanceid = resourceinstancefrom_id;

            DELETE FROM resource_x_resource WHERE tileid = tile_id;

            WITH updated_tiles as (
                select * from tiles t
                WHERE
                    t.tileid = tile_id
            )
            , relationships AS (
                SELECT n.nodeid, n.config,
                    jsonb_array_elements(tt.tiledata->n.nodeid::text) AS relationship
                FROM updated_tiles tt
                    LEFT JOIN nodes n ON tt.nodegroupid = n.nodegroupid
                WHERE n.datatype IN ('resource-instance-list', 'resource-instance')
                    AND tt.tiledata->>n.nodeid::text IS NOT null
            )
            , relationships2 AS (
                SELECT r.nodeid, r.config, r.relationship, (SELECT ri.graphid
                    FROM resource_instances ri
                    WHERE (r.relationship->>'resourceId')::uuid = ri.resourceinstanceid) AS to_graphid
                FROM relationships r
            )
            , relationships3 AS (
                SELECT fr.nodeid, fr.relationship, fr.to_graphid,
                (
                    SELECT graphs->>'ontologyProperty'
                    FROM jsonb_array_elements(fr.config->'graphs') AS graphs
                    WHERE graphs->>'graphid' = fr.to_graphid::text
                ) AS defaultOntologyProperty,
                (
                    SELECT graphs->>'inverseOntologyProperty'
                    FROM jsonb_array_elements(fr.config->'graphs') AS graphs
                    WHERE graphs->>'graphid' = fr.to_graphid::text
                ) AS defaultInverseOntologyProperty
                FROM relationships2 fr
            )

            INSERT INTO resource_x_resource (
                resourcexid,
                notes,
                relationshiptype,
                inverserelationshiptype,
                resourceinstanceidfrom,
                resourceinstanceidto,
                resourceinstancefrom_graphid,
                resourceinstanceto_graphid,
                tileid,
                nodeid,
                created,
                modified
            ) (SELECT
                CASE relationship->>'resourceXresourceId'
                    WHEN '' THEN uuid_generate_v4()
                    ELSE (relationship->>'resourceXresourceId')::uuid
                END,
                '',
                CASE relationship->>'ontologyProperty'
                    WHEN '' THEN defaultOntologyProperty
                    ELSE relationship->>'ontologyProperty'
                END,
                CASE relationship->>'inverseOntologyProperty'
                    WHEN '' THEN defaultInverseOntologyProperty
                    ELSE relationship->>'inverseOntologyProperty'
                END,
                resourceinstancefrom_id,
                (relationship->>'resourceId')::uuid,
                from_graphid,
                to_graphid,
                tile_id,
                nodeid,
                now(),
                now()
            FROM relationships3);
            RETURN val;
        END;
        $BODY$;
    """

    update_tile_data = rename_tile_data_keys(
        "ontologyProperty",
        "relationship",
        "inverseOntologyProperty",
        "inverseRelationship",
    )

    reverse_tile_data = rename_tile_data_keys(
        "relationship",
        "ontologyProperty",
        "inverseRelationship",
        "inverseOntologyProperty",
    )

    update_refresh_function = """
        CREATE OR REPLACE FUNCTION public.__arches_refresh_tile_resource_relationships(tile_id uuid)
        RETURNS boolean
        LANGUAGE plpgsql
        AS $function$
        DECLARE
            resource_id uuid;
        BEGIN
            SELECT resourceinstanceid INTO resource_id FROM tiles WHERE tileid = tile_id;

            DELETE FROM resource_x_resource WHERE tileid = tile_id;

            WITH relationships AS (
                SELECT n.nodeid,
                    jsonb_array_elements(t.tiledata->n.nodeid::text) AS relationship
                FROM tiles t
                    LEFT JOIN nodes n ON t.nodegroupid = n.nodegroupid
                WHERE n.datatype IN ('resource-instance-list', 'resource-instance')
                    AND t.tileid = tile_id
                    AND t.tiledata->>n.nodeid::text IS NOT null
            )
            INSERT INTO resource_x_resource (
                resourcexid,
                notes,
                relationshiptype,
                resourceinstanceidfrom,
                resourceinstanceidto,
                inverserelationshiptype,
                tileid,
                nodeid,
                created,
                modified,
                resourceinstancefrom_graphid,
                resourceinstanceto_graphid
            ) SELECT
                CASE relationship->>'resourceXresourceId'
                    WHEN '' THEN uuid_generate_v4()
                    ELSE (relationship->>'resourceXresourceId')::uuid
                END,
                '',
                COALESCE(relationship->>'relationship', relationship->>'ontologyProperty'),
                resource_id,
                (relationship->>'resourceId')::uuid,
                COALESCE(relationship->>'inverseRelationship', relationship->>'inverseOntologyProperty'),
                tile_id,
                nodeid,
                now(),
                now(),
                resourcefrom.graphid,
                resourceto.graphid
            FROM relationships r
                LEFT JOIN resource_instances resourcefrom ON resourcefrom.resourceinstanceid = resource_id
                LEFT JOIN resource_instances resourceto ON resourceto.resourceinstanceid = (r.relationship ->> 'resourceId')::uuid;
            RETURN true;
        END;
        $function$
    """

    reverse_refresh_function = """
        CREATE OR REPLACE FUNCTION public.__arches_refresh_tile_resource_relationships(tile_id uuid)
        RETURNS boolean
        LANGUAGE plpgsql
        AS $function$
        DECLARE
            resource_id uuid;
        BEGIN
            SELECT resourceinstanceid INTO resource_id FROM tiles WHERE tileid = tile_id;

            DELETE FROM resource_x_resource WHERE tileid = tile_id;

            WITH relationships AS (
                SELECT n.nodeid,
                    jsonb_array_elements(t.tiledata->n.nodeid::text) AS relationship
                FROM tiles t
                    LEFT JOIN nodes n ON t.nodegroupid = n.nodegroupid
                WHERE n.datatype IN ('resource-instance-list', 'resource-instance')
                    AND t.tileid = tile_id
                    AND t.tiledata->>n.nodeid::text IS NOT null
            )
            INSERT INTO resource_x_resource (
                resourcexid,
                notes,
                relationshiptype,
                resourceinstanceidfrom,
                resourceinstanceidto,
                inverserelationshiptype,
                tileid,
                nodeid,
                created,
                modified,
                resourceinstancefrom_graphid,
                resourceinstanceto_graphid
            ) SELECT
                CASE relationship->>'resourceXresourceId'
                    WHEN '' THEN uuid_generate_v4()
                    ELSE (relationship->>'resourceXresourceId')::uuid
                END,
                '',
                relationship->>'ontologyProperty',
                resource_id,
                (relationship->>'resourceId')::uuid,
                relationship->>'inverseOntologyProperty',
                tile_id,
                nodeid,
                now(),
                now(),
                resourcefrom.graphid,
                resourceto.graphid
            FROM relationships r
                LEFT JOIN resource_instances resourcefrom ON resourcefrom.resourceinstanceid = resource_id
                LEFT JOIN resource_instances resourceto ON resourceto.resourceinstanceid = (r.relationship ->> 'resourceId')::uuid;
            RETURN true;
        END;
        $function$
    """

    def update_published_graphs(apps, schema_editor):
        _update_published_graphs(apps, convert_published_graph_configs)

    def reverse_published_graphs(apps, schema_editor):
        _update_published_graphs(apps, revert_published_graph_configs)

    operations = [
        migrations.RunSQL(update_node_configs, reverse_node_configs),
        migrations.RunPython(update_published_graphs, reverse_published_graphs),
        migrations.RunSQL(update_tile_data, reverse_tile_data),
        migrations.RunSQL(update_relationship_function, reverse_relationship_function),
        migrations.RunSQL(update_refresh_function, reverse_refresh_function),
    ]
