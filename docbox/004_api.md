# API

## Web API

## Data/Import API

### Branches

#### Cards

#### Vocabulary

#### Business Data

#### Functions

### Graphs

`python manage.py packages -o import_json(package_name, data_source)` - the import_json command loads the nodes and edges arrays from the arches4json to Arches. Calls the command `ArchesFile(data_source).import_graphs()`. Note, this command will also import ontology data. All ontology classes used in a graph must be present in the ontology(ies) loaded to or already existing in Arches.

	Parameters:
		package_name - 
		data_source - file path to arches4json file including the file name. Default: RESOURCE_GRAPH_LOCATIONS filepath from django settings.py or settings_local.py file. 

### GIS Data

#### Shapefiles

#### KML

#### JSON

### CSV
