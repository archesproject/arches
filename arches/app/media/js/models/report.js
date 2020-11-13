define(['jquery',
    'arches',
    'models/abstract',
    'knockout',
    'knockout-mapping',
    'underscore',
    'report-templates'
], function($, arches, AbstractModel, ko, koMapping, _, reportLookup) {
    var ReportModel = AbstractModel.extend({
        /**
         * A backbone model to manage report data
         * @augments AbstractModel
         * @constructor
         * @name ReportModel
         */

        url: arches.urls.graph,

        initialize: function(options) {
            var self = this;
            this.templateId = ko.observable(self.get('graph').template_id);
            this.cards = options.cards || [];
            this.preview = options.preview;
            this.userisreviewer = options.userisreviewer;
            
            this.set('graphid', ko.observable());
            this.set('config', {});
            self.configKeys = ko.observableArray();
            
            this._data = ko.observable('{}');
            
            this.configJSON = ko.observable({});
            this.configState = {};
            this.configKeys.subscribe(function(val){
                var config;
                self.defaultConfig = JSON.parse(reportLookup[self.templateId()].defaultconfig);
                if (val.length) {
                    self.configState = {};
                    config = self.get('config');
                    _.each(val, function(key) {
                        if (self.defaultConfig.hasOwnProperty(key)) {
                            self.configState[key] = ko.unwrap(config[key]);
                        }
                    });
                    self.configState = koMapping.fromJS(self.configState);
                }
            });

            this.resetConfigs = function(previousConfigs) {
                this.configKeys().forEach(function(key){
                    if (self.defaultConfig.hasOwnProperty(key)) {
                        if (JSON.stringify(self.configState[key]()) !== JSON.stringify(previousConfigs[key])) {
                            koMapping.fromJS(previousConfigs, self.configState);
                        }
                    }
                });
            };

            this.relatedResourcesLookup = ko.observable({});
            
            if (options.related_resources) {
                this.updateRelatedResourcesLookup(options.related_resources);
            }

            this.graph = options.graph;
            this.parse(options.graph);
        },

        /**
         * parse - parses the passed in attributes into a {@link ReportModel}
         * @memberof ReportModel.prototype
         * @param  {object} attributes - the properties to seed a {@link ReportModel} with
         */
        parse: function(attributes) {
            var self = this;
            this._attributes = attributes;

            _.each(attributes, function(value, key) {
                switch (key) {
                case 'graphid':
                    this.set('id', value);
                    this.get('graphid')(value);
                    break;
                case 'template_id':
                    self.templateId(value);
                    this.set(key, ko.computed({
                        read: function() {
                            return self.templateId();
                        },
                        write: function(value) {
                            var key;
                            var configKeys = [];
                            var defaultConfig = JSON.parse(reportLookup[value].defaultconfig);
                            for (key in defaultConfig) {
                                defaultConfig[key] = ko.observable(defaultConfig[key]);
                            }
                            var currentConfig = this.get('config');
                            this.set('config', _.defaults(currentConfig, defaultConfig));
                            for (key in defaultConfig) {
                                if (_.contains(self.configKeys(), key) === false) {
                                    configKeys.push(key);
                                }
                            }
                            self.templateId(value);
                            self.configKeys(self.configKeys().concat(configKeys));
                        },
                        owner: this
                    }));
                    break;
                case 'config':
                    var config = {};
                    var configKeys = [];
                    self.configKeys.removeAll();
                    _.each(value, function(configVal, configKey) {
                        config[configKey] = configVal;
                        configKeys.push(configKey);
                    });
                    this.set(key, config);
                    self.configKeys(configKeys);
                    break;
                default:
                    this.set(key, value);
                }
            }, this);

            this._data(JSON.stringify(this.toJSON()));
        },

        updateRelatedResourcesLookup: function(json) {
            var relatedResourcesLookup = this.relatedResourcesLookup();

            for (var [graphId, value] of Object.entries(json)) {
                var relatedResources;
                var paginator;
                var remainingResources;
                
                if (!relatedResourcesLookup[graphId]) {
                    // add graphId to lookup if we haven't added it yet
                    relatedResources = ko.observableArray();
                    remainingResources = ko.observable();
                    paginator = ko.observable();

                    relatedResourcesLookup[graphId] = {
                        'graphId': graphId,
                        'loadedRelatedResources': relatedResources,
                        'name': value['name'] || value['related_resources']['node_config_lookup'][graphId]['name'],
                        'paginator': paginator,
                        'remainingResources': remainingResources,
                        'totalRelatedResources': value['related_resources'] ? value['related_resources']['total']['value'] : 0,
                    };
                } else {
                    // else get pertinent references
                    relatedResources = relatedResourcesLookup[graphId]['loadedRelatedResources'];
                    paginator = relatedResourcesLookup[graphId]['paginator'];
                    remainingResources = relatedResourcesLookup[graphId]['remainingResources'];
                }

                paginator(value['paginator']);

                /* 
                    if there's no paginator, the incoming json is all related resource instances,
                    and we should remove the ones we already have so as not to duplicate them
                */
                if (!value['paginator']) {relatedResources.removeAll();}

                if (value['related_resources']) {
                    // add new resource relationships to lookup entry
                    for (var resourceRelationship of value['related_resources']['resource_relationships']) {
                        var relatedResource = value['related_resources']['related_resources'].find(function(resource) {
                            return (
                                resource.resourceinstanceid === resourceRelationship.resourceinstanceidto
                                || resource.resourceinstanceid === resourceRelationship.resourceinstanceidfrom
                                || this.attributes && resource.resourceinstanceid === this.attributes.graph.graphid  // self
                            );
                        });
    
                        if (relatedResource) {
                            relatedResources.push({
                                'displayName': relatedResource.displayname,
                                'relationship': resourceRelationship.relationshiptype_label,
                                'link': arches.urls.resource_report + relatedResource.resourceinstanceid,
                            });
                        }
                    }

                    var resourceLimit = value['related_resources']['resource_relationships'].length;  /* equivalent to settings.py RELATED_RESOURCES_PER_PAGE */ 
                    var remainingResourcesCount = value['related_resources']['total']['value'] - relatedResources().length;
    
                    remainingResources(remainingResourcesCount < resourceLimit ? remainingResourcesCount : resourceLimit);
                }
            }

            this.relatedResourcesLookup(relatedResourcesLookup);
        },

        getRelatedResources: function(loadAll, resource) {
            $.ajax({
                context: this,
                url: (
                    arches.urls.related_resources 
                    + this.attributes.resourceid 
                    + `?resourceinstance_graphid=${resource.graphId}`
                    + (loadAll ? `&paginate=false` : `&page=${resource.paginator().next_page_number}`)
                ),
            }).done(function(json) {
                this.updateRelatedResourcesLookup({
                    // coerces expected shape
                    [resource.graphId]: json['paginator'] ? json : {'related_resources': json, 'paginator': null }
                });  
            });
        },

        reset: function() {
            this._attributes = JSON.parse(this._data());
            this.parse(this._attributes);
        },

        toJSON: function() {
            var ret = {};
            var self = this;
            for (var key in ['template_id', 'config']) {
                if (ko.isObservable(this.attributes[key])) {
                    ret[key] = this.attributes[key]();
                } else if (key === 'config') {
                    var configKeys = this.configKeys();
                    var config = null;
                    if (configKeys.length > 0) {
                        config = {};
                        _.each(configKeys, function(configKey) {
                            config[configKey] = ko.unwrap(self.get('config')[configKey]);
                        });
                    }
                    ret[key] = config;
                } else {
                    ret[key] = this.attributes[key];
                }
            }
            return ret;
        },

        save: function() {
            AbstractModel.prototype.save.call(this, function(request, status, self) {
                if (status === 'success') {
                    this._data(JSON.stringify(this.toJSON()));
                }
            }, this);
        }
    });
    return ReportModel;
});
