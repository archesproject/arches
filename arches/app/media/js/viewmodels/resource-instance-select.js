define([
    'knockout',
    'jquery',
    'underscore',
    'viewmodels/widget',
    'arches',
    'views/components/resource-summary',
    'utils/ontology'
], function(ko, $, _, WidgetViewModel, arches, ResourceSummary, ontologyUtils) {
    var resourceLookup = {};
    require(['views/components/workflows/new-tile-step']);
    var ResourceInstanceSelectViewModel = function(params) {
        var self = this;
        params.configKeys = ['placeholder'];
        this.preview = arches.graphs.length > 0;
        this.renderContext = params.renderContext;
        this.multiple = params.multiple || false;
        this.value = params.value || undefined;
        this.graphIsSemantic = params.graph ? !!params.graph.ontologyclass : false;
        this.rootOntologyClass = params.graph ? params.graph.ontologyclass : undefined;
        this.resourceInstanceDisplayName = params.form && params.form.displayname ? params.form.displayname() : '';
        this.makeFriendly = ontologyUtils.makeFriendly;
        this.getSelect2ConfigForOntologyProperties = ontologyUtils.getSelect2ConfigForOntologyProperties;
        self.newTileStep = ko.observable();
        this.resourceReportUrl = arches.urls.resource_report;
        this.selectedResourceRelationship = ko.observable(null);
        this.reportResourceId = ko.observable();
        this.reportGraphId = ko.observable(null);
        this.filter = ko.observable('');

        this.toggleSelectedResourceRelationship = function(resourceRelationship) {
            if (self.selectedResourceRelationship() === resourceRelationship) {
                self.selectedResourceRelationship(null);
            } else {
                self.selectedResourceRelationship(resourceRelationship);
            }
        };
        
        WidgetViewModel.apply(this, [params]);
        
        this.displayValue = ko.observable('');
        
        //
        // this.close is only called if newTileStep is True and the user 
        // decides not to add the new resource instance, and closes the window without adding it
        //
        this.close = function(){
            this.newTileStep(null);
        };
        
        
        var setValue = function(valueObject) {
            if (self.multiple) {
                valueObject = [valueObject];
                if (self.value() !== null) {
                    valueObject = valueObject.concat(self.value());
                }
                self.value(valueObject);
            } else {
                self.value([valueObject]);
            }
        };
        
        var lookupResourceInstanceData = function(resourceid) {
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
                            lookupResourceInstanceData(val.resourceId())
                                .then(function(resourceInstance) {
                                    names.push(resourceInstance["_source"].displayname);
                                    self.displayValue(names.join(', '));
                                    val.resourceName(resourceInstance["_source"].displayname);
                                    val.ontologyClass(resourceInstance["_source"].root_ontology_class);
                                });
                        }
                    });
                }
            };
    
            self.value.subscribe(updateNameAndOntologyClass);
            
            // Resolve Resource Instance Names from the incoming values
            updateNameAndOntologyClass(self.value);

            this.relationshipsInFilter = ko.computed(function() {
                if(!self.value()) {
                    return [];
                }
                return self.value().filter(function(relationship) {
                    return self.filter().toLowerCase() === '' || relationship.resourceName().toLowerCase().includes(self.filter().toLowerCase());
                });
            });

            var relatedResourceModels = ko.computed(function() {
                var res = [];
                var graphlist = this.preview ? arches.graphs : arches.resources;
                if (params.node) {
                    res = params.node.config.graphs().map(function(item){
                        var graph = graphlist.find(function(graph){
                            return graph.graphid === item.graphid;
                        });
                        graph.config = item;
                        return graph;
                    });
                }
                return res;
            }, this);

            this.lookupGraph = function(graphid) {
                var model = relatedResourceModels().find(function(model){
                    return model.graphid === graphid;
                });
                return model;
            };
        }

        var makeObject = function(id, esSource){
            var graph = self.lookupGraph(esSource.graph_id);
            var ret = {
                "resourceId": ko.observable(id),
                "ontologyProperty": ko.observable(graph.config.ontologyProperty || ''),
                "inverseOntologyProperty": ko.observable(graph.config.inverseOntologyProperty || ''),
                "resourceXresourceId": ""
            };            
            Object.defineProperty(ret, 'resourceName', {value: ko.observable(esSource.displayname)});
            Object.defineProperty(ret, 'ontologyClass', {value: ko.observable(esSource.root_ontology_class)});
            return ret;
        };

        var url = ko.observable(arches.urls.search_results);
        this.url = url;
        var resourceToAdd = ko.observable("");
        this.select2Config = {
            value: self.renderContext === 'search' ? self.value : resourceToAdd,
            clickBubble: true,
            multiple: self.renderContext === 'search' ? params.multiple : false,
            placeholder: this.placeholder() || "Add new Relationship",
            closeOnSelect: true,
            allowClear: self.renderContext === 'search' ? true : false,
            onSelect: function(item) {
                if (self.renderContext !== 'search') {
                    if (item._source) {
                        var ret = makeObject(item._id, item._source);
                        setValue(ret);
                        window.setTimeout(function() {
                            resourceToAdd("");
                        }, 250);
                    } else {
                        // This section is used when creating a new resource Instance
                        if(!self.preview){
                            var params = {
                                graphid: item._id,
                                complete: ko.observable(false),
                                resourceid: ko.observable(),
                                tileid: ko.observable()
                            };
                            self.newTileStep(params);
                            params.complete.subscribe(function() {
                                window.fetch(arches.urls.search_results + "?id=" + params.resourceid())
                                    .then(function(response){
                                        if(response.ok) {
                                            return response.json();
                                        }
                                        throw("error");
                                    })
                                    .then(function(json) {
                                        var item = json.results.hits.hits[0];
                                        var ret = makeObject(params.resourceid(), item._source);
                                        setValue(ret);
                                    })
                                    .finally(function(){
                                        self.newTileStep(null);
                                        window.setTimeout(function() {
                                            resourceToAdd("");
                                        }, 250);
                                    });
                            });
                        }
                    }
                }
            },
            ajax: {
                url: function() {
                    return url();
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
                        url(term.replace('search', 'search/resources'));
                        return {};
                    } else {
                        url(arches.urls.search_results);
                        var data = { 'paging-filter': page };
                        if (!!params.node) {
                            var graphids = ko.unwrap(params.node.config.graphs).map(function(graph) {
                                return {
                                    "graphid": graph.graphid,
                                    "inverted": false
                                };
                            });
                            if(graphids.length > 0) {
                                data['resource-type-filter'] = JSON.stringify(graphids);
                            }
                        }
                        if (term) {
                            data['term-filter'] = JSON.stringify([{
                                "inverted": false,
                                "type": "string",
                                "context": "",
                                "context_label": "",
                                "id": term,
                                "text": term,
                                "value": term

                            }]);
                        }
                        return data;
                    }
                },
                results: function(data, page) {
                    if (!data['paging-filter'].paginator.has_next && self.renderContext !== 'search') {
                        if (relatedResourceModels()) {
                            relatedResourceModels().forEach(function(graph) {
                                var val = {
                                    name: graph.name,
                                    _id: graph.graphid,
                                    isGraph: true
                                };
                                data.results.hits.hits.push(val);
                            });
                        }
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
                    return item._source.displayname;
                } else {
                    return '<b> Create a new ' + item.name + ' . . . </b>';
                }
            },
            formatSelection: function(item) {
                if (item._source) {
                    return item._source.displayname;
                } else {
                    return item.name;
                }
            },
            initSelection: function(ele, callback) {
                if(self.renderContext === "search" && self.value() !== "") {
                    var values = self.value();
                    if(!Array.isArray(self.value())){
                        values = [self.value()];
                    }
                    var lookups = [];
                    values.forEach(function(val){
                        lookups.push(lookupResourceInstanceData(val)
                            .then(function(resourceInstance) {
                                return resourceInstance;
                            })
                        );
                    });
                    Promise.all(lookups).then(function(val){
                        var ret = val.map(function(item) {
                            return {"_source":{"displayname": item["_source"].displayname}, "_id":item["_id"]};
                        });
                        if(self.multiple === false) {
                            ret = ret[0];
                        }
                        callback(ret);
                    });
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
