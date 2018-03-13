# Data migration procedures for EAMENA
A number of commands have been implemented which together allow an existing arches database to migrate to an updated schema. Business data can be moved from nodes in the old schema to the new, and old data can be cleaned up.

The migration is done in multiple stages:
- extend_ontology
- migrate_resources
- prune oldresources and ontology

### Export to csv and add path to settings
The processes are configured via a collection of csv files. For convenience, these can be edited in an excel spreadsheet and exported to csv.

Before executing either of these stages, the spreadsheet sheets should first be exported to csv files named ```<RESOURCE_TYPE>_<sheet_name>.csv```
E.g. ```HERITAGE_RESOURCE_GROUP.E27_added_nodes.csv```

These should all be in a common directory, and an entry for ADDITIONAL_RESOURCE_GRAPH_LOCATIONS should be added to settings.py to point at any such directories as a tuple of paths. E.g.
```
ADDITIONAL_RESOURCE_GRAPH_LOCATIONS = (
     os.path.join(PACKAGE_ROOT, 'additional_resource_graphs'),
)
```

### 1 Add new properties
If the new ontology structure requires any new property types, these must be added to the database.
The extend_ontology command  described below will execute the sql file found at: arches/management/commands/package_utils/added_classes.sql, so this file should be updated to add any property types not defined in the standard set of PX relationships.

### 2 Extend ontology
The ontology is extended by inserting additional nodes and relationships to the resource graph, in much the same way as graphs are imported in the first instance. The code implementing the extension is based on the resource graph import code.

As per the main import process, ontology data is in 2 files: 
- [RESOURCE_TYPE]_added_edges.csv
- [RESOURCE_TYPE]_added_nodes.csv

These each have the same syntax as used in the main arches ontology import process

A further file determine changes to the properties linking nodes: 
- [RESOURCE_TYPE]_altered_edges.csv

Finally, one more file allows Reference data to be moved from the old entitytypes to the new ones. This file is also used in the next step to migrate business data
- [RESOURCE_TYPE]_altered_nodes.csv

With the files in place and pointed at the settings, the ontology is extended with the command:
```
python manage.py packages -o extend_ontology
```

#### Hooking onto existing nodes
nodes declared in the added_nodes.csv file will be taken to represent the nodes in the existing graph if they share the same name. There will typically be at least the root HERITAGE_RESOURCE_ROOT.E27 represented in the schema.

#### Adding brand new resource types
For importing schemas for new resource types, e.g. E24/E25, the existing arches workflow should be used. There is a shortcut to loading graphs post-installation which may be accessed via the following command (loading graphs in the path specified in settings.py for RESOURCE_GRAPH_LOCATIONS):
```
python manage.py packages -o load_graphs
```
#### Reference Data and drop downs
After this process, the new fields point at the correct reference data (according to the altered_nodes file).
N.B. the RDM will still show the old value as the title of the dropdown set, since the reference data is shared by both the old and new entitytypes. After pruning the ontology, this will appear correctly.

# 3 Migrate Business Data
At this point the ontology consists of the old schema, with new entity types and rules added. Some edge property types on the old schema have been altered.
All business data resides in the nodes and rules of the old schema however, so a separate command with its own configuration is used to populate areas of the new schema based on data in the old.

The data is migrated according to the [RESOURCE_TYPE]_altered_nodes.csv file. This file lists nodes where business data values within the old schema should be set for nodes within the new ontology.

This file has the following columns:
- OldEntityTypeId
  - The entity in which to find the value
- NewEntityTypeId
  - The entity type to be added to the resource with said value
- GroupRootNodeOld, GroupRootNodeNew
  - Where multiple related values are being migrated to the new area of the graph, they can be moved together by specifying a pair or group root nodes are specified.
  - For example, Where the existing business data specifies a FEATURE_EVIDENCE_INTERPRETATION_TYPE with an associated certainty, and these values are to be moved to new nodes in the resource graph, the certainty can be kept associated to the type by specifying
     - GroupRootNodeOld = FEATURE_EVIDENCE_INTERPRETATION_ASSIGNMENT.E17
     - GroupRootNodeNew = FEATUREFUNCTION_AND_INTERPRETATION.I5
  - Without these group nodes specified, the data would gain the new nodes and values, but the graph structure would not associate them together. For a resource with multiple interpretation types and certainties, there would be no way to know which certainty applies to which interpretation.


To run the migration invoke the following command
```
python manage.py packages -o migrate_resources
```

N.B. This operation is not idempotent. i.e. running a given migration multiple times will lead to duplicated business data in the new area of the ontology. It is therefore recommended to divide the business data migration into multiple steps each addressing a subset of the resource graph, and proceeding with caution, taking backups at each stage.

## Verifying results
For convenience, a dictionary representation of a resource can be viewed at /resource-debug/[resourceid]
This allows a straightforward way to confirm that business data has moved as expected. This data is taken directly from the database, not from the search index.

# 4 Prune ontology and Business Data
Following a migration, old areas of ontology can be removed, along with any associated business data.

The configuration for this is stored in [RESOURCE_TYPE]_removed_nodes.csv, again in the directory specified by the Settings file.

This csv should contains a single column, listing the entitytypeids to be removed.

The business data and ontology data can be removed using
```
python manage.py packages -o prune_ontology
```

This command will remove:
- Business data
  - All entities of these types
  - Relationships to or from those entities
  - Value entries for those entities
- Ontology data
  - The entity type entries
  - Mappings and Mapping steps to these entity types
  - Rules associated to these mappings

N.B. Only leaf nodes or entire branches should be removed at the same time. Removing an intermediate entity type without also removing its descendant entity types may have adverse consequences.


# 5 Converting E27 Resources to E24
First the ontology must be imported for the E24 resource type
This can be done by putting the _nodes.csv and _edges.csv files in a directory covered by settings.RESOURCE_GRAPH_LOCATIONS

The new graph can then be loaded by invoking the command
```
python manage.py packages -o load_graphs
```

Resources can then be converted according to a csv file specifying the conversions. The conversion allows relationships to other resources to be added at the time of conversion.

| resourceid | target_resource_type | related_resourceid | relationship |
| ---------- | -------------------- | ------------------ | ------------ |
| abc-123    | PHYSICAL_MAN_MADE_THING.E24 | xyz-456 | contained |

The columns are used as follows
- *resourceid* is the entity to be converted
- target_resource_type
  - The resourcetype to convert the resource to
- related_resourceid
  - The id of the resource to which a relationship should be added
- relationship
  - The value string for the relationship. N.B. this is matched against relationship types in the values table using a LIKE query. It is preferable to use the exact string rather than the shortened version in this example.

The conversion process is executed by the following command
```
python manage.py packages -o convert_resources -s path/to/config_file.csv
```
Affected resources and relationships are reindexed during the conversion process


# Data validation utilities
2 utilities have been added to diagnose schema/data issues, which can be fixed with the above tools:
 - validate_values
 - find_unused_entity_types
 
### Validate values
This utility will examine all domain values for entity types, and verify that the chosen value is a member of the collection specified by the entity type.
```
python manage.py packages -o validate_values
```
The results are written to a file at /logs/concept_value_errors.txt

N.B.This operation takes a long time. It may be more convenient to run it for a subset of the values by setting a value. This will likely identify the general cases affected.

### Find unused entities
```
python manage.py packages -o find_unused_entity_types
```

This identifies any entity types for which there are no entities in the database. The results are written to logs/unused_entity_types.txt
