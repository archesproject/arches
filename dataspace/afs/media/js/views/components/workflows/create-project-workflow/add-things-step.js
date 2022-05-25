define([
    'jquery',
    'underscore',
    'knockout',
    'knockout-mapping',
    'uuid',
    'arches',
    'bindings/select2-query',
    'views/components/search/paging-filter',
], function($, _, ko, koMapping, uuid, arches) {
    var collectionNameNodegroupId = '52aa1673-c450-11e9-8640-a4d18cec433a'; // Name (E33) in Collection resource
    var activityUsedSetNodeId = 'cc5d6df3-d477-11e9-9f59-a4d18cec433a'; //Used Set in Project
    var activityNameNodeId = "0b92cf5c-ca85-11e9-95b1-a4d18cec433a"; // Name_content in Project resource

    var getQueryObject = function() {
        var query = _.chain(decodeURIComponent(location.search).slice(1).split('&'))
            // Split each array item into [key, value]
            // ignore empty string if search is empty
            .map(function(item) {
                if (item) return item.split('=');
            })
            // Remove undefined in the case the search is empty
            .compact()
            // Turn [key, value] arrays into object parameters
            .object()
            // Return the value of the chain operation
            .value();
        return query;
    };
    
    function viewModel(params) {
        var self = this;

        _.extend(this, params.form);

        var limit = 7;
        this.projectResourceId = ko.observable();
        this.collectionResourceId = ko.observable();
        this.collectionTileId = ko.observable();
        this.usedSetTileId = ko.observable();
        this.reportDataLoading = ko.observable(params.loading());
        let projectName;

        if (params.projectStepData){
            const projectStepData = params.projectStepData;
            projectName = projectStepData.name.value;
            this.projectResourceId(projectStepData.projectResourceId);    
        } else if (params.resourceid){
            this.projectResourceId(params.resourceid);
        }

        this.selectedTab = ko.observable();
        this.searchResults = {'timestamp': ko.observable()};
        this.targetResource = ko.observable();
        this.toggleRelationshipCandidacy = ko.observable();
        this.isResourceRelatable = ko.observable();
        this.filters = {
            'paging-filter': ko.observable(),
            'search-results': ko.observable(),
        };
        this.termFilter = ko.observable();
        this.totalResults = ko.observable();
        this.query = ko.observable(getQueryObject());
        this.selectedTerm = ko.observable();
        this.targetResources = ko.observableArray([]);
        this.targetResourceSearchValue = ko.observable();
        this.termOptions = [];
        this.value = ko.observableArray([]).extend({
            rateLimit: 100
        });
        this.startValue = ko.observableArray();
        this.selectedResources = ko.observableArray([]);
        this.addedValues = ko.observableArray();
        this.removedValues = ko.observableArray();

        this.dirty = ko.pureComputed(function() {
            if (self.startValue() && self.value()){
                return !!(self.startValue().find(x => !self.value().includes(x))
                    || self.value().find(x => !self.startValue().includes(x)));
            } else {
                return false;
            }
        });
        this.dirty.subscribe(function(dirty) {
            params.dirty(dirty);
        });

        this.value.subscribe(function(a) {
            a.forEach(function(action) {
                if (action.status === 'added') {
                    $.ajax({
                        url: arches.urls.api_resources(ko.unwrap(action.value)),
                        data: {
                            format: 'json',
                            includetiles: 'false'
                        }
                    }).done(function(data) {
                        self.selectedResources.push(data);
                    });
                } else if (action.status === 'deleted') {
                    self.selectedResources().forEach(function(val) {
                        if (val.resourceinstanceid === ko.unwrap(action.value)) {
                            self.selectedResources.remove(val);
                        }
                    });
                }
            });
        }, null, "arrayChange");

        const loadExistingCollection = async function(){
            const projectRelatedResources = await (await window.fetch(`${arches.urls.related_resources}${self.projectResourceId()}`)).json();
            self.collectionResourceId(projectRelatedResources.related_resources.related_resources.find(x=>x.graph_id==="1b210ef3-b25c-11e9-a037-a4d18cec433a").resourceinstanceid);

            const collectionRelatedResources = await (await window.fetch(`${arches.urls.related_resources}${self.collectionResourceId()}`)).json();
            const childPhysicalThingsValueIds = [
                '77d8cf19-ce9c-4e0a-bde1-9148d870e11c', //sample
                '7375a6fb-0bfb-4bcf-81a3-6180cdd26123', //sample location
                '31d97bdd-f10f-4a26-958c-69cb5ab69af1', //anlysis area
            ];

            self.startValue(
                collectionRelatedResources.related_resources.related_resources
                    .filter(rr =>
                        rr.graph_id === "9519cb4f-b25b-11e9-8c7b-a4d18cec433a"
                    )
                    .filter(rr =>
                        !rr.tiles.find(tile =>
                            tile.nodegroup_id === "8ddfe3ab-b31d-11e9-aff0-a4d18cec433a" &&
                            tile.data["8ddfe3ab-b31d-11e9-aff0-a4d18cec433a"].find(value =>
                                childPhysicalThingsValueIds.includes(value))
                        )
                    )
                    .map(rr => rr.resourceinstanceid)
            );

            self.startValue().forEach(function(val){
                self.value.push(val);
            });
        };

        this.initialize = function(){
            if (params.value()) {
                const cachedValue = ko.unwrap(params.value);
                if (cachedValue['collectionResourceId']){
                    self.collectionResourceId(cachedValue['collectionResourceId']);
                }
                if (cachedValue['collectionTileId']){
                    self.collectionTileId(cachedValue['collectionTileId']);
                }
                if (cachedValue['usedSetTileId']){
                    self.usedSetTileId(cachedValue['usedSetTileId']);
                }
                if (cachedValue["value"]){
                    self.startValue(ko.unwrap(cachedValue["value"]));
                    self.startValue().forEach(function(val){
                        self.value.push(val);
                    });
                }
            } else if (params.action === "update") {
                loadExistingCollection();
            }
        };

        this.resetTile = function() {
            if (self.startValue()) {
                self.value.removeAll();
                self.startValue().forEach(function(val){
                    self.value.push(val);
                });
            }
        };
        params.form.reset = this.resetTile;

        this.updateTileData = function(resourceid) {
            var val = self.value().find(function(item) {
                return ko.unwrap(item) === resourceid;
            });

            if (!!val) {
                // remove item, we don't want users to add the same item twice
                self.value.remove(val);
            } else {
                self.value.push(resourceid);
            }
        };

        this.addCollectionToPhysicalThings = () => {
            let resourcesToUpdate = [];
            self.addedValues(self.value().filter(val => !self.startValue().includes(val)));
            self.removedValues(self.startValue().filter(val => !self.value().includes(val)));

            self.addedValues().map(function(value){
                resourcesToUpdate.push({
                    resourceid: value,
                    action: 'add',
                });
            });

            self.removedValues().map(function(value){
                resourcesToUpdate.push({
                    resourceid: value,
                    action: 'remove',
                });
            });

            const memberOfSetNodegroupId = '63e49254-c444-11e9-afbe-a4d18cec433a';
            return $.ajax({
                url: arches.urls.root + 'updateresourcelist',
                type: 'POST',
                data: {
                    relatedresourceid : ko.unwrap(self.collectionResourceId),
                    nodegroupid : memberOfSetNodegroupId,
                    nodeid : memberOfSetNodegroupId,
                    transactionid : params.form.workflowId,
                    data: JSON.stringify(resourcesToUpdate)
                }
            });
        };

        this.submit = function() {
            self.complete(false);
            self.saving(true);
            if (params.action === "update") {
                self.addCollectionToPhysicalThings()
                    .then(() => {
                        params.form.lockExternalStep("select-project", true);
                    })
                    .fail((err) => {
                        // eslint-disable-next-line no-console
                        console.log(err);
                        const startValue = ko.unwrap(self.startValue);
                        self.value(startValue);
                    }).always(() => {
                        self.savedData(
                            {
                                value: ko.unwrap(self.value),
                                projectResourceId: ko.unwrap(self.projectResourceId),
                                collectionResourceId: ko.unwrap(self.collectionResourceId),
                                collectionTileId: ko.unwrap(self.collectionTileId), 
                            }
                        );
                        self.saving(false);
                        self.complete(true);
                    });
            } else {
                const nameTileData = {
                    "52aa1ade-c450-11e9-8326-a4d18cec433a": ["bc35776b-996f-4fc1-bd25-9f6432c1f349"], // English
                    "52aa1d0f-c450-11e9-aec4-a4d18cec433a": null,
                    "52aa1e1c-c450-11e9-91cc-a4d18cec433a": null,
                    "52aa1f17-c450-11e9-a114-a4d18cec433a": ["7d069762-bd96-44b8-afc8-4761389105c5"], // [primary title]
                    "52aa2007-c450-11e9-b5d4-a4d18cec433a": `Collection for ${projectName}`,
                };
    
                const nameTile = {
                    "tileid": ko.unwrap(self.collectionTileId) || "",
                    "nodegroup_id": collectionNameNodegroupId,
                    "parenttile_id": null,
                    "resourceinstance_id": ko.unwrap(self.collectionResourceId),
                    "sortorder": 0,
                    "tiles": {},
                    "data": nameTileData,
                    "transaction_id": params.form.workflowId
                };
    
                window.fetch(arches.urls.api_tiles(ko.unwrap(self.collectionTileId) || uuid.generate()), {
                    method: 'POST',
                    credentials: 'include',
                    body: JSON.stringify(nameTile),
                    headers: {
                        'Content-Type': 'application/json'
                    },
                }).then(function(response) {
                    if (response.ok) {
                        return response.json();
                    }
                }).then(function(data) {
                    self.collectionResourceId(data.resourceinstance_id);
                    self.collectionTileId(data.tileid);
    
                    createActivityUsedSet()
                        .done(data => {
                            self.usedSetTileId(data.tileid);
                            self.addCollectionToPhysicalThings()
                                .fail((err) => {
                                    // eslint-disable-next-line no-console
                                    console.log(err);
                                    const startValue = ko.unwrap(self.startValue);
                                    self.value(startValue);
                                }).always(() => {
                                    self.savedData(
                                        {
                                            value: ko.unwrap(self.value),
                                            projectResourceId: ko.unwrap(self.projectResourceId),
                                            collectionResourceId: ko.unwrap(self.collectionResourceId),
                                            collectionTileId: ko.unwrap(self.collectionTileId), 
                                            usedSetTileId: ko.unwrap(self.usedSetTileId),
                                        }
                                    );
                                    self.saving(false);
                                    self.complete(true);
                                });
                        });
                });    
            }
        };

        params.form.save = self.submit;
        params.form.onSaveSuccess = function() {};

        const createActivityUsedSet = () => {
            const activityUsedSetToCreate = 
                $.ajax({
                    url: arches.urls.api_node_value,
                    type: 'POST',
                    dataType: 'json',
                    data: {
                        'nodeid': activityUsedSetNodeId, // used_set (of Activity)
                        'data': JSON.stringify(
                            [{
                                'resourceId': ko.unwrap(self.collectionResourceId),
                                'ontologyProperty': '',
                                'inverseOntologyProperty':'',
                                'resourceXresourceId':''
                            }]
                        ), 
                        'tileid': ko.unwrap(self.usedSetTileId),
                        'resourceinstanceid': ko.unwrap(self.projectResourceId)
                    }
                });
            return activityUsedSetToCreate;
        };

        this.targetResourceSelectConfig = {
            value: self.selectedTerm,
            minimumInputLength: 2,
            placeholder: 'find a physical thing: enter an artist, object name, artwork title or object number',
            clickBubble: true,
            multiple: false,
            closeOnSlect: false,
            allowClear: true,
            ajax: {
                url: arches.urls.search_terms,
                dataType: 'json',
                quietMillis: 250,
                data: function(term, page) {
                    var data = {
                        start: (page - 1) * limit,
                        // eslint-disable-next-line camelcase
                        page_limit: limit,
                        q: term
                    };
                    return data;
                },
                results: function(data, page) {
                    const value = window.document.getElementsByClassName('select2-input')[0].value;
                    const results = data.terms;
                    results.unshift({
                        type: 'string',
                        context: '',
                        context_label: 'Search Term',
                        id: value,
                        text: value,
                        value: value
                    });
                    self.termOptions = results;

                    const filteredResults = results.filter(function(result){
                        return (result.context_label.includes("Physical Thing") || result.context_label.includes("Search Term")) && 
                            !(result.text.includes("[Sample") || result.text.includes("[Analysis") || result.text.includes("[Region"));
                    });
                    return {
                        results: filteredResults,
                        more: data.count >= (page * limit)
                    };
                }
            },
            id: function(item) {
                return item.id;
            },
            formatResult: function(item) {
                if (item.context_label === 'Search Term') {
                    return `<strong><u>${item.text}</u></strong>`;
                }
                return item.text;
            },
            formatSelection: function(item) {
                return item.text;
            },
            clear: function() {
                self.selectedTerm();
            },
            isEmpty: ko.computed(function() {
                return self.selectedTerm() === '' || !self.selectedTerm();
            }, this),
            initSelection: function() {
                return;
            }
        };
        
        var getResultData = function(termFilter, pagingFilter) {
            var filters = {};
            // let's empty our termFilters
            _.each(self.filters, function(_value, key) {
                if (key !== 'paging-filter' && key !== 'search-results') {
                    delete self.filters[key];
                }
            });

            const advancedSearchFilter = [
                {
                    "op":"and",
                    "8ddfe3ab-b31d-11e9-aff0-a4d18cec433a":{
                        "op":"!",
                        "val":"31d97bdd-f10f-4a26-958c-69cb5ab69af1"
                    }
                },
                {
                    "op":"and",
                    "8ddfe3ab-b31d-11e9-aff0-a4d18cec433a":{
                        "op":"!",
                        "val":"7375a6fb-0bfb-4bcf-81a3-6180cdd26123"
                    }
                },
                {
                    "op":"and",
                    "8ddfe3ab-b31d-11e9-aff0-a4d18cec433a":{
                        "op":"!",
                        "val":"77d8cf19-ce9c-4e0a-bde1-9148d870e11c"
                    }
                },
                {
                    "op":"or",
                    "8ddfe3ab-b31d-11e9-aff0-a4d18cec433a":{
                        "op":"null",
                        "val":""
                    }
                }
            ];
            filters["advanced-search"] = JSON.stringify(advancedSearchFilter);

            if (termFilter) {
                termFilter['inverted'] = false;
                filters["term-filter"] = JSON.stringify([termFilter]);
            } 

            if (pagingFilter) {
                filters['paging-filter'] = pagingFilter;
                self.filters['paging-filter'](pagingFilter);
            } else {
                filters['paging-filter'] = 1;
            }

            self.reportDataLoading(true);

            const setUpReports = function() {
                const filterParams = Object.entries(filters).map(([key, val]) => `${key}=${val}`).join('&');
                fetch(arches.urls.physical_thing_search_results + '?' + filterParams)
                    .then(response => response.json())
                    .then(data => {
                        _.each(self.searchResults, function(_value, key) {
                            if (key !== 'timestamp') {
                                delete self.searchResults[key];
                            }
                        });
                        _.each(data, function(value, key) {
                            if (key !== 'timestamp') {
                                self.searchResults[key] = value;
                            }
                        });
                        self.searchResults.timestamp(data.timestamp);
        
                        self.totalResults(data['total_results']);
                        var resources = data['results']['hits']['hits'].map(source => {
                            source._source.tiles.forEach((tile) => {
                                if (tile.data['22c15cfa-b498-11e9-b5e3-a4d18cec433a'] && 
                                    tile.data['22c15cfa-b498-11e9-b5e3-a4d18cec433a'].length &&
                                    tile.data['22c15cfa-b498-11e9-b5e3-a4d18cec433a'][0] === '26094e9c-2702-4963-adee-19ad118f0f5a') {
                                    source.identifier = tile.data['22c169b5-b498-11e9-bdad-a4d18cec433a'];
                                }
                            });
                            return source;
                        });
                        self.targetResources(resources);
                        self.reportDataLoading(false);
                    });
            };
            setUpReports();
        };

        this.updateSearchResults = function(termFilter, pagingFilter) {
            getResultData(termFilter, pagingFilter);
        };

        this.selectedTerm.subscribe(function(val) {
            self.termFilter(self.termOptions.find(x => val == x.id));
            self.updateSearchResults(self.termFilter());
        });

        this.query.subscribe(function(query) {
            self.updateSearchResults(self.termFilter(), query['paging-filter']);
        });

        this.initialize();
    }

    ko.components.register('add-things-step', {
        viewModel: viewModel,
        template: {
            require: 'text!templates/views/components/workflows/create-project-workflow/add-things-step.htm'
        }
    });

    return viewModel;
});
