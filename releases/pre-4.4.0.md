### Arches 4.4.0 release notes

The Arches team has been busy improving Arches and fixing several bugs as well.
Below you'll find a listing of all the changes that are included in the latest release.

Some of the highlights:

- Debut of the Arches Collection Manager for designing mobile projects for the Arches Collector App
- Addition of Arches Plugin components
- Default Ubuntu installation is now Ubuntu 18.04 LTS
- Cards represented in reports are now collapsible
- Users can now edit any card for which they have write permissions (edited)
- Tile datatype validation is now always applied on save
- Provisional edit review is now fully available for file, map, and iiif widgets
- Usability enhancements in resource editor tree selection
- Enhancements to card component viewmodel for easier customization

#### Upgrading Arches

Users are encouraged to update at their earliest convenience.  Completely re-installing Arches is the easiest way to accomplish this.

If you can't completely re-install Arches (because you have data in the system that you want to preserve) then you'll need to upgrade by running the following commands in your activated virtual environment:

```
pip install arches --upgrade --no-binary :all:
python manage.py migrate
python manage.py es delete_indexes
python manage.py es setup_indexes
python manage.py es index_database
```

If you have Arches running on a web server such as Apache, be sure to update your static files directory and restart your web server.

As always the documentation can be found at <http://arches.readthedocs.io>

#### Upgrading an Arches project

1.  Add the following to your package.json file:

        "datatables.net-buttons": "^1.5.4",
        "datatables.net-buttons-bs": "^1.5.4"

        and run: `yarn install`

2. If you intend to use the Arches Collector you will need to install and configure CouchDB:

        sudo add-apt-repository "deb https://apache.bintray.com/couchdb-deb $(lsb_release -sc) main"
        wget --quiet -O - https://couchdb.apache.org/repo/bintray-pubkey.asc | sudo apt-key add -
        sudo apt-get update
        sudo apt-get install couchdb

    By default arches connects to couch using the following credentials:

    	username: admin
    	password: admin
    	http://localhost:5984/

    You'll also need to add the following settings to your project's settings.py file:

        MOBILE_OAUTH_CLIENT_ID = ''
        MOBILE_DEFAULT_ONLINE_BASEMAP = {'default': 'mapbox://styles/mapbox/streets-v9'}
        COUCHDB_URL = 'http://admin:admin@localhost:5984'

    You may want to update this setting to something more secure:

    	COUCHDB_URL = 'http://admin:admin@localhost:5984'

    Now you can create a new oauth client for the api:
        https://arches.readthedocs.io/en/stable/api/?highlight=application#authentication

    Finally, if you are running Apache, you will need to add the following directive to your site's `000-default.conf` file:

    	WSGIPassAuthorization on


# Testing Script

Before Version Release, go through this checklist to confirm that Arches is running as intended.

## Index

