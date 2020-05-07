define([
    'knockout',
    'jquery',
    'viewmodels/widget',
    'arches',
    'report-templates',
], function(ko, $, WidgetViewModel, arches, reportLookup) {
    var resourceLookup = {};
    require(['views/components/workflows/new-tile-step']);
    var ResourceInstanceSelectViewModel = function(params) {
        var self = this;
        params.configKeys = ['placeholder'];
        this.renderContext = params.renderContext;
        this.multiple = params.multiple || false;
        this.value = params.value || undefined;
        this.graphIsSemantic = params.graph ? !!params.graph.ontologyclass : false;
        self.newTileStep = ko.observable();
        this.useSemanticRelationships = arches.useSemanticRelationships;
        this.resourceReportUrl = arches.urls.resource_report;
        this.selectedResourceRelationship = ko.observable(null);

        this.graphids = params.node ? ko.unwrap(params.node.config.graphid) : [params.graphid];
        this.graphids = this.graphids || [];
        this.graphNames = {};
        this.graphids.forEach(function(graphid){
            self.graphNames[graphid] = arches.resources.find(function(resource){
                return resource.graphid === graphid;
            });
        });

        this.filter = ko.observable('');
        this.relationshipInFilter = function(relationship) {
            if (self.filter().toLowerCase() === '' || relationship.resourceName().toLowerCase().includes(self.filter().toLowerCase())){
                return true;
            }
            return false;
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

        var lookupResourceInstanceName = function(resourceid) {
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
            // Resolve Resource Instance Names from the incoming values
            var names = [];
            var value = ko.unwrap(self.value);
            if (!self.multiple && value && !Array.isArray(value)) {
                value = [value];
            }
            if(!!value) {
                value.forEach(function(val) {
                    if (val) {
                        lookupResourceInstanceName(val.resourceId())
                            .then(function(resourceInstance) {
                                names.push(resourceInstance["_source"].displayname);
                                self.displayValue(names.join(', '));
                                val.resourceName(resourceInstance["_source"].displayname);
                            });
                    }
                });
            }

            var relatedResourceModels = ko.computed(function() {
                var res = [];
                if (params.node) {
                    res = params.node.config.graphs().map(function(item){
                        var graph = arches.resources.find(function(graph){
                            return graph.graphid === item.graphid;
                        });
                        return {
                            name: graph.name,
                            _id: graph.graphid,
                            isGraph: true
                        };
                    });
                }
                return res;
            }, this);

            this.lookupGraphName = function(graphid) {
                var model = relatedResourceModels().find(function(model){
                    return model._id === graphid;
                });
                return model;
            };
        }

        var makeObject = function(id, name, ontologyclass){
            var ret = {
                "resourceId": ko.observable(id),
                "ontologyProperty": ko.observable(""),
                "inverseOntologyProperty": ko.observable(""),
                "resourceName": ko.observable(name),
                "ontologyClass": ko.observable(ontologyclass),
                "resourceXresourceId": ""
            };
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
                        var ret = makeObject(item._id, item._source.displayname, item._source.root_ontology_class);
                        setValue(ret);
                        window.setTimeout(function() {
                            resourceToAdd("");
                        }, 250);
                    } else {
                        // This section is used when creating a new resource Instance
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
                                    var ret = makeObject(params.resourceid(), item._source.displayname, item._source.root_ontology_class);
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
                            relatedResourceModels().forEach(function(val) {
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
                        lookups.push(lookupResourceInstanceName(val)
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
                return name + ' (' + self.makeFriendly(ontologyProperty) + '/' + self.makeFriendly(inverseOntologyProperty) + ')';
            }
            else {
                return name;
            }
        };

        this.makeFriendly = function(item) {
            var parts = item.split("/");
            return parts[parts.length-1];
        };

        this.getSelect2ConfigForOntologyProperties = function(value, domain, range) {
            return {
                value: value,
                clickBubble: false,
                placeholder: 'Select an Ontology Property',
                closeOnSelect: true,
                allowClear: false,
                ajax: {
                    url: function() {
                        return arches.urls.ontology_properties;
                    },
                    data: function(term, page) {
                        var data = { 
                            'domain_ontology_class': domain,
                            'range_ontology_class': range,
                            'ontologyid': ''
                        };
                        return data;
                    },
                    dataType: 'json',
                    quietMillis: 250,
                    results: function(data, page) {
                        return {
                            results: data
                        };
                    }
                },
                id: function(item) {
                    return item;
                },
                formatResult: this.makeFriendly,
                formatSelection: this.makeFriendly,
                initSelection: function(el, callback) {
                    callback(value());
                }
            };
        };

    };

    return ResourceInstanceSelectViewModel;
});
