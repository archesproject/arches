### Arches 4.3.0 release notes

The Arches team has been busy improving Arches and fixing several bugs as well.
Below you'll find a listing of all the changes that are included in the latest release.

Some of the highlights:
- The Graph Manager has been redesigned to support the lifting of the graph depth constraint
- The Card Manager, Permission Manager, and Report Manager pages have been integrated into the new graph designer
- Branch depth is no longer restricted
- Adds ability to append a branch to any node in a resource model
- Individual nodes can be added to Resource Models
- The Resource Editor has also been redesigned to support the new graph capabilities
- Branches can be exported from Resource Models
- Cards have adapted as knockout components, allowing developers to create their own custom cards
- Lifting the graph depth constraint allows cards to serve the role of 'Menus'. Menus are therefore deprecated
- Package settings now allow packages to have tailored settings
- The main navigation panel now expands revealing more navigation details
- Provisional users can now view the status of their edits
- API endpoints have been added for concepts, resource instances with JSON-LD context support

#### Known Issues

- [#3993](https://github.com/archesproject/arches/issues/3993) - During graph creation (adding several nodes in a single session) the browser may crash or hang.  This is because the Knockout.js Mapping package that Arches uses consumes an unnecessarily large amount of memory.  

  **Workaround:** During heavy graph development users can periodically refresh the browser to reclaim memory and reduce the occurrence of browser issues.

- [#4044](https://github.com/archesproject/arches/issues/4044) - Exporting data that uses the File-list datatype in csv format can't be successfully re-imported.  
  
  **Workaround:** If users need to export data that uses the File-list datatype, then they should export in JSON format instead, so that data can be successfully re-imported.
  
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
```

If you have Arches running on a web server such as Apache, be sure to update your static files directory and restart your web server.

As always the documentation can be found at http://arches.readthedocs.io

#### Upgrading an Arches project

If you are upgrading your project from 4.1.1, you should review the project [upgrade steps from 4.1.1 to 4.2](https://github.com/archesproject/arches/blob/master/releases/4.2.0.md#upgrading-arches) before proceeding.

If you have made no changes to the package.json file in your project you can run :

1. In a terminal cd to your project directory and run the following command::

        python manage.py updateproject

    This command adds the `package.json` and `.yarnrc` files to your project and then runs `yarn install`.

2. If you have made changes to `package.json`, then you should update your javascript dependencies manually:

    ```
    cd into your project's root directory (where yarn.lock is located) and run the following:
    yarn add core-js@2.5.7
    yarn add dom4@2.0.1
    yarn install
    yarn upgrade mapbox-gl@0.48.0
    yarn upgrade underscore@1.9.1
    ```

#### Changes

    - add new management command that finds a uuid in your db and tells you about it
    - Fix issue with importing dates from shapefile with new date_import_export_format setting,re # 3230
    - Loads a package settings file #3377
    - Exports package settings when updating or creating a package re # 3377
    - applies permissions in new editor, re: #3210
    - supports new instances in new editor, re: #3210
    - fix issue with setting the user to anonymous and oauth authentication,re # 3311
    - adds support for expanded nav, re: #3222 ...via click on main icon
    - better defaults for fit buffer and max zoom
    - Applies hover and click filters to overlay features. re # 3375
    - Shows provisional flag in search to reviewers only. re # 3473
    - Add ability to append a branch to any node in a resource model. re # 3397
    - Prevents provisional users from seeing the provisional edits of other users. re # 3385
    - add oauth tests,re # 3311
    - push headers prefixed with X_ARCHES_ to the request.GET dict,re # 3309
    - add unit test for api, re # 3309
    - Remove references to protected graphs,re # 3443
    - validate that a proper json-ld context is used,re # 3313
    - allow users to supply a URI that points to JSON-LD context object, or the actual context object itself,re # 3313
    - working version of a paging api to get a list of resource instance ids, #3313
    - enable permissions on all output formats so that the api can filter tiles based on the request.user,re # 3313
    - Add API endpoint for single concept retrieval RE: #3399
    - Adjust get inputs to allow for passing of Headers RE: #3399
    - Adjust variables to match similar classes in the api RE: #3399
    - Add Method Decorator for API retreival of concepts RE: #3399
    - integrate permissions into PUT endpoint, re #3313
    - Update Docker entrypoint.sh to utilize the set PGUSERNAME [ci skip]
    - Adds alert when saving graph settings fails. re #3199
    - Make 'Create a New Account' link open in a new tab, re #2739
    - Fixes issue with provisional edits getting overwritten by other users. re #3385
    - Changes provisionaledits in postgres from json string to true json. re #3385
    - improve map source deletion and error handling
    - Graph Manager: Add Graph Switcher RE: #3553
    - Style improvements of provisional edit list.re #3385
    - Allow filter box and expand/collapse button to remain in header while scrolling graph tree, re #3436
    - Migrates editor tree to card components, re: #3205
    - Add dictionary equality to json export test, fix error with null concept-list values in json import, re #3455
    - Implement verbose errors for Graph Validation issues #3554
    - Summarizes a provisional user's edit history, re #3385
    - Moves provisional edit panel into card component. re #3385
    - Moves color input above icon selector and pins color picker to the bottom of the color input when scrolling. re #3199
    - Add progress bar to deleting all the instances of a resource model #3574
    - Allow progress bar in deleting all instances of a Resource model #3574
    - Add CLI option to remove all instances related to a Resource model #3574
    - Remove restrictions on appending graphs to non-resource nodes,re #3397
    - Set Splash to only show when no Related Resources are set #3605
    - Allows users to enter a search url into the resource-instance search widget. re #3607
    - Makes the provisional edit history filterable and sortable by date. Adds the instance display name to each edit and adds the reviewer status if a reviewer approves an edit by directly saving the card.re #3385
    - Allow deletion of an invalid graph,re #3725
    - Add Delete ability for Resource API Endpoint #3709
    - Records provisional edit data when a reviewer deletes a fully provisional tile.re #3385
    - Removes edit link in provisional edit history if the resource has been deleted (prevents error when user navigates to the edit page of a deleted resource)re #3385
    - Records reviewer when saving a deletion to the edit log.re #3385
    - Gracefully notifies a user if they try to edit or delete a tile that has already been deleted that it does not exist in the system.re #3385
    - Adds card components to reports, re: #3757
    - Removes deprecated graph manager, updates test to work with the designer view.re #3601
    - Removes Form/Menu views and models on front end, server and import commands.re #3601
    - Removes "forms" mode from management command. re #3601
    - Removes references to forms in report and graph modelsre #3601
    - Add UUID_REGEX setting to settings.py, re #3706
    - Add error handling into JSONldReader, re #3706
    - Make sure we serialize and deserialize tile data properly for JSONld support, re #3706
    - Adds new report manager interface, re: #3724

- Several dependencies were updated including (but not limited to):
    - upgrades TileStache and mapboxgl
    - Bump django from 1.11.10 to 1.11.14 in /arches/install
    - Bump sparqlwrapper from 1.8.0 to 1.8.2 in /arches/install
    - Updates django-revproxy to 0.9.15
    - Bump underscore from 1.8.3 to 1.9.1
    - Updates django-revproxy to 0.9.15
    - Bump underscore from 1.8.3 to 1.9.1
    - Remove pycrypto #3704

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
| Test that users can't access the Mobile Survey Manager page                               |:white_check_mark:|    ?   |    ?    |   ?  |  ?  |  -    |

* * *

## Authentication

Assigned to: Alexei (.5)

Ensure that all browsers are compatible with Authentication process.

| Test Subject                                                             | Chrome | Safari | Firefox | IE11 | UI  | Notes |
| ------------------------------------------------------------------------ | :----: | :----: | :-----: | :--: | --- | ----- |
| User can sign themselves up for a new Arches account                     |:white_check_mark:|    ?   |    ?    |   ?  | ?   | -     |
| User is added to default group (Crowdsource Editor)                      |:white_check_mark:|    ?   |    ?    |   ?  | ?   | -     |
| User can log in with their email address                                 |:white_check_mark:|    ?   |    ?    |   ?  | ?   | -     |
| User can reset their password                                            |:white_check_mark:|    ?   |    ?    |   ?  | ?   | -     |
| User can edit their profile (First and Last name, email address, etc...) |:white_check_mark:|    ?   |    ?    |   ?  | ?   | -     |

* * *

## System Settings

Assigned to: Cyrus (0.25)

#### Basic Settings

| Test Subject                                                                                                                 | Chrome | Safari | Firefox | IE11 | UI  | Notes |
| ---------------------------------------------------------------------------------------------------------------------------- | :----: | :----: | :-----: | :--: | --- | ----- |
| Project Name - Updating name updates and the page tab                                                                        |:white_check_mark:|    ?   |    ?    |   ?  |  ?  | -     |
| Web Analytics - String value inserts in base.htm at the location of this template variable:{{GOOGLE_ANALYTICS_TRACKING_ID}}  |:white_check_mark:|    ?   |    ?    |   ?  |  ?  | -     |

#### Map Settings

Assigned to: Cyrus (1.0)

| Test Subject                                                                                                                                                                                    | Chrome | Safari | Firefox | IE11 | UI  | Notes |
| ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :----: | :----: | :-----: | :--: | --- | ----- |
| API Key - Key saves and API calls are successful                                                                                                                                                |:white_check_mark:|    ?   |    ?    |   ?  | ?   | -     |
| Hex Grid Precision - Saves properly, but errors if precision is too high (\`Exception detail: TransportError(400, u'parsing_exception', u'[geohash_grid] failed to parse field [precision]')``) |:white_check_mark:|    ?   |    ?    |   ?  | ?   | -     |
| Hex Cell Size - Changes reflected in Search results                                                                                                                                             |:white_check_mark:|    ?   |    ?    |   ?  | ?   | -     |
| Default Zoom  Changes reflected in Card Config Manager                                                                                                                                          |:white_check_mark:|    ?   |    ?    |   ?  | ?   | -     |
| Min Zoom  Changes reflected in Card Config Manager                                                                                                                                              |:white_check_mark:|    ?   |    ?    |   ?  | ?   | -     |
| Max Zoom  Changes reflected in Card Config Manager                                                                                                                                              |:white_check_mark:|    ?   |    ?    |   ?  | ?   | -     |
| Project Extent - Changes reflected in Card Config Manager                                                                                                                                       |:white_check_mark:|    ?   |    ?    |   ?  | ?   | -     |

#### Search Settings

Assigned to: Cyrus (0.25)

Basic Search Settings

| Test Subject                                                   | Chrome | Safari | Firefox | IE11 | UI  | Notes |
| -------------------------------------------------------------- | :----: | :----: | :-----: | :--: | --- | ----- |
| Searches per page updates properly in Search                   |:white_check_mark:|    ?   |    ?    |   ?  | ?   | -     |
| Number of search suggestions is reflected in search term input |:white_check_mark:|    ?   |    ?    |   ?  | ?   | -     |

Saved Searches

| Test Subject                                                                                                       | Chrome | Safari | Firefox | IE11 | UI  | Notes |
| ------------------------------------------------------------------------------------------------------------------ | :----: | :----: | :-----: | :--: | --- | ----- |
| A new search saves with a name, search url, description, and image and displays properly in the saved search page. |:white_check_mark:|    ?   |    ?    |   ?  | ?   | -     |
| Users can delete a saved search                                                                                    |:white_check_mark:|    ?   |    ?    |   ?  | ?   | -     |

* * *

## Map Widget

Assigned to: Cyrus (0.5)

Test in the Card Configuration Manager.

| Test Subject                                                                                                                                            | Chrome | Safari | Firefox | IE11 | UI  | Notes |
| ------------------------------------------------------------------------------------------------------------------------------------------------------- | :----: | :----: | :-----: | :--: | --- | ----- |
| Point line and poly geoms can be created, edited, and deleted                                                                                           |:white_check_mark:|    ?   |    ?    |   ?  | ?   | #3898 |
| XY widget is working properly                                                                                                                           |:white_check_mark:|    ?   |    ?    |   ?  | ?   | -     |
| Valid geojson entered in the geojson input adds features to the map and pans to those features. If geojson is invalid user has a chance to update data. |:white_check_mark:|    ?   |    ?    |   ?  | ?   | -     |
| Widget configs (maxzoom, tilt, etc) update when the map changes and the map changes when the properties change                                          |:white_check_mark:|    ?   |    ?    |   ?  | ?   | -     |

* * *

## Map Layer Manager

Assigned to: Rob

#### Resource Layers

Assigned to: Rob

| Test Subject                                                                                                                         | Chrome | Safari | Firefox | IE11 | UI  | Notes |
| ------------------------------------------------------------------------------------------------------------------------------------ | :----: | :----: | :-----: | :--: | --- | ----- |
| Settings - changes to the name and icon of a layer are reflected in the map widget overlay list and overlay library                  |    :white_check_mark:   |    ?   |    ?    |   ?  | ?   | -     |
| Deactivating/Activating a resource layer hides/shows the layer in the map widget overlay list and overlay library                    |    :white_check_mark:   |    ?   |    ?    |   ?  | ?   | -     |
| Style Settings - changes to the layer style are displayed in the layer                                                               |    :white_check_mark:   |    ?   |    ?    |   ?  | ?   | -     |
| Style Settings Advanced - changes to the layer style are displayed in the layer                                                      |    :white_check_mark:   |    ?   |    ?    |   ?  | ?   | -     |
| Activating caching adds a cache folder for a resource in your projects tileserver directory                                          |    :white_check_mark:   |    ?   |    ?    |   ?  | ?   | -     |
| Activating clean cache on edit updates the cache when a geometry is edited                                                           |    :white_check_mark:   |    ?   |    ?    |   ?  | ?   | -     |
| Setting permissions for a user or group as No Access removes the user and group from the permissions list under the permissions tab. |    :white_check_mark:   |    ?   |    ?    |   ?  | ?   | -     |

#### Clustering (Resource Layers)

Assigned to: Rob

| Test Subject                                                                               | Chrome | Safari | Firefox | IE11 | UI  | Notes |
| ------------------------------------------------------------------------------------------ | :----: | :----: | :-----: | :--: | --- | ----- |
| Increasing cluster distance causes features to cluster at increased distances between them |    :white_check_mark:   |    ?   |    ?    |   ?  | ?   | -     |
| Increasing cluster max zoom causes clusters to be formed at higher zoom levels             |    :white_check_mark:   |    ?   |    ?    |   ?  | ?   | -     |
| Decreasing min points to 2 points causes clusters to form with only 2 points               |    :white_check_mark:   |    ?   |    ?    |   ?  | ?   | -     |
| Increasing vector simplification to 0.0 prevents simplification a low zoom levels          |    :white_check_mark:   |    ?   |    ?    |   ?  | ?   | -     |

#### Basemaps

Assigned to: Rob

| Test Subject                                                                                    | Chrome | Safari | Firefox | IE11 | UI  | Notes |
| ----------------------------------------------------------------------------------------------- | :----: | :----: | :-----: | :--: | --- | ----- |
| Changing the default search basemap in the basemap settings is reflected on the search page     |    :white_check_mark:   |    ?   |    ?    |   ?  | ?   | -     |
| Settings - changes to the name and icon of a layer are reflected in the map widget basemap list |    :white_check_mark:   |    ?   |    ?    |   ?  | ?   | -     |
| User can delete a basemap and it no longer appears in the map widget's list of basemaps         |    :white_check_mark:   |    ?   |    ?    |   ?  | ?   | -     |

#### Overlays

Assigned to: Rob

| Test Subject                                                                                                        | Chrome | Safari | Firefox | IE11 | UI  | Notes |
| ------------------------------------------------------------------------------------------------------------------- | :----: | :----: | :-----: | :--: | --- | ----- |
| Settings - changes to the name and icon of a layer are reflected in the map widget overlay list and overlay library |    :white_check_mark:   |    ?   |    ?    |   ?  | ?   | -     |
| User can delete an overlay and it no longer appears in the map widget overlay library                               |    :white_check_mark:   |    ?   |    ?    |   ?  | ?   | -     |
| Overlays support custom popups                                                                                      |    :white_check_mark:   |    ?   |    ?    |   ?  | ?   | -     |
* * *

## Import/Export

Assigned to: Ryan (0.5)

| Test Subject               | Chrome | Safari | Firefox | IE11 | UI  | Notes |
| -------------------------- | :----: | :----: | :-----: | :--: | --- | ----- |
| Create_mapping_file        |    :white_check_mark:   |    ?   |    ?    |   ?  | ?   | -     |
| Import business data (cli) |    ?   |    ?   |    ?    |   ?  | ?   | #4044     |
| Export business data (cli) |    :white_check_mark:   |    ?   |    ?    |   ?  | ?   | -     |
| Load package (cli)         |    :white_check_mark:   |    ?   |    ?    |   ?  | ?   | -     |
| Create package (cli)       |    ?   |    ?   |    ?    |   ?  | ?   | #4042     |

* * *

## Resource Instance Management

Assigned to: Adam

#### Data Types

Confirm that the user is able to edit the following data types. Use the Test model to quickly test all ten data types.
Note (GeoJson is covered by map widget testing in a different section)

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

#### Resource Descriptors

Assigned to: Adam

Updating a resource descriptor should be reflected in the following subjects.

| Test Subject                                                                                        | Chrome | Safari | Firefox | IE11 | UI  | Notes |
| --------------------------------------------------------------------------------------------------- | :----: | :----: | :-----: | :--: | --- | ----- |
| Search results                                                                                      |:white_check_mark:|    ?   |    ?    |   ?  | ?   | -     |
| Form headings                                                                                       |:white_check_mark:|    ?   |    ?    |   ?  | ?   | -     |
| Report headings                                                                                     |:white_check_mark:|    ?   |    ?    |   ?  | ?   | -     |
| Map popups                                                                                          |:white_check_mark:|    ?   |    ?    |   ?  | ?   | -     |
| Related resource d3 graph and listings                                                              |:white_check_mark:|    ?   |    ?    |   ?  | ?   | -     |

* * *

#### Provisional Edit Management

Assigned to: Cyrus (0.5)

| Test Subject                                                                                        | Chrome | Safari | Firefox | IE11 | UI  | Notes |
| --------------------------------------------------------------------------------------------------- | :----: | :----: | :-----: | :--: | --- | ----- |
| Provisional users see indication in a widget that their tile edits were submitted                   |:white_check_mark:|    ?   |    ?    |   ?  | ?   | -     |
| Resource reviewers are able to identify provisional tiles and can approve/discard provisional edits |:white_check_mark:|    ?   |    ?    |   ?  | ?   | -     |
| Provisional edit history properly shows the status of a tile: pending, approved, or declined        |:white_check_mark:|    ?   |    ?    |   ?  | ?   | -     |
| Reviewer can switch between edits of 2 or more provisional users in a partially provisional tile    |:white_check_mark:|    ?   |    ?    |   ?  | ?   | -     |
| Provisional edits display in editor report for provisional users.                                   |:white_check_mark:|    ?   |    ?    |   ?  | ?   | -     |
| No provisional data appears in reviewer or report page report.                                      |:white_check_mark:|    ?   |    ?    |   ?  | ?   | -     |

* * *

## Related Resources

Assigned to: Jeff

#### Resource Editor

| Test Subject                                           | Chrome | Safari | Firefox | IE11 | UI  | Notes |
| ------------------------------------------------------ | :----: | :----: | :-----: | :--: | --- | ----- |
| User can add a related resource                        |    :white_check_mark:   |    ?   |    ?    |   ?  | ?   | -     |
| User can delete a related resource                     |    :white_check_mark:   |    ?   |    ?    |   ?  | ?   | -     |
| User can change the properties of related resources    |    :x:   |    ?   |    ?    |   ?  | ?   | [#4040](https://github.com/archesproject/arches/issues/4040)     |
| User can switch between table and force directed graph |    :white_check_mark:   |    ?   |    ?    |   ?  | ?   | -     |
| User can page through related resources in table       |    :white_check_mark:   |    ?   |    ?    |   ?  | ?   | -     |

#### Resource Search (.5)

| Test Subject                                                                                                                           | Chrome | Safari | Firefox | IE11 | UI  | Notes |
| -------------------------------------------------------------------------------------------------------------------------------------- | :----: | :----: | :-----: | :--: | --- | ----- |
| Hovering over a link in the force directed graph opens a panel with source and target node info and list each unique relationship type |    :white_check_mark:   |    ?   |    ?    |   ?  | ?   | -     |
| Hovering over a node highlights the adjacent links and the corresponding entry in the node list                                        |    :white_check_mark:   |    ?   |    ?    |   ?  | ?   | -     |
| Hovering over a node list entry highlights the corresponding node and its adjacent links                                               |    :white_check_mark:   |    ?   |    ?    |   ?  | ?   | -     |
| User can switch between table and force directed graph                                                                                 |    :white_check_mark:   |    ?   |    ?    |   ?  | ?   | -     |
| Entering text in the search field filters the list of list entries                                                                     |    :white_check_mark:   |    ?   |    ?    |   ?  | ?   | -     |


* * *

## Search

Assigned to: Jeff (.5)

| Test Subject                                                                                                                                                                         | Chrome | Safari | Firefox | IE11 | UI  | Notes |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | :----: | :----: | :-----: | :--: | --- | ----- |
| Free text search                                                                                                                                                                     |    :white_check_mark:   |    ?   |    ?    |   ?  | ?   | -     |
| Concept search                                                                                                                                                                       |    :white_check_mark:   |    ?   |    ?    |   ?  | ?   | -     |
| Map search                                                                                                                                                                           |    :white_check_mark:   |    ?   |    ?    |   ?  | ?   | -     |
| Time range based search                                                                                                                                                              |    :white_check_mark:   |    ?   |    ?    |   ?  | ?   | -     |
| Time wheel search                                                                                                                                                                    |    :white_check_mark:   |    ?   |    ?    |   ?  | ?   | -     |
| Advanced search                                                                                                                                                                      |    :white_check_mark:   |    ?   |    ?    |   ?  | ?   | -     |
| Related resource graph list filter graph                                                                                                                                             |    :white_check_mark:   |    ?   |    ?    |   ?  | ?   | the d3 graph seems to not center very well     |
| Resource type search                                                                                                                                                                 |    :white_check_mark:   |    ?   |    ?    |   ?  | ?   | -     |
| Edit status search (provisional, authoritative, or both). Confirm that only resource reviewers are able to see provisional tile data                                                 |    :white_check_mark:   |    ?   |    ?    |   ?  | ?   | -     |
| Map should not zoom to points that a user is not permitted to read, nor should the search aggregation layer (e.g. hexbin or heatmap) indicate that a restricted resource is present. |    :white_check_mark:   |    ?   |    ?    |   ?  | ?   | -     |

* * *

Assigned to: Alexei (1.5)

## Graph/Resource Designer

| Test Subject     | Chrome | Safari | Firefox | IE11 | UI  | Notes |
| ---------------- | :----: | :----: | :-----: | :--: | --- | ----- |
| Export graph     |:white_check_mark:|    ?   |    ?    |   ?  | ?   | -     |
| Import graph     |:construction:|    ?   |    ?    |   ?  | ?   | #4043    |
| Create branch    |:x:|    ?   |    ?    |   ?  | ?   | #4050     |
| Create resource  |:white_check_mark:|    ?   |    ?    |   ?  | ?   | -     |
| Add/Edit cards   |:white_check_mark:|    ?   |    ?    |   ?  | ?   | #4034 |
| Add/Edit reports |:white_check_mark:|    ?   |    ?    |   ?  | ?   | -     |
| Edit functions   |:white_check_mark:|    ?   |    ?    |   ?  | ?   | -     |
| Delete graph     |:white_check_mark:|    ?   |    ?    |   ?  | ?   | -     |
| Clone graph      |:white_check_mark:|    ?   |    ?    |   ?  | ?   | -     |

* * *

## Permissions Management

Assigned to: Ryan (1)

| Test Subject                                                                                                                                            | Chrome | Safari | Firefox | IE11 | UI  | Notes |
| ------------------------------------------------------------------------------------------------------------------------------------------------------- | :----: | :----: | :-----: | :--: | --- | ----- |
| Confirm removing `read` permissions removes that section from the report                                                                                |    :white_check_mark:   |    ?   |    ?    |   ?  | ?   | -     |
| Confirm removing `read` permissions removes that section from the form                                                                                  |    :white_check_mark:   |    ?   |    ?    |   ?  | ?   | -     |
| Confirm removing `read` permissions removes that section from the adv. search                                                                           |    :white_check_mark:   |    ?   |    ?    |   ?  | ?   | -     |
| Confirm removing `read` permissions for a spatial nodegroup removes that resource type from map based search results                                    |    :white_check_mark:   |    ?   |    ?    |   ?  | ?   | -     |
| Confirm removing `read` permissions for a spatial nodegroup removes that resource type from the overlays section of the map settings                    |    :white_check_mark:   |    ?   |    ?    |   ?  | ?   | -     |
| Confirm removing `read` permissions for a spatial nodegroup removes the map from the Map Report                                                         |    :white_check_mark:   |    ?   |    ?    |   ?  | ?   | -     |
| Confirm removing `read` permissions for a date based nodegroup removes the related entries from the type dropdown in the time filter of the search page |    :white_check_mark:   |    ?   |    ?    |   ?  | ?   | -     |
| Confirm removing `read` permissions for a date based nodegroup reduces the wheel count appropriately                                                    |    :white_check_mark:   |    ?   |    ?    |   ?  | ?   | -     |
| Confirm removing `write` permissions but still having read permissions disallows saving that section of the form                                        |    :white_check_mark:   |    ?   |    ?    |   ?  | ?   | -     |

* * *

## Reports

Assigned to: Adam

#### Headers Rendering

| Test Subject                                                            | Chrome | Safari | Firefox | IE11 | UI  | Notes |
| ----------------------------------------------------------------------- | :----: | :----: | :-----: | :--: | --- | ----- |
| Confirm that report templates with map header gets rendered correctly   |    :white_check_mark:   |    ?   |    ?    |   ?  | ?   | -     |
| Confirm that report templates with image header gets rendered correctly |    :x:   |    ?   |    ?    |   ?  | ?   | #4035     |
| Confirm that report templates with no header gets rendered correctly    |    :white_check_mark:   |    ?   |    ?    |   ?  | ?   | -     |

#### Data Rendering

| Test Subject           | Chrome | Safari | Firefox | IE11 | UI  | Notes |
| ---------------------- | :----: | :----: | :-----: | :--: | --- | ----- |
| String                 |    :white_check_mark:   |    ?   |    ?    |   ?  | ?   | -     |
| Concepts               |    :white_check_mark:   |    ?   |    ?    |   ?  | ?   | -     |
| Domains                |    :white_check_mark:   |    ?   |    ?    |   ?  | ?   | -     |
| Images                 |   :white_check_mark:   |    ?   |    ?    |   ?  | ?   | -     |
| Dates                  |    :white_check_mark:   |    ?   |    ?    |   ?  | ?   | -     |
| Number                 |    :white_check_mark:   |    ?   |    ?    |   ?  | ?   | -     |
| Boolean                |    :white_check_mark:   |    ?   |    ?    |   ?  | ?   | -     |
| Resource instance type |    :white_check_mark:   |    ?   |    ?    |   ?  | ?   | -     |
| Node data type         |    :white_check_mark:   |    ?   |    ?    |   ?  | ?   | -     |

* * *

## RDM

Assigned to: Ryan (1)

#### Thesauri

| Test Subject       | Chrome | Safari | Firefox | IE11 | UI  | Notes |
| ------------------ | :----: | :----: | :-----: | :--: | --- | ----- |
| Add scheme         |    :white_check_mark:   |    ?   |    ?    |   ?  | ?   | -     |
| Delete scheme      |    :white_check_mark:   |    ?   |    ?    |   ?  | ?   | -     |
| Import scheme      |    :white_check_mark:   |    ?   |    ?    |   ?  | ?   | -     |
| Export scheme      |    :white_check_mark:   |    ?   |    ?    |   ?  | ?   | -     |
| Add top concept    |    :white_check_mark:   |    ?   |    ?    |   ?  | ?   | -     |
| Import from SPARQL |    ?   |    ?   |    ?    |   ?  | ?   | -     |
| Manage parents     |    :white_check_mark:   |    ?   |    ?    |   ?  | ?   | -     |
| Make collection    |    :white_check_mark:   |    ?   |    ?    |   ?  | ?   | -     |
| Add label          |    :white_check_mark:   |    ?   |    ?    |   ?  | ?   | -     |
| Add Note           |    :white_check_mark:   |    ?   |    ?    |   ?  | ?   | -     |
| Add image          |    :white_check_mark:   |    ?   |    ?    |   ?  | ?   | -     |

#### Collections

| Test Subject                           | Chrome | Safari | Firefox | IE11 | UI  | Notes |
| -------------------------------------- | :----: | :----: | :-----: | :--: | --- | ----- |
| Add collection                         |    :white_check_mark:   |    ?   |    ?    |   ?  | ?   | -     |
| Delete collection                      |    :white_check_mark:   |    ?   |    ?    |   ?  | ?   | -     |
| Export all collections                 |    :white_check_mark:   |    ?   |    ?    |   ?  | ?   | -     |
| Add dropdown entry                     |    :white_check_mark:   |    ?   |    ?    |   ?  | ?   | -     |
| Add sort order and confirm in dropdown |    :white_check_mark:   |    ?   |    ?    |   ?  | ?   | -     |

* * *
