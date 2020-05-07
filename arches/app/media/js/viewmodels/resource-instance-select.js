define([
    'knockout',
    'jquery',
    'viewmodels/widget',
    'arches',
    'report-templates',
], function(ko, $, WidgetViewModel, arches, reportLookup) {
    var nameLookup = {};
    require(['views/components/workflows/new-tile-step']);
    var ResourceInstanceSelectViewModel = function(params) {
        var self = this;
        params.configKeys = ['placeholder'];
        this.renderContext = params.renderContext;
        this.multiple = params.multiple || false;
        this.value = params.value || undefined;
        this.graphIsSemantic = params.graph ? !!params.graph.ontologyclass : false;
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

        this.useSemanticRelationships = arches.useSemanticRelationships;


        WidgetViewModel.apply(this, [params]);
        //var displayName = ko.observable('');
        self.newTileStep = ko.observable();
        // this.valueList = ko.computed(function() {
        //     var valueList = ko.unwrap(self.value);
        //     //displayName();
        //     if (!self.multiple && valueList) {
        //         valueList = [valueList];
        //     }
        //     if (Array.isArray(valueList)) {
        //         return valueList;
        //     }
        //     return [];
        // });
        this.displayValue = ko.observable('');

        ///
        // this.removeGraphIdsFromValue and this.close are only used if newTileStep is True
        ///
        this.removeGraphIdsFromValue = function(value) {
            if (Array.isArray(value)) {
                self.graphids.forEach(function(graphid){
                    var graphindex = self.value().indexOf(graphid);
                    if (graphindex > -1) {
                        self.value().splice(graphindex, 1);
                    }
                });
                return ko.unwrap(value).length > 0 ? ko.unwrap(value) : null;
            } else if (self.graphids.indexOf(value) !== -1) {
                return null;
            } else {
                return value;
            }
        };

        this.close = function(){
            var cleanval = self.removeGraphIdsFromValue(this.value());
            this.value(cleanval);
            this.newTileStep(null);
        };


        this.selectedResourceRelationship = ko.observable(null);

        // this.editRelationship = function(relationshipItem) {
        //     this.selectedResourceRelationship(resourceName)
        // }

        // this.valueObjects = ko.computed(function() {
        //     return self.valueList().map(function(value) {
        //         return {
        //             id: value,
        //             name: nameLookup[value],
        //             reportUrl: arches.urls.resource_report + value
        //         };
        //     }).filter(function(item) {
        //         return item.name;
        //     });
        // });


        var setValue = function(valueObject) {
            if (self.multiple) {
                valueObject = [valueObject];
                if (self.value() !== null) {
                    valueObject = valueObject.concat(self.value());
                }
                self.value(valueObject);
            } else {
                self.value([valueObject]);
                // Object.assign(self.value, valueObject);
                //self.value(valueObject);
                // if(!self.value()[0].resourceName){
                //     Object.assign(self.value()[0], valueObject);

                //     Object.defineProperty(self.value()[0], 'resourceName', {
                //         value: valueObject.resourceName
                //     });
                //     Object.defineProperty(self.value()[0], 'ontologyClass', {
                //         value: valueObject.ontologyClass
                //     });
                // }
            }
        };

        //this.valueObjects = ko.observableArray();

        this.resourceReportUrl = arches.urls.resource_report;

        var updateName = function() {
            var names = [];
            var value = ko.unwrap(self.value);
            if (!self.multiple && value && !Array.isArray(value)) {
                value = [value];
            }
            if(!!value) {
                value.forEach(function(val) {
                    if (val) {
                        if (nameLookup[val.resourceId()]) {
                            names.push(nameLookup[val.resourceId()]);
                            self.displayValue(names.join(', '));
                        } else {
                            window.fetch(arches.urls.search_results + "?id=" + val.resourceId())
                                .then(function(response){
                                    if(response.ok) {
                                        return response.json();
                                    }
                                })
                                .then(function(json) {
                                    json["results"]["hits"]["hits"].forEach(function(resourceInstance){
                                        nameLookup[val.resourceId()] = resourceInstance["_source"].displayname;
                                        names.push(resourceInstance["_source"].displayname);
                                        self.displayValue(names.join(', '));
                                        val.resourceName(nameLookup[val.resourceId()]);
                                    });
                                });
                            // window.fetch(arches.urls.disambiguate_node_value(params.datatype, val.resourceXresourceId()))
                            //     .then(function(response) {
                            //         return response.json();
                            //     }).then(function(data) {
                            //         data.forEach(function(resourceInstance){
                            //             nameLookup[val.resourceId()] = resourceInstance.resourceName;
                            //             names.push(resourceInstance.resourceName);
                            //             self.displayValue(names.join(', '));
                            //             val.resourceName(nameLookup[val.resourceId()]);
                            //             // var valueObj = makeObject(resourceInstance.resourceId, resourceInstance.resourceName, '');
                            //             // setValue(valueObj);
                            //         });
                            //         //self.valueObjects(data);
                            //     });
                        }
                    }
                });
            }
        };

        // update related resource names even though it's already in tile.data, 
        // but the name might have been changed since the relationship was made
        // if(self.multiple === true){
        //     if(!!self.value()){
        //         self.value().forEach(function(value){
        //             updateName();
        //         });
        //     }
        // }else{
        //     updateName();
        // }

        updateName();

        var relatedResourceModels = ko.computed(function() {
            var res = [];
            if (params.node) {
                var ids = ko.unwrap(params.node.config.graphid);
                if (ids) {
                    res = arches.resources.filter(function(graph) {
                        return ids.indexOf(graph.graphid) >= 0;
                    }).map(function(g) {
                        return {
                            name: g.name,
                            _id: g.graphid,
                            isGraph: true
                        };
                    });
                }
            }
            return res;
        }, this);


        var makeObject = function(id, name, ontologyclass){
            var ret = {
                "resourceId": ko.observable(id),
                "ontologyProperty": ko.observable(""),
                "inverseOntologyProperty": ko.observable(""),
                "resourceName": ko.observable(name),
                "ontologyClass": ko.observable(ontologyclass),
                "resourceXresourceId": ""
            };
            // Object.defineProperty(ret, 'resourceName', {
            //     value: name
            // });
            // Object.defineProperty(ret, 'ontologyClass', {
            //     value: ontologyclass
            // });
            return ret;
        };

        var getResourceInfo = function() {
            return window.fetch(arches.urls.search_results + "?id=" + params.resourceid())
                .then(function(response){
                    if(response.ok === false) {
                        return response.json();
                    }
                    throw("error");
                })
                .then(function(json) {
                    return json;
                });
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
                                    if(response.ok === false) {
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
                    if (!data['paging-filter'].paginator.has_next) {
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
            initSelection: function() {

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
