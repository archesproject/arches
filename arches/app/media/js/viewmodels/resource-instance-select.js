define([
    'knockout',
    'underscore',
    'viewmodels/widget',
    'arches',
    'utils/ontology',
    'views/components/resource-report-abstract',
], function(ko, _, WidgetViewModel, arches, ontologyUtils) {
    var resourceLookup = {};
    var graphCache = {};
    require(['views/components/related-instance-creator']);
    
    /**
    * A viewmodel used for generic alert messages
    *
    * @constructor
    * @name ResourceInstanceSelectViewModel
    *
    * @param  {object} params
    * @param  {object} params.node (optional) - if supplied will assume that a node in an editor is being managed and will show 
    * the table of ontologyProperties below the dropdown otherwise the table will be hidden and you will have to populate params.graphids
    * @param  {boolean} params.graphids (optional) - if params.node is not supplied then you need to supply a list of graphids that can be used to get resource instances for the dropdown
    * @param  {boolean} params.multiple - whether to display multiple values in the dropdown/table
    * @param  {boolean} params.allowInstanceCreation - whether the dropdown will give the user the option to create a new resource instance
    * @param  {string} params.searchString (optional) - will limit the search results by the search string (it has to be full URL) and will override node.config.searchString if there is one
    * @param  {function} params.termFilter (optional) - a function to override the default term filter used when typing into the dropdown to search for resources
    * this.termFilter = function(term, data){
    *    return data["advanced-search"] = JSON.stringify([{
    *        "op": "and",
    *        "07e671ac-d069-11ea-bb31-acde48001122": {
    *            "op": "eq",
    *            "val": parseInt(term)
    *        }
    *    }]);
    * };
     */
    var ResourceInstanceSelectViewModel = function(params) {
        var self = this;
        this.graphLookup = graphCache;
        this.graphLookupKeys = ko.observable(Object.keys(this.graphLookup)); // used for informing the widget when to disable/enable the dropdown
        params.configKeys = ['placeholder', 'defaultResourceInstance'];
        this.preview = arches.graphs.length > 0;
        this.renderContext = params.renderContext;
        /* 
            shoehorn logic to piggyback off of search context functionality. 
            Should be refactored when we get the chance for better component clarity.
        */ 
        if (params.renderContext === 'workflow') {
            self.renderContext = 'search';
        }

        this.allowInstanceCreation = params.allowInstanceCreation === false ? false : true;
        if (self.renderContext === 'search') {
            this.allowInstanceCreation = params.allowInstanceCreation === true ? true : false;
        }
        if (!!params.configForm) {
            this.allowInstanceCreation = false;
        }

        this.multiple = params.multiple || false;
        this.value = params.value || undefined;
        this.selectedItem = params.selectedItem || ko.observable();
        this.rootOntologyClass = '';
        this.graphIsSemantic = false;
        this.resourceTypesToDisplayInDropDown = ko.observableArray(!!params.graphids ? ko.toJS(params.graphids) : []);
        this.displayOntologyTable = this.renderContext !== 'search' && !!params.node;
        this.graphIds = ko.observableArray();
        this.searchString = params.searchString || ko.unwrap(params.node?.config.searchString);

        this.waitingForGraphToDownload = ko.computed(function(){
            if (!!params.node && this.resourceTypesToDisplayInDropDown().length > 0){
                var found = this.resourceTypesToDisplayInDropDown().find(function(graphid){
                    return this.graphLookupKeys().includes(graphid);
                }, this);
                return !found;
            }
            return false;
        }, this);

        this.downloadGraph = function(graphid){
            if (graphid in self.graphLookup){
                return Promise.resolve(self.graphLookup[graphid]);
            } else {
                return window.fetch(`${arches.urls.graphs_api}${graphid}?cards=false&exclude=cards,domain_connections,edges,nodegroups,nodes,widgets`)
                    .then(function(response){
                        if (!response.ok) {
                            throw new Error(arches.translations.reNetworkReponseError);
                        }
                        return response.json();
                    })
                    .then(function(json){
                        self.graphLookup[graphid] = json.graph;
                        self.graphLookupKeys(Object.keys(self.graphLookup));
                        self.value.valueHasMutated();
                        return json.graph;
                    });
            }
        };

        // depending on where the widget is being rendered there are several ways to get the ontologyclass 
        if(!!params.node && params.state !== 'display_value'){
            if(!!params.node.graph && !!params.node.graph.get('root')){
                this.rootOntologyClass = params.node.graph.get('root').ontologyclass();
                this.graphIsSemantic = !!this.rootOntologyClass;
            } else {
                var graphid = params.node.graph_id || params.node.get('graph_id');
                self.downloadGraph(graphid)
                    .then(function(graph){
                        self.rootOntologyClass = graph.root.ontologyclass;
                        self.graphIsSemantic = !!self.rootOntologyClass;
                    });
            }
            if (params.state !== 'report') {
                ko.unwrap(params.node.config.graphs).forEach(function(graph){
                    self.downloadGraph(graph.graphid);
                }, this);
                this.resourceTypesToDisplayInDropDown(ko.unwrap(params.node.config.graphs).map(function(graph){return graph.graphid;}));
            }
        } else if(this.resourceTypesToDisplayInDropDown().length > 0) {
            this.resourceTypesToDisplayInDropDown().forEach(function(graphid){
                self.downloadGraph(graphid);
            });
        }
    
        this.resourceInstanceDisplayName = params.form && params.form.displayname ? params.form.displayname() : '';
        this.makeFriendly = ontologyUtils.makeFriendly;
        this.getSelect2ConfigForOntologyProperties = ontologyUtils.getSelect2ConfigForOntologyProperties;
        self.newResourceInstance = ko.observable();
        this.resourceReportUrl = arches.urls.resource_report;
        this.resourceEditorUrl = arches.urls.resource_editor;
        this.selectedResourceRelationship = ko.observable(null);
        this.reportResourceId = ko.observable();
        this.reportGraphId = ko.observable(null);
        this.filter = ko.observable('');

        this.toggleSelectedResourceRelationship = function(resourceRelationship) {
            if(self.graphIsSemantic){
                if (self.selectedResourceRelationship() === resourceRelationship) {
                    self.selectedResourceRelationship(null);
                } else {
                    self.selectedResourceRelationship(resourceRelationship);
                }
            }
        };
        
        WidgetViewModel.apply(this, [params]);

        // if a default resource instance is defined, then show them in the ui
        // by pushing them to the value variable
        if (ko.isObservable(this.defaultResourceInstance)) {
            var ret = [];
            if (!(Array.isArray(self.defaultResourceInstance()))) {
                self.defaultResourceInstance([]);
            }
            self.defaultResourceInstance().forEach(function(val){
                var ri = {
                    "resourceId": ko.observable(val.resourceId),
                    "ontologyProperty": ko.observable(val.ontologyProperty),
                    "inverseOntologyProperty": ko.observable(val.inverseOntologyProperty),
                    "resourceXresourceId": ""
                };
                ri.ontologyProperty.subscribe(function(){
                    self.defaultResourceInstance(self.value());
                });
                ri.inverseOntologyProperty.subscribe(function(){
                    self.defaultResourceInstance(self.value());
                });
                ret.push(ri); 
            });
            // only set the default values if the tile has never been saved before OR if this is the config form
            if ((this.tile && !this.tile.noDefaults && ko.unwrap(this.tile.tileid) == "" && ret.length > 0) || !!params.configForm) {
                this.value(ret);
            }
        }

        this.displayValue = ko.observable('');
        
        //
        // this.close is only called if newResourceInstance is True and the user 
        // decides not to add the new resource instance, and closes the window without adding it
        //
        this.close = function(){
            this.newResourceInstance(null);
        };
        
        
        this.setValue = function(valueObject) {
            if (self.multiple) {
                valueObject = [valueObject];
                if (self.value() !== null) {
                    valueObject = valueObject.concat(self.value());
                }
                self.value(valueObject);
            } else {
                self.value([valueObject]);
            }
            if (!!params.configForm) {
                self.defaultResourceInstance(self.value());
            }
        };
        
        this.lookupResourceInstanceData = function(resourceid) {
            if (resourceLookup[resourceid]) {
                return Promise.resolve(resourceLookup[resourceid]);
            } else {
                return window.fetch(arches.urls.search_results + "?id=" + resourceid)
                    .then(function(response){
                        if(response.ok) {
                            return response.json();
                        }
                    })
                    .then(function(json) {
                        resourceLookup[resourceid] = json["results"]["hits"]["hits"][0];
                        return resourceLookup[resourceid];
                    });
            }
        };
        
        if(self.renderContext !== 'search'){
            var updateNameAndOntologyClass = function(values) {
                var names = [];
                var value = ko.unwrap(values);
                if (!self.multiple && value && !Array.isArray(value)) {
                    value = [value];
                }
                if(!!value) {
                    value.forEach(function(val) {
                        if (val) {
                            if(!val.resourceName) {
                                Object.defineProperty(val, 'resourceName', {value: ko.observable()});
                            }
                            if(!val.ontologyClass) {
                                Object.defineProperty(val, 'ontologyClass', {value:ko.observable()});
                            }
                            if(!val.iconClass) {
                                Object.defineProperty(val, 'iconClass', {value: ko.observable()});
                            }
                            self.lookupResourceInstanceData(ko.unwrap(val.resourceId))
                                .then(function(resourceInstance) {
                                    names.push(resourceInstance["_source"].displayname);
                                    self.displayValue(names.join(', '));
                                    val.resourceName(resourceInstance["_source"].displayname)
                                    val.iconClass(self.graphLookup[resourceInstance["_source"].graph_id]?.iconclass || 'fa fa-question')
                                    val.ontologyClass(resourceInstance["_source"].root_ontology_class);
                                });
                        }
                    });
                }
            };
    
            self.value.subscribe(updateNameAndOntologyClass);
            // Resolve Resource Instance Names from the incoming values
            self.value.valueHasMutated();

            this.relationshipsInFilter = ko.computed(function() {
                if(!self.value()) {
                    return [];
                }
                return self.value().filter(function(relationship) {
                    return self.filter().toLowerCase() === '' || relationship.resourceName().toLowerCase().includes(self.filter().toLowerCase());
                });
            });
        }

        this.makeObject = function(id, esSource){
            var graph = self.graphLookup[esSource.graph_id];
            var iconClass = graph.iconclass  || 'fa fa-question';

            var ontologyProperty;
            var inverseOntologyProperty;

            if (graph) {
                ontologyProperty = graph.config.ontologyProperty;
                inverseOntologyProperty = graph.config.inverseOntologyProperty;

                if (self.node && (!ontologyProperty || !inverseOntologyProperty) ) {
                    var ontologyProperties = self.node.config.graphs().find(function(nodeConfigGraph) {
                        return nodeConfigGraph.graphid === graph.graphid;
                    });

                    if (ontologyProperties) {
                        ontologyProperty = ontologyProperty || ontologyProperties.ontologyProperty;
                        inverseOntologyProperty = inverseOntologyProperty || ontologyProperties.inverseOntologyProperty;
                    }
                }
            }

            var ret = {
                "resourceId": ko.observable(id),
                "ontologyProperty": ko.observable(ontologyProperty || ""),
                "inverseOntologyProperty": ko.observable(inverseOntologyProperty || ""),
                "resourceXresourceId": ""
            };            
            Object.defineProperty(ret, 'resourceName', {value: ko.observable(esSource.displayname)});
            Object.defineProperty(ret, 'ontologyClass', {value: ko.observable(esSource.root_ontology_class)});
            Object.defineProperty(ret, 'iconClass', {value: ko.observable(iconClass)});
            if (!!params.configForm) {
                ret.ontologyProperty.subscribe(function(){
                    self.defaultResourceInstance(self.value());
                });
                ret.inverseOntologyProperty.subscribe(function(){
                    self.defaultResourceInstance(self.value());
                });
            }
            
            return ret;
        };


        this.url = ko.observable(arches.urls.search_results);
        this.resourceToAdd = ko.observable("");

        this.disabled = ko.computed(function() {
            return ko.unwrap(self.waitingForGraphToDownload) || ko.unwrap(params.disabled) || !!ko.unwrap(params.form?.locked);
        });
        
        this.select2Config = {
            value: self.renderContext === 'search' ? self.value : self.resourceToAdd,
            clickBubble: true,
            disabled: this.disabled,
            multiple: !self.displayOntologyTable ? params.multiple : false,
            placeholder: this.placeholder() || arches.translations.riSelectPlaceholder,
            closeOnSelect: true,
            allowClear: self.renderContext === 'search' ? true : false,
            onSelect: function(item) {
                self.selectedItem(item);
                if (!(self.renderContext === 'search') || self.allowInstanceCreation) {
                    if (item._source) {
                        if (self.renderContext === 'search'){
                            self.value(item._id);
                        } else {
                            var ret = self.makeObject(item._id, item._source);
                            self.setValue(ret);
                            window.setTimeout(function() {
                                if(self.displayOntologyTable){
                                    self.resourceToAdd("");
                                }
                            }, 250);    
                        }
                    } else {
                        // This section is used when creating a new resource Instance
                        if(!self.preview){
                            var params = {
                                graphid: item._id,
                                complete: ko.observable(false),
                                resourceid: ko.observable(),
                                tileid: ko.observable()
                            };
                            self.newResourceInstance(params);
                            var clearNewInstance = function() {
                                self.newResourceInstance(null);
                                window.setTimeout(function() {
                                    self.resourceToAdd("");
                                }, 250);
                            };
                            params.complete.subscribe(function() {
                                if (params.resourceid()) {
                                    if (self.renderContext === 'search'){
                                        self.value(params.resourceid());
                                        clearNewInstance();
                                    } else {
                                        window.fetch(arches.urls.search_results + "?id=" + params.resourceid())
                                        .then(function(response){
                                            if(response.ok) {
                                                return response.json();
                                            }
                                            throw("error");
                                        })
                                        .then(function(json) {
                                            var item = json.results.hits.hits[0];
                                            var ret = self.makeObject(params.resourceid(), item._source);
                                            self.setValue(ret);
                                        })
                                        .finally(function(){
                                            clearNewInstance();
                                        });
                                    }
                                } else {
                                    clearNewInstance();
                                }
                            });
                        }
                    }
                }
            },
            ajax: {
                url: function() {
                    return self.url();
                },
                dataType: 'json',
                quietMillis: 250,
                data: function(term, page) {
                    //TODO This regex isn't working, but it would nice fix it so that we can do more robust url checking
                    // var expression = /[-a-zA-Z0-9@:%_\+.~#?&//=]{2,256}\.[a-z]{2,4}\b(\/[-a-zA-Z0-9@:%_\+.~#?&//=]*)?/gi;
                    // var regex = new RegExp(expression);
                    // var isUrl = val.target.value.match(regex)
                    var isUrl = term.startsWith('http');
                    if (isUrl) {
                        self.url(term.replace('search', 'search/resources'));
                        return {};
                    } else {
                        self.url(arches.urls.search_results);
                        var queryString = new URLSearchParams();
                        if (self.searchString) {
                            const searchUrl = new URL(self.searchString);
                            queryString = new URLSearchParams(searchUrl.search);
                        } 
                        queryString.set('paging-filter', page);

                        // merge resource type filters
                        var resourceFiltersString = queryString.get('resource-type-filter') || "[]";
                        var resourceFilters = JSON.parse(resourceFiltersString);
                        self.resourceTypesToDisplayInDropDown().forEach(function(graphid){
                            if(!(resourceFiltersString.includes(graphid))){
                                resourceFilters.push({
                                    "graphid": graphid,
                                    "inverted": false
                                });
                            }
                        });
                        if(resourceFilters.length > 0) {
                            queryString.set('resource-type-filter', JSON.stringify(resourceFilters));
                        }
                        if (term || typeof params.termFilter === 'function') {
                            if(typeof params.termFilter === 'function'){
                                params.termFilter(term, queryString);
                            } else {
                                var termFilter = JSON.parse(queryString.get('term-filter')) || [];
                                termFilter.push({
                                    "inverted": false,
                                    "type": "string",
                                    "context": "",
                                    "context_label": "",
                                    "id": term,
                                    "text": term,
                                    "value": term
                                });
                                queryString.set('term-filter', JSON.stringify(termFilter));
                            }
                        }
                        return queryString.toString();
                    }
                },
                results: function(data, page) {
                    if (!data['paging-filter'].paginator.has_next && self.allowInstanceCreation) {
                        self.resourceTypesToDisplayInDropDown().forEach(function(graphid) {
                            var graph = self.graphLookup[graphid];
                            var val = {
                                name: graph.name,
                                _id: graphid,
                                isGraph: true
                            };
                            data.results.hits.hits.push(val);
                            if (!self.graphIds().includes(graphid)) {
                                self.graphIds.push(graphid);
                            }
                        });
                    }
                    return {
                        results: data.results.hits.hits,
                        more: data['paging-filter'].paginator.has_next
                    };
                }
            },
            id: function(item) {
                return item._id;
            },
            formatResult: function(item) {
                if (item._source) {
                    iconClass = self.graphLookup[item._source.graph_id]?.iconclass
                    return `<i class="fa ${iconClass} sm-icon-wrap"></i> ${item._source.displayname}`;
                } else {
                    if (self.allowInstanceCreation) {
                        return '<b> ' + arches.translations.riSelectCreateNew.replace('${graphName}', item.name) + ' . . . </b>';
                    }
                }
            },
            formatSelection: function(item) {
                if (item._source) {
                    return `<i class="fa ${item._source.iconclass} sm-icon-wrap"></i> ${item._source.displayname}`;
                } else {
                    return item.name;
                }
            },
            initSelection: function(ele, callback) {
                if(self.renderContext === "search" && self.value() !== "" && !self.graphIds().includes(self.value())) {
                    var values = self.value();
                    if(!Array.isArray(self.value())){
                        values = [self.value()];
                    }

                    var lookups = [];

                    values.forEach(function(val){
                        var resourceId;
                        if (typeof val === 'string') {
                            resourceId = val;
                        }
                        else if (ko.unwrap(val.resourceId)) {
                            resourceId = ko.unwrap(val.resourceId);
                        }

                        var resourceInstance = self.lookupResourceInstanceData(resourceId).then(
                            function(resourceInstance) { return resourceInstance; }
                        );
           
                        if (resourceInstance) { lookups.push(resourceInstance); }
                    });

                    Promise.all(lookups).then(function(arr){
                        if (arr.length) {
                            var ret = arr.map(function(item) {
                                return {"_source":{"displayname": item["_source"].displayname, "iconclass": self.graphLookup[item._source.graph_id]?.iconclass || 'fa fa-question'}, "_id":item["_id"]};
                            });
                            if(self.multiple === false) {
                                ret = ret[0];
                            }
                            callback(ret);
                        }
                    });
                } else if (self.graphIds().includes(self.value())){
                    self.value(null);
                }
            }
        };

        this.deleteRelationship = function(valueToDelete) {
            var newValues = [];
            self.value().forEach(function(val) {
                if (val.resourceId !== valueToDelete.resourceId) {
                    newValues.push(val);
                }
            });
            self.value(newValues);
            if (!!params.configForm) {
                self.defaultResourceInstance(newValues);
            }
        };

        this.formatLabel = function(name, ontologyProperty, inverseOntologyProperty){
            if (self.graphIsSemantic) {
                return name + ' (' + ontologyUtils.makeFriendly(ontologyProperty) + '/' + ontologyUtils.makeFriendly(inverseOntologyProperty) + ')';
            }
            else {
                return name;
            }
        };
    };

    return ResourceInstanceSelectViewModel;
});