| Test Subject   |      Chrome     |      Safari     |     Firefox     |       IE11      | UI                        | Notes                                |
| -------------- | :-------------: | :-------------: | :-------------: | :-------------: | ------------------------- | ------------------------------------ |
| (Test Subject) | (use indicator from list below) | (use indicator from list below) | (use indicator from list below) | (use indicator from list below) | :white_check_mark: (to confirm that the UI has rendered correctly) or :x: (to confirm that the UI failed to render correctly) | (add ticket #, details on bug, etc.) |

When doing a test pass, consider using these status indicators:  
:white_check_mark: = Tested & Approved  
:x: = Merge blocking  
:construction: = Non-blocking bugs  
:ok: = Issue has been fixed  
:question: = Open question  

* * *

## Install

Assigned to: Alexei

| Test Subject                                                   | Chrome | Safari | Firefox | IE11 | UI  | Notes |
| -------------------------------------------------------------- | :----: | :----: | :-----: | :--: | --- | ----- |
| Confirm that upgrading from the previous release is issue free ||    ?   |    ?    |   ?  | ?   | -     |

* * *

## Authentication

Assigned to: Ryan

Ensure that all browsers are compatible with Authentication process.

| Test Subject                                                             | Chrome | Safari | Firefox | IE11 | UI  | Notes |
| ------------------------------------------------------------------------ | :----: | :----: | :-----: | :--: | --- | ----- |
| User can sign themselves up for a new Arches account                     |:white_check_mark:     |    ?   |    ?    |   ?  | ?   | -     |
| User is added to default group (Crowdsource Editor)                      |:white_check_mark:       |    ?   |    ?    |   ?  | ?   | -     |
| User can log in with their email address                                 |:white_check_mark:       |    ?   |    ?    |   ?  | ?   | -     |
| User can reset their password                                            |:white_check_mark:       |    ?   |    ?    |   ?  | ?   | -     |
| User can edit their profile (First and Last name, email address, etc...) |:white_check_mark:       |    ?   |    ?    |   ?  | ?   | -     |

* * *

## System Settings

Assigned to: Cyrus

#### Basic Settings

| Test Subject                                                                                                                 | Chrome | Safari | Firefox | IE11 | UI  | Notes |
| ---------------------------------------------------------------------------------------------------------------------------- | :----: | :----: | :-----: | :--: | --- | ----- |
| Project Name - Updating name updates in index.htm and the page tab                                                           |:white_check_mark:|    ?   |    ?    |   ?  | ?   | -     |
| Web Analytics - String value inserts in base.htm at the location of this template variable:{{GOOGLE_ANALYTICS_TRACKING_ID}} |:white_check_mark:|    ?   |    ?    |   ?  | ?   | -     |

#### Map Settings

Assigned to: Galen (extent verified by @chiatt)

| Test Subject                                                                                                                                                                                    | Chrome | Safari | Firefox | IE11 | UI  | Notes |
| ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :----: | :----: | :-----: | :--: | --- | ----- |
| API Key - Key saves and API calls are successful                                                                                                                                                ||    ?   |    ?    |   ?  | ?   | -     |
| Hex Grid Precision - Saves properly, but errors if precision is too high (\`Exception detail: TransportError(400, u'parsing_exception', u'[geohash_grid] failed to parse field [precision]')``) ||    ?   |    ?    |   ?  | ?   | -     |
| Hex Cell Size - Changes reflected in Search results                                                                                                                                             ||    ?   |    ?    |   ?  | ?   | -     |
| Default Zoom - Changes reflected in Card Config Manager                                                                                                                                         ||    ?   |    ?    |   ?  | ?   | -     |
| Min Zoom - Changes reflected in Card Config Manager                                                                                                                                             ||    ?   |    ?    |   ?  | ?   | -     |
| Max Zoom - Changes reflected in Card Config Manager                                                                                                                                             ||    ?   |    ?    |   ?  | ?   | -     |
| Project Extent - Changes reflected in Card Config Manager                                                                                                                                       ||    ?   |    ?    |   ?  | ?   | -     |

#### Search Settings

Assigned to: Galen

Basic Search Settings

| Test Subject                                                   | Chrome | Safari | Firefox | IE11 | UI  | Notes |
| -------------------------------------------------------------- | :----: | :----: | :-----: | :--: | --- | ----- |
| Searches per page updates properly in Search                   ||    ?   |    ?    |   ?  | ?   | -     |
| Number of search suggestions is reflected in search term input ||    ?   |    ?    |   ?  | ?   | -     |

Temporal Search Settings (not in use)

| Test Subject                                                                                       | Chrome | Safari | Firefox | IE11 | UI  | Notes |
| -------------------------------------------------------------------------------------------------- | :----: | :----: | :-----: | :--: | --- | ----- |
| Changes in time wheel color ramp are reflected in time wheel change time wheel colors (not in use) |    -   |    -   |    -    |   -  | -   | -     |
| Changes in time wheel config are reflected in time wheel (not in use)                              |    -   |    -   |    -    |   -  | -   | -     |

Saved Searches

| Test Subject                                                                                                       | Chrome | Safari | Firefox | IE11 | UI  | Notes |
| ------------------------------------------------------------------------------------------------------------------ | :----: | :----: | :-----: | :--: | --- | ----- |
| A new search saves with a name, search url, description, and image and displays properly in the saved search page. ||    ?   |    ?    |   ?  | ?   | -     |
| Users can delete a saved search                                                                                    ||    ?   |    ?    |   ?  | ?   | -     |

* * *

## Map Widget

Assigned to: Namjun

Test in the Card Configuration Manager.

| Test Subject                                                                                                                                            | Chrome | Safari | Firefox | IE11 | UI  | Notes |
| ------------------------------------------------------------------------------------------------------------------------------------------------------- | :----: | :----: | :-----: | :--: | --- | ----- |
| Point line and poly geoms can be created, edited, and deleted                                                                                           ||    ?   |    ?    |   ?  | ?   | -     |
| XY widget is working properly                                                                                                                           ||    ?   |    ?    |   ?  | ?   | -     |
| Valid geojson entered in the geojson input adds features to the map and pans to those features. If geojson is invalid user has a chance to update data. ||    ?   |    ?    |   ?  | ?   | -     |

* * *

## Map Layer Manager

Assigned to: Rob

#### Resource Layers

Assigned to: Rob

| Test Subject                                                                                                                         | Chrome | Safari | Firefox | IE11 | UI  | Notes |
| ------------------------------------------------------------------------------------------------------------------------------------ | :----: | :----: | :-----: | :--: | --- | ----- |
| Settings - changes to the name and icon of a layer are reflected in the map widget overlay list and overlay library                  |:white_check_mark:|    ?   |    ?    |   ?  | ?   | -     |
| Deactivating/Activating a resource layer hides/shows the layer in the map widget overlay list and overlay library                    |:white_check_mark:|    ?   |    ?    |   ?  | ?   | -     |
| Style Settings - changes to the layer style are displayed in the layer                                                               |:white_check_mark:|    ?   |    ?    |   ?  | ?   | -     |
| Style Settings Advanced - changes to the layer style are displayed in the layer                                                      |:white_check_mark:|    ?   |    ?    |   ?  | ?   | -     |
| Activating caching adds a cache folder for a resource in your projects tile server directory                                          |:white_check_mark:|    ?   |    ?    |   ?  | ?   | -     |
| Activating clean cache on edit updates the cache when a geometry is edited                                                           |:white_check_mark:|    ?   |    ?    |   ?  | ?   | -     |
| Setting permissions for a user or group as No Access removes the user and group from the permissions list under the permissions tab. |:white_check_mark:|    ?   |    ?    |   ?  | ?   | -     |

#### Clustering (Resource Layers)

Assigned to: Rob

| Test Subject                                                                               | Chrome | Safari | Firefox | IE11 | UI  | Notes |
| ------------------------------------------------------------------------------------------ | :----: | :----: | :-----: | :--: | --- | ----- |
| Increasing cluster distance causes features to cluster at increased distances between them |:white_check_mark:|    ?   |    ?    |   ?  | ?   | -     |
| Increasing cluster max zoom causes clusters to be formed at higher zoom levels             |:white_check_mark:|    ?   |    ?    |   ?  | ?   | -     |
| Decreasing min points to 2 points causes clusters to form with only 2 points               |:white_check_mark:|    ?   |    ?    |   ?  | ?   | -     |
| Increasing vector simplification to 0.0 prevents simplification a low zoom levels          |:white_check_mark:|    ?   |    ?    |   ?  | ?   | -     |

#### Basemaps

Assigned to: Rob

| Test Subject                                                                                    | Chrome | Safari | Firefox | IE11 | UI  | Notes |
| ----------------------------------------------------------------------------------------------- | :----: | :----: | :-----: | :--: | --- | ----- |
| Changing the default search basemap in the basemap settings is reflected on the search page     |:white_check_mark:|    ?   |    ?    |   ?  | ?   | -     |
| Settings - changes to the name and icon of a layer are reflected in the map widget basemap list |:white_check_mark:|    ?   |    ?    |   ?  | ?   | -     |
| User can delete a basemap and it no longer appears in the map widget's list of basemaps         |:white_check_mark:|    ?   |    ?    |   ?  | ?   | -     |

#### Overlays

Assigned to: Rob

| Test Subject                                                                                                        | Chrome | Safari | Firefox | IE11 | UI  | Notes |
| ------------------------------------------------------------------------------------------------------------------- | :----: | :----: | :-----: | :--: | --- | ----- |
| Settings - changes to the name and icon of a layer are reflected in the map widget overlay list and overlay library |:white_check_mark:|    ?   |    ?    |   ?  | ?   | -     |
| User can delete an overlay and it no longer appears in the map widget overlay library                               |:white_check_mark:|    ?   |    ?    |   ?  | ?   | -     |

* * *

## Import/Export

Assigned to: Cyrus

| Test Subject               | Chrome | Safari | Firefox | IE11 | UI  | Notes |
| -------------------------- | :----: | :----: | :-----: | :--: | --- | ----- |
| Create_mapping_file        |:white_check_mark:|    ?   |    ?    |   ?  | ?   | -     |
| Import business data (cli) |:construction:|    ?   |    ?    |   ?  | ?   | #4625 |
| Export business data (cli) |:white_check_mark:|    ?   |    ?    |   ?  | ?   | -     |
| Load package (cli)         |:white_check_mark:|    ?   |    ?    |   ?  | ?   | -     |
| Create package (cli)       |:white_check_mark:|    ?   |    ?    |   ?  | ?   | -     |

* * *

## Resource Instance Management

Assigned to: Namjun

#### Data Types

Confirm that the user is able to edit the following data types. Use the Test model to quickly test all ten data types.
Note (GeoJson is covered by map widget testing in a different section)

| Test Subject           | Chrome | Safari | Firefox | IE11 | UI  | Notes |
| ---------------------- | :----: | :----: | :-----: | :--: | --- | ----- |
| String                 ||    ?   |    ?    |   ?  | ?   | -     |
| Concepts               ||    ?   |    ?    |   ?  | ?   | -     |
| Domains                ||    ?   |    ?    |   ?  | ?   | -     |
| Images                 ||    ?   |    ?    |   ?  | ?   | -     |
| Dates                  ||    ?   |    ?    |   ?  | ?   | -     |
| Number                 ||    ?   |    ?    |   ?  | ?   | -     |
| Boolean                ||    ?   |    ?    |   ?  | ?   | -     |
| Resource instance type ||    ?   |    ?    |   ?  | ?   | -     |
| Node data type         ||    ?   |    ?    |   ?  | ?   | -     |

#### Resource Descriptors

Assigned to: Alexei

Updating a resource descriptor should be reflected in the following subjects.

| Test Subject                                                                                        | Chrome | Safari | Firefox | IE11 | UI  | Notes |
| --------------------------------------------------------------------------------------------------- | :----: | :----: | :-----: | :--: | --- | ----- |
| Search results                                                                                      || :white_check_mark: | :white_check_mark:  |:white_check_mark:| ?   | -     |
| Form headings                                                                                       || :white_check_mark: | :white_check_mark:  |:white_check_mark:| ?   | -     |
| Report headings                                                                                     || :white_check_mark: | :white_check_mark:  |:white_check_mark:| ?   | -     |
| Map popups                                                                                          || :white_check_mark: | :white_check_mark:  |:white_check_mark:| ?   | -     |
| Related resource d3 graph and listings                                                              || :white_check_mark: | :white_check_mark:  |:white_check_mark:| ?   | -     |

* * *

#### Provisional Edit Management

Assigned to: Ryan

| Test Subject                                           | Chrome | Safari | Firefox | IE11 | UI  | Notes |
| ------------------------------------------------------ | :----: | :----: | :-----: | :--: | --- | ----- |
| Provisional users see indication in a widget that their tile edits were submitted                   |:white_check_mark:|    ?   |    ?    |   ?  | ?   | -     |
| Resource reviewers are able to identify provisional tiles and can approve/discard provisional edits |:white_check_mark:|    ?   |    ?    |   ?  | ?   | -     |

* * *

## Related Resources

Assigned to: Galen

#### Resource Editor

| Test Subject                                           | Chrome | Safari | Firefox | IE11 | UI  | Notes |
| ------------------------------------------------------ | :----: | :----: | :-----: | :--: | --- | ----- |
| User can add a related resource                        ||    ?   |    ?    |   ?  | ?   | -     |
| User can delete a related resource                     ||    ?   |    ?    |   ?  | ?   | -     |
| User can change the properties of related resources    ||    ?   |    ?    |   ?  | ?   | -     |
| User can switch between table and force directed graph ||    ?   |    ?    |   ?  | ?   | -     |
| User can page through related resources in table       ||    ?   |    ?    |   ?  | ?   | -     |

#### Resource Search

| Test Subject                                                                                                                           | Chrome | Safari | Firefox | IE11 | UI  | Notes |
| -------------------------------------------------------------------------------------------------------------------------------------- | :----: | :----: | :-----: | :--: | --- | ----- |
| Hovering over a link in the force directed graph opens a panel with source and target node info and list each unique relationship type ||    ?   |    ?    |   ?  | ?   | -     |
| Hovering over a node highlights the adjacent links and the corresponding entry in the node list                                        ||    ?   |    ?    |   ?  | ?   | -     |
| Hovering over a node list entry highlights the corresponding node and its adjacent links                                               ||    ?   |    ?    |   ?  | ?   | -     |
| User can switch between table and force directed graph                                                                                 ||    ?   |    ?    |   ?  | ?   | -     |
| Entering text in the search field filters the list of list entries                                                                     ||    ?   |    ?    |   ?  | ?   | -     |
| Overlays support custom popups                                                                                                         |    ?   |    ?   |    ?    |   ?  | ?   | -     |

* * *

## Search

Assigned to: Alexei

| Test Subject                                                                                                                                                                         | Chrome | Safari | Firefox | IE11 | UI  | Notes |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | :----: | :----: | :-----: | :--: | --- | ----- |
| Free text search                                                                                                                                                                     || :white_check_mark: | :white_check_mark:  |:white_check_mark:| ?   | -     |
| Concept search                                                                                                                                                                       || :white_check_mark: | :white_check_mark:  |:white_check_mark:| ?   | -     |
| Map search                                                                                                                                                                           || :white_check_mark: | :white_check_mark:  |:white_check_mark:| ?   | -     |
| Time range based search                                                                                                                                                              || :white_check_mark: | :white_check_mark:  |:white_check_mark:| ?   | -     |
| Time wheel search                                                                                                                                                                    || :white_check_mark: | :white_check_mark:  |:white_check_mark:| ?   | -     |
| Advanced search                                                                                                                                                                      || :white_check_mark: | :white_check_mark:  |:white_check_mark:| ?   | -     |
| Related resource table search                                                                                                                                                        |:construction:|    ?   |    ?    |   ?  | ?   |Table filter is not available|
| Related resource graph search                                                                                                                                                        || :white_check_mark: | :white_check_mark:  |:white_check_mark:| ?   | -     |
| Resource type search                                                                                                                                                                 || :white_check_mark: | :white_check_mark:  |:white_check_mark:| ?   | -     |
| Edit status search (provisional, authoritative, or both). Confirm that only resource reviewers are able to see provisional tile data                                                 || :white_check_mark: | :white_check_mark:  |:white_check_mark:| ?   | -     |
| Map should not zoom to points that a user is not permitted to read, nor should the search aggregation layer (e.g. hexbin or heatmap) indicate that a restricted resource is present. || :white_check_mark: | :white_check_mark:  |:white_check_mark:| ?   | -     |

* * *

## Graph Design

Assigned to: Namjun

### Arches Designer

| Test Subject     | Chrome | Safari | Firefox | IE11 | UI  | Notes |
| ---------------- | :----: | :----: | :-----: | :--: | --- | ----- |
| Import graph     ||    ?   |    ?    |   ?  | ?   | -     |
| Export graph     ||    ?   |    ?    |   ?  | ?   | -     |
| Clone graph      ||    ?   |    ?    |   ?  | ?   | -     |
| Delete graph     ||    ?   |    ?    |   ?  | ?   | -     |
| Create branch    ||    ?   |    ?    |   ?  | ?   | -     |
| Create graph     ||    ?   |    ?    |   ?  | ?   | -     |
| Delete Instances ||    ?   |    ?    |   ?  | ?   | -     |

### Graph Designer

| Test Subject     | Chrome | Safari | Firefox | IE11 | UI  | Notes |
| ---------------- | :----: | :----: | :-----: | :--: | --- | ----- |
| Import graph     |    ?   |    ?   |    ?    |   ?  | ?   | -     |
| Export graph     |    ?   |    ?   |    ?    |   ?  | ?   | -     |
| Clone graph      |    ?   |    ?   |    ?    |   ?  | ?   | -     |
| Delete graph     |    ?   |    ?   |    ?    |   ?  | ?   | -     |
| Create branch    |    ?   |    ?   |    ?    |   ?  | ?   | -     |
| Create graph     ||    ?   |    ?    |   ?  | ?   | -     |
| Delete Instances ||    ?   |    ?    |   ?  | ?   | -     |
| Add/Edit cards   ||    ?   |    ?    |   ?  | ?   | -     |
| Reorder widgets  in card ||    ?   |    ?    |   ?  | ?   | -     |

* * *

## Permissions Management

Assigned to: Ryan

| Test Subject                                                                                                                                            | Chrome | Safari | Firefox | IE11 | UI  | Notes |
| ------------------------------------------------------------------------------------------------------------------------------------------------------- | :----: | :----: | :-----: | :--: | --- | ----- |
| Confirm removing `read` permissions removes that section from the report                                                                                |       |    ?   |    ?    |   ?  | ?   | -     |
| Confirm removing `read` permissions removes that section from the form                                                                                  |       |    ?   |    ?    |   ?  | ?   | -     |
| Confirm removing `read` permissions removes that section from the adv. search                                                                           |       |    ?   |    ?    |   ?  | ?   | -     |
| Confirm removing `read` permissions for a spatial nodegroup removes that resource type from map based search results                                    |       |    ?   |    ?    |   ?  | ?   | -     |
| Confirm removing `read` permissions for a spatial nodegroup removes that resource type from the overlays section of the map settings                    |       |    ?   |    ?    |   ?  | ?   | -     |
| Confirm removing `read` permissions for a spatial nodegroup removes the map from the Map Report                                                         |       |    ?   |    ?    |   ?  | ?   | -     |
| Confirm removing `read` permissions for a date based nodegroup removes the related entries from the type dropdown in the time filter of the search page |       |    ?   |    ?    |   ?  | ?   | -     |
| Confirm removing `read` permissions for a date based nodegroup reduces the wheel count appropriately                                                    |       |    ?   |    ?    |   ?  | ?   | -     |
| Confirm removing `write` permissions but still having read permissions disallows saving that section of the form                                        |       |    ?   |    ?    |   ?  | ?   | -     |

* * *

## Reports

Assigned to: Cyrus

#### Headers Rendering

| Test Subject                                                            | Chrome | Safari | Firefox | IE11 | UI  | Notes |
| ----------------------------------------------------------------------- | :----: | :----: | :-----: | :--: | --- | ----- |
| Confirm that report templates with map header gets rendered correctly   |:white_check_mark:|    ?   |    ?    |   ?  | ?   | -     |
| Confirm that report templates with image header gets rendered correctly |:white_check_mark:|    ?   |    ?    |   ?  | ?   | -     |
| Confirm that report templates with no header gets rendered correctly    |:white_check_mark:|    ?   |    ?    |   ?  | ?   | #4613 |

#### Data Rendering

| Test Subject           | Chrome | Safari | Firefox | IE11 | UI  | Notes |
| ---------------------- | :----: | :----: | :-----: | :--: | --- | ----- |
| String                 |:white_check_mark:|    ?   |    ?    |   ?  | ?   | -     |
| Concepts               |:white_check_mark:|    ?   |    ?    |   ?  | ?   | -     |
| Domains                |:white_check_mark:|    ?   |    ?    |   ?  | ?   | -     |
| Images                 |:white_check_mark:|    ?   |    ?    |   ?  | ?   | -     |
| Dates                  |:white_check_mark:|    ?   |    ?    |   ?  | ?   | -     |
| Number                 |:white_check_mark:|    ?   |    ?    |   ?  | ?   | -     |
| Boolean                |:white_check_mark:|    ?   |    ?    |   ?  | ?   | -     |
| Resource instance type |:white_check_mark:|    ?   |    ?    |   ?  | ?   | -     |
| Node data type         |:white_check_mark:|    ?   |    ?    |   ?  | ?   | -     |

* * *

## RDM

Assigned to: Namjun

#### Thesauri

| Test Subject       | Chrome | Safari | Firefox | IE11 | UI  | Notes |
| ------------------ | :----: | :----: | :-----: | :--: | --- | ----- |
| Add scheme         ||    ?   |    ?    |   ?  | ?   | -     |
| Delete scheme      ||    ?   |    ?    |   ?  | ?   | -     |
| Import scheme      ||    ?   |    ?    |   ?  | ?   | -     |
| Export scheme      ||    ?   |    ?    |   ?  | ?   | -     |
| Add top concept    ||    ?   |    ?    |   ?  | ?   | -     |
| Import from SPARQL ||    ?   |    ?    |   ?  | ?   |The list is not refreshed on import|
| Manage parents     ||    ?   |    ?    |   ?  | ?   |When polyhierachy is set, the selection not deactivated |
| Make collection    ||    ?   |    ?    |   ?  | ?   |If a user creates two collections with the same name they will not be able to delete either of them|
| Add label          ||    ?   |    ?    |   ?  | ?   | -     |
| Add Note           ||    ?   |    ?    |   ?  | ?   | -     |
| Add image          ||    ?   |    ?    |   ?  | ?   | -     |

#### Collections

| Test Subject                           | Chrome | Safari | Firefox | IE11 | UI  | Notes |
| -------------------------------------- | :----: | :----: | :-----: | :--: | --- | ----- |
| Add collection                         ||    ?   |    ?    |   ?  | ?   | -     |
| Delete collection                      ||    ?   |    ?    |   ?  | ?   | -     |
| Export all collections                 ||    ?   |    ?    |   ?  | ?   | -     |
| Add dropdown entry                     ||    ?   |    ?    |   ?  | ?   | -     |
| Add sort order and confirm in dropdown ||    ?   |    ?    |   ?  | ?   |In some cases custom sorting reverts to alphabetical order|

* * *
