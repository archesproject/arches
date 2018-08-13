### Arches 4.3.0 release notes

The Arches team has been busy improving Arches and fixing several bugs as well.
Below you'll find a listing of all the changes that are included in the latest release.

Some of the highlights:
-


#### Upgrading Arches

Users are encouraged to update at their earliest convenience.  Completely re-installing Arches is the easiest way to accomplish this.

If you can't completely re-install Arches (because you have data in the system that you want to preserve) then you'll need to upgrade by running the following commands in your activated virtual environment:

```
pip install arches --upgrade --no-binary :all:
pip uninstall pycryptodome, rdflib-jsonld
pip install pycryptodome django-oauth-toolkit==1.1.2 PyLD[requests]==1.0.3 pyprind==2.11.2

python manage.py migrate
python manage.py es delete_indexes
python manage.py es setup_indexes
python manage.py es index_database

cd into your project's root directory (where yarn.lock is located) and run the following:
yarn add core-js@2.5.7
yarn add dom4@2.0.1
yarn install
yarn upgrade mapbox-gl@0.46.0
yarn upgrade underscore@1.9.1
```

If you have Arches running on a web server such as Apache, be sure to update your static files directory and restart your web server.

As always the documentation can be found at http://arches.readthedocs.io

#### Upgrading an Arches project

#### Changes


# Testing Script

Before Version Release, go through this checklist to confirm that Arches is running as intended.

## Index

| Test Subject   |      Chrome     |      Safari     |     Firefox     |       IE11      | UI                        | Notes                                |
| -------------- | :-------------: | :-------------: | :-------------: | :-------------: | ------------------------- | ------------------------------------ |
| (Test Subject) | (use indicator from list below) | (use indicator from list below) | (use indicator from list below) | (use indicator from list below) |:white_check_mark:(to confirm that the UI has rendered correctly) or :x: (to confirm that the UI failed to render correctly) | (add ticket #, details on bug, etc.) |

When doing a test pass, consider using these status indicators:  
:white_check_mark: = Tested & Approved
:x: = Release blocking issue
:construction: = Non-blocking issue
:ok: = Issue has been fixed
:question: = Open question

* * *

## Install

Assigned to: Cyrus (0.5)

| Test Subject                                                   | Chrome | Safari | Firefox | IE11 | UI  | Notes |
| -------------------------------------------------------------- | :----: | :----: | :-----: | :--: | --- | ----- |
| Confirm that upgrading from the previous release is issue free |    ?   |    ?   |    ?    |   ?  | ?   | -     |

* * *

## Future Release Features

Assigned to: Cyrus (0.1)

| Test Subject                                                                              | Chrome | Safari | Firefox | IE11 |  UI | Notes |
| ----------------------------------------------------------------------------------------- | :----: | :----: | :-----: | :--: | :-: | ----- |
| Test that users can't access the Mobile Survey Manager page                               |    ?   |    ?   |    ?    |   ?  |  ?  |  -    |

* * *

## Authentication

Assigned to: Alexei (.5)

Ensure that all browsers are compatible with Authentication process.

| Test Subject                                                             | Chrome | Safari | Firefox | IE11 | UI  | Notes |
| ------------------------------------------------------------------------ | :----: | :----: | :-----: | :--: | --- | ----- |
| User can sign themselves up for a new Arches account                     |    ?   |    ?   |    ?    |   ?  | ?   | -     |
| User is added to default group (Crowdsource Editor)                      |    ?   |    ?   |    ?    |   ?  | ?   | -     |
| User can log in with their email address                                 |    ?   |    ?   |    ?    |   ?  | ?   | -     |
| User can reset their password                                            |    ?   |    ?   |    ?    |   ?  | ?   | -     |
| User can edit their profile (First and Last name, email address, etc...) |    ?   |    ?   |    ?    |   ?  | ?   | -     |

* * *

## System Settings

Assigned to: Cyrus (0.25)

#### Basic Settings

| Test Subject                                                                                                                 | Chrome | Safari | Firefox | IE11 | UI  | Notes |
| ---------------------------------------------------------------------------------------------------------------------------- | :----: | :----: | :-----: | :--: | --- | ----- |
| Project Name - Updating name updates and the page tab                                                                        |    ?   |    ?   |    ?    |   ?  | ?   | -     |
| Web Analytics - String value inserts in base.htm at the location of this template variable:{{GOOGLE_ANALYTICS_TRACKING_ID}}  |    ?   |    ?   |    ?    |   ?  | ?   | -     |

#### Map Settings

Assigned to: Cyrus (1.0)

| Test Subject                                                                                                                                                                                    | Chrome | Safari | Firefox | IE11 | UI  | Notes |
| ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :----: | :----: | :-----: | :--: | --- | ----- |
| API Key - Key saves and API calls are successful                                                                                                                                                |    ?   |    ?   |    ?    |   ?  | ?   | -     |
| Hex Grid Precision - Saves properly, but errors if precision is too high (\`Exception detail: TransportError(400, u'parsing_exception', u'[geohash_grid] failed to parse field [precision]')``) |    ?   |    ?   |    ?    |   ?  | ?   | -     |
| Hex Cell Size - Changes reflected in Search results                                                                                                                                             |    ?   |    ?   |    ?    |   ?  | ?   | -     |
| Default Zoom  Changes reflected in Card Config Manager                                                                                                                                          |    ?   |    ?   |    ?    |   ?  | ?   | -     |
| Min Zoom  Changes reflected in Card Config Manager                                                                                                                                              |    ?   |    ?   |    ?    |   ?  | ?   | -     |
| Max Zoom  Changes reflected in Card Config Manager                                                                                                                                              |    ?   |    ?   |    ?    |   ?  | ?   | -     |
| Project Extent - Changes reflected in Card Config Manager                                                                                                                                       |    ?   |    ?   |    ?    |   ?  | ?   | -     |

#### Search Settings

Assigned to: Cyrus (0.25)

Basic Search Settings

| Test Subject                                                   | Chrome | Safari | Firefox | IE11 | UI  | Notes |
| -------------------------------------------------------------- | :----: | :----: | :-----: | :--: | --- | ----- |
| Searches per page updates properly in Search                   |    ?   |    ?   |    ?    |   ?  | ?   | -     |
| Number of search suggestions is reflected in search term input |    ?   |    ?   |    ?    |   ?  | ?   | -     |

Saved Searches

| Test Subject                                                                                                       | Chrome | Safari | Firefox | IE11 | UI  | Notes |
| ------------------------------------------------------------------------------------------------------------------ | :----: | :----: | :-----: | :--: | --- | ----- |
| A new search saves with a name, search url, description, and image and displays properly in the saved search page. |    ?   |    ?   |    ?    |   ?  | ?   | -     |
| Users can delete a saved search                                                                                    |    ?   |    ?   |    ?    |   ?  | ?   | -     |

* * *

## Map Widget

Assigned to: Cyrus (0.5)

Test in the Card Configuration Manager.

| Test Subject                                                                                                                                            | Chrome | Safari | Firefox | IE11 | UI  | Notes |
| ------------------------------------------------------------------------------------------------------------------------------------------------------- | :----: | :----: | :-----: | :--: | --- | ----- |
| Point line and poly geoms can be created, edited, and deleted                                                                                           |    ?   |    ?   |    ?    |   ?  | ?   | -     |
| XY widget is working properly                                                                                                                           |    ?   |    ?   |    ?    |   ?  | ?   | -     |
| Valid geojson entered in the geojson input adds features to the map and pans to those features. If geojson is invalid user has a chance to update data. |    ?   |    ?   |    ?    |   ?  | ?   | -     |
| Widget configs (maxzoom, tilt, etc) update when the map changes and the map changes when the properties change                                          |    ?   |    ?   |    ?    |   ?  | ?   | -     |

* * *

## Map Layer Manager

Assigned to: Rob (1.5)

#### Resource Layers

Assigned to: Rob

| Test Subject                                                                                                                         | Chrome | Safari | Firefox | IE11 | UI  | Notes |
| ------------------------------------------------------------------------------------------------------------------------------------ | :----: | :----: | :-----: | :--: | --- | ----- |
| Settings - changes to the name and icon of a layer are reflected in the map widget overlay list and overlay library                  |    ?   |    ?   |    ?    |   ?  | ?   | -     |
| Deactivating/Activating a resource layer hides/shows the layer in the map widget overlay list and overlay library                    |    ?   |    ?   |    ?    |   ?  | ?   | -     |
| Style Settings - changes to the layer style are displayed in the layer                                                               |    ?   |    ?   |    ?    |   ?  | ?   | -     |
| Style Settings Advanced - changes to the layer style are displayed in the layer                                                      |    ?   |    ?   |    ?    |   ?  | ?   | -     |
| Activating caching adds a cache folder for a resource in your projects tileserver directory                                          |    ?   |    ?   |    ?    |   ?  | ?   | -     |
| Activating clean cache on edit updates the cache when a geometry is edited                                                           |    ?   |    ?   |    ?    |   ?  | ?   | -     |
| Setting permissions for a user or group as No Access removes the user and group from the permissions list under the permissions tab. |    ?   |    ?   |    ?    |   ?  | ?   | -     |

#### Clustering (Resource Layers)

Assigned to: Rob

| Test Subject                                                                               | Chrome | Safari | Firefox | IE11 | UI  | Notes |
| ------------------------------------------------------------------------------------------ | :----: | :----: | :-----: | :--: | --- | ----- |
| Increasing cluster distance causes features to cluster at increased distances between them |    ?   |    ?   |    ?    |   ?  | ?   | -     |
| Increasing cluster max zoom causes clusters to be formed at higher zoom levels             |    ?   |    ?   |    ?    |   ?  | ?   | -     |
| Decreasing min points to 2 points causes clusters to form with only 2 points               |    ?   |    ?   |    ?    |   ?  | ?   | -     |
| Increasing vector simplification to 0.0 prevents simplification a low zoom levels          |    ?   |    ?   |    ?    |   ?  | ?   | -     |

#### Basemaps

Assigned to: Rob

| Test Subject                                                                                    | Chrome | Safari | Firefox | IE11 | UI  | Notes |
| ----------------------------------------------------------------------------------------------- | :----: | :----: | :-----: | :--: | --- | ----- |
| Changing the default search basemap in the basemap settings is reflected on the search page     |    ?   |    ?   |    ?    |   ?  | ?   | -     |
| Settings - changes to the name and icon of a layer are reflected in the map widget basemap list |    ?   |    ?   |    ?    |   ?  | ?   | -     |
| User can delete a basemap and it no longer appears in the map widget's list of basemaps         |    ?   |    ?   |    ?    |   ?  | ?   | -     |

#### Overlays

Assigned to: Rob

| Test Subject                                                                                                        | Chrome | Safari | Firefox | IE11 | UI  | Notes |
| ------------------------------------------------------------------------------------------------------------------- | :----: | :----: | :-----: | :--: | --- | ----- |
| Settings - changes to the name and icon of a layer are reflected in the map widget overlay list and overlay library |    ?   |    ?   |    ?    |   ?  | ?   | -     |
| User can delete an overlay and it no longer appears in the map widget overlay library                               |    ?   |    ?   |    ?    |   ?  | ?   | -     |
| Overlays support custom popups                                                                                      |    ?   |    ?   |    ?    |   ?  | ?   | -     |
* * *

## Import/Export

Assigned to: Ryan (0.5)

| Test Subject               | Chrome | Safari | Firefox | IE11 | UI  | Notes |
| -------------------------- | :----: | :----: | :-----: | :--: | --- | ----- |
| Create_mapping_file        |    ?   |    ?   |    ?    |   ?  | ?   | -     |
| Import business data (cli) |    ?   |    ?   |    ?    |   ?  | ?   | -     |
| Export business data (cli) |    ?   |    ?   |    ?    |   ?  | ?   | -     |
| Load package (cli)         |    ?   |    ?   |    ?    |   ?  | ?   | -     |
| Create package (cli)       |    ?   |    ?   |    ?    |   ?  | ?   | -     |

* * *

## Resource Instance Management

Assigned to: Adam

#### Data Types

Confirm that the user is able to edit the following data types. Use the Test model to quickly test all ten data types.
Note (GeoJson is covered by map widget testing in a different section)

| Test Subject           | Chrome | Safari | Firefox | IE11 | UI  | Notes |
| ---------------------- | :----: | :----: | :-----: | :--: | --- | ----- |
| String                 |    ?   |    ?   |    ?    |   ?  | ?   | -     |
| Concepts               |    ?   |    ?   |    ?    |   ?  | ?   | -     |
| Domains                |    ?   |    ?   |    ?    |   ?  | ?   | -     |
| Images                 |    ?   |    ?   |    ?    |   ?  | ?   | -     |
| Dates                  |    ?   |    ?   |    ?    |   ?  | ?   | -     |
| Number                 |    ?   |    ?   |    ?    |   ?  | ?   | -     |
| Boolean                |    ?   |    ?   |    ?    |   ?  | ?   | -     |
| Resource instance type |    ?   |    ?   |    ?    |   ?  | ?   | -     |
| Node data type         |    ?   |    ?   |    ?    |   ?  | ?   | -     |

#### Resource Descriptors

Assigned to: Adam

Updating a resource descriptor should be reflected in the following subjects.

| Test Subject                                                                                        | Chrome | Safari | Firefox | IE11 | UI  | Notes |
| --------------------------------------------------------------------------------------------------- | :----: | :----: | :-----: | :--: | --- | ----- |
| Search results                                                                                      |    ?   |    ?   |    ?    |   ?  | ?   | -     |
| Form headings                                                                                       |    ?   |    ?   |    ?    |   ?  | ?   | -     |
| Report headings                                                                                     |    ?   |    ?   |    ?    |   ?  | ?   | -     |
| Map popups                                                                                          |    ?   |    ?   |    ?    |   ?  | ?   | -     |
| Related resource d3 graph and listings                                                              |    ?   |    ?   |    ?    |   ?  | ?   | -     |

* * *

#### Provisional Edit Management

Assigned to: Cyrus (0.5)

| Test Subject                                                                                        | Chrome | Safari | Firefox | IE11 | UI  | Notes |
| --------------------------------------------------------------------------------------------------- | :----: | :----: | :-----: | :--: | --- | ----- |
| Provisional users see indication in a widget that their tile edits were submitted                   |    ?   |    ?   |    ?    |   ?  | ?   | -     |
| Resource reviewers are able to identify provisional tiles and can approve/discard provisional edits |    ?   |    ?   |    ?    |   ?  | ?   | -     |
| Provisional edit history properly shows the status of a tile: pending, approved, or declined        |    ?   |    ?   |    ?    |   ?  | ?   | -     |

* * *

## Related Resources

Assigned to: Jeff

#### Resource Editor

| Test Subject                                           | Chrome | Safari | Firefox | IE11 | UI  | Notes |
| ------------------------------------------------------ | :----: | :----: | :-----: | :--: | --- | ----- |
| User can add a related resource                        |    ?   |    ?   |    ?    |   ?  | ?   | -     |
| User can delete a related resource                     |    ?   |    ?   |    ?    |   ?  | ?   | -     |
| User can change the properties of related resources    |    ?   |    ?   |    ?    |   ?  | ?   | -     |
| User can switch between table and force directed graph |    ?   |    ?   |    ?    |   ?  | ?   | -     |
| User can page through related resources in table       |    ?   |    ?   |    ?    |   ?  | ?   | -     |

#### Resource Search (.5)

| Test Subject                                                                                                                           | Chrome | Safari | Firefox | IE11 | UI  | Notes |
| -------------------------------------------------------------------------------------------------------------------------------------- | :----: | :----: | :-----: | :--: | --- | ----- |
| Hovering over a link in the force directed graph opens a panel with source and target node info and list each unique relationship type |    ?   |    ?   |    ?    |   ?  | ?   | -     |
| Hovering over a node highlights the adjacent links and the corresponding entry in the node list                                        |    ?   |    ?   |    ?    |   ?  | ?   | -     |
| Hovering over a node list entry highlights the corresponding node and its adjacent links                                               |    ?   |    ?   |    ?    |   ?  | ?   | -     |
| User can switch between table and force directed graph                                                                                 |    ?   |    ?   |    ?    |   ?  | ?   | -     |
| Entering text in the search field filters the list of list entries                                                                     |    ?   |    ?   |    ?    |   ?  | ?   | -     |


* * *

## Search

Assigned to: Jeff (.5)

| Test Subject                                                                                                                                                                         | Chrome | Safari | Firefox | IE11 | UI  | Notes |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | :----: | :----: | :-----: | :--: | --- | ----- |
| Free text search                                                                                                                                                                     |    ?   |    ?   |    ?    |   ?  | ?   | -     |
| Concept search                                                                                                                                                                       |    ?   |    ?   |    ?    |   ?  | ?   | -     |
| Map search                                                                                                                                                                           |    ?   |    ?   |    ?    |   ?  | ?   | -     |
| Time range based search                                                                                                                                                              |    ?   |    ?   |    ?    |   ?  | ?   | -     |
| Time wheel search                                                                                                                                                                    |    ?   |    ?   |    ?    |   ?  | ?   | -     |
| Advanced search                                                                                                                                                                      |    ?   |    ?   |    ?    |   ?  | ?   | -     |
| Related resource table search                                                                                                                                                        |    ?   |    ?   |    ?    |   ?  | ?   | -     |
| Related resource graph list filter graph                                                                                                                                             |    ?   |    ?   |    ?    |   ?  | ?   | -     |
| Resource type search                                                                                                                                                                 |    ?   |    ?   |    ?    |   ?  | ?   | -     |
| Edit status search (provisional, authoritative, or both). Confirm that only resource reviewers are able to see provisional tile data                                                 |    ?   |    ?   |    ?    |   ?  | ?   | -     |
| Map should not zoom to points that a user is not permitted to read, nor should the search aggregation layer (e.g. hexbin or heatmap) indicate that a restricted resource is present. |    ?   |    ?   |    ?    |   ?  | ?   | -     |

* * *

Assigned to: Alexei (1.5)

## Graph/Resource Designer

| Test Subject     | Chrome | Safari | Firefox | IE11 | UI  | Notes |
| ---------------- | :----: | :----: | :-----: | :--: | --- | ----- |
| Export graph     |    ?   |    ?   |    ?    |   ?  | ?   | -     |
| Import graph     |    ?   |    ?   |    ?    |   ?  | ?   | -     |
| Create branch    |    ?   |    ?   |    ?    |   ?  | ?   | -     |
| Create resource  |    ?   |    ?   |    ?    |   ?  | ?   | -     |
| Add/Edit cards   |    ?   |    ?   |    ?    |   ?  | ?   | -     |
| Add/Edit menus   |    ?   |    ?   |    ?    |   ?  | ?   | -     |
| Add/Edit reports |    ?   |    ?   |    ?    |   ?  | ?   | -     |
| delete graph     |    ?   |    ?   |    ?    |   ?  | ?   | -     |
| clone graph      |    ?   |    ?   |    ?    |   ?  | ?   | -     |

* * *

## Permissions Management

Assigned to: Ryan (1)

| Test Subject                                                                                                                                            | Chrome | Safari | Firefox | IE11 | UI  | Notes |
| ------------------------------------------------------------------------------------------------------------------------------------------------------- | :----: | :----: | :-----: | :--: | --- | ----- |
| Confirm removing `read` permissions removes that section from the report                                                                                |    ?   |    ?   |    ?    |   ?  | ?   | -     |
| Confirm removing `read` permissions removes that section from the form                                                                                  |    ?   |    ?   |    ?    |   ?  | ?   | -     |
| Confirm removing `read` permissions removes that section from the adv. search                                                                           |    ?   |    ?   |    ?    |   ?  | ?   | -     |
| Confirm removing `read` permissions for a spatial nodegroup removes that resource type from map based search results                                    |    ?   |    ?   |    ?    |   ?  | ?   | -     |
| Confirm removing `read` permissions for a spatial nodegroup removes that resource type from the overlays section of the map settings                    |    ?   |    ?   |    ?    |   ?  | ?   | -     |
| Confirm removing `read` permissions for a spatial nodegroup removes the map from the Map Report                                                         |    ?   |    ?   |    ?    |   ?  | ?   | -     |
| Confirm removing `read` permissions for a date based nodegroup removes the related entries from the type dropdown in the time filter of the search page |    ?   |    ?   |    ?    |   ?  | ?   | -     |
| Confirm removing `read` permissions for a date based nodegroup reduces the wheel count appropriately                                                    |    ?   |    ?   |    ?    |   ?  | ?   | -     |
| Confirm removing `write` permissions but still having read permissions disallows saving that section of the form                                        |    ?   |    ?   |    ?    |   ?  | ?   | -     |

* * *

## Reports

Assigned to: Adam

#### Headers Rendering

| Test Subject                                                            | Chrome | Safari | Firefox | IE11 | UI  | Notes |
| ----------------------------------------------------------------------- | :----: | :----: | :-----: | :--: | --- | ----- |
| Confirm that report templates with map header gets rendered correctly   |    ?   |    ?   |    ?    |   ?  | ?   | -     |
| Confirm that report templates with image header gets rendered correctly |    ?   |    ?   |    ?    |   ?  | ?   | -     |
| Confirm that report templates with no header gets rendered correctly    |    ?   |    ?   |    ?    |   ?  | ?   | -     |

#### Data Rendering

| Test Subject           | Chrome | Safari | Firefox | IE11 | UI  | Notes |
| ---------------------- | :----: | :----: | :-----: | :--: | --- | ----- |
| String                 |    ?   |    ?   |    ?    |   ?  | ?   | -     |
| Concepts               |    ?   |    ?   |    ?    |   ?  | ?   | -     |
| Domains                |    ?   |    ?   |    ?    |   ?  | ?   | -     |
| Images                 |    ?   |    ?   |    ?    |   ?  | ?   | -     |
| Dates                  |    ?   |    ?   |    ?    |   ?  | ?   | -     |
| Number                 |    ?   |    ?   |    ?    |   ?  | ?   | -     |
| Boolean                |    ?   |    ?   |    ?    |   ?  | ?   | -     |
| Resource instance type |    ?   |    ?   |    ?    |   ?  | ?   | -     |
| Node data type         |    ?   |    ?   |    ?    |   ?  | ?   | -     |

* * *

## RDM

Assigned to: Ryan (1)

#### Thesauri

| Test Subject       | Chrome | Safari | Firefox | IE11 | UI  | Notes |
| ------------------ | :----: | :----: | :-----: | :--: | --- | ----- |
| Add scheme         |    ?   |    ?   |    ?    |   ?  | ?   | -     |
| Delete scheme      |    ?   |    ?   |    ?    |   ?  | ?   | -     |
| Import scheme      |    ?   |    ?   |    ?    |   ?  | ?   | -     |
| Export scheme      |    ?   |    ?   |    ?    |   ?  | ?   | -     |
| Add top concept    |    ?   |    ?   |    ?    |   ?  | ?   | -     |
| Import from SPARQL |    ?   |    ?   |    ?    |   ?  | ?   | -     |
| Manage parents     |    ?   |    ?   |    ?    |   ?  | ?   | -     |
| Make collection    |    ?   |    ?   |    ?    |   ?  | ?   | -     |
| Add label          |    ?   |    ?   |    ?    |   ?  | ?   | -     |
| Add Note           |    ?   |    ?   |    ?    |   ?  | ?   | -     |
| Add image          |    ?   |    ?   |    ?    |   ?  | ?   | -     |

#### Collections

| Test Subject                           | Chrome | Safari | Firefox | IE11 | UI  | Notes |
| -------------------------------------- | :----: | :----: | :-----: | :--: | --- | ----- |
| Add collection                         |    ?   |    ?   |    ?    |   ?  | ?   | -     |
| Delete collection                      |    ?   |    ?   |    ?    |   ?  | ?   | -     |
| Export all collections                 |    ?   |    ?   |    ?    |   ?  | ?   | -     |
| Add dropdown entry                     |    ?   |    ?   |    ?    |   ?  | ?   | -     |
| Add sort order and confirm in dropdown |    ?   |    ?   |    ?    |   ?  | ?   | -     |

* * *
