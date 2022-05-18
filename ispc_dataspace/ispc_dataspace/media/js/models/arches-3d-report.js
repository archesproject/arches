define(['arches',
    'arches_3d',
    'arches-original-report',
    'knockout',
    'knockout-mapping',
    'underscore',
    'report-templates'
], function(arches, arches_3d, ReportModel, ko, koMapping, _, reportLookup) {
    var CustomReportModel = ReportModel.extend({

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
                    var templateId = ko.observable(value);
                    this.set(key, ko.computed({
                        read: function() {
                            return templateId();
                        },
                        write: function(value) {
                            var key;
                            var defaultConfig = JSON.parse(reportLookup[value].defaultconfig);
                            for (key in defaultConfig) {
                                defaultConfig[key] = ko.observable(defaultConfig[key]);
                            }
                            var currentConfig = this.get('config');
                            this.set('config', _.defaults(currentConfig, defaultConfig));
                            for (key in defaultConfig) {
                                self.configKeys.push(key);
                            }
                            templateId(value);
                        },
                        owner: this
                    }));
                    break;
                case 'config':
                    var config = {};
                    var configKeys = [];
                    self.configKeys.removeAll();
                    _.each(value, function(configVal, configKey) {
                        if (!ko.isObservable(configVal)) {
                            configVal = ko.observable(configVal);
                        }
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

            this.related_resources = [];

            this.sort_related = function(anArray, property) {
                anArray.sort(function(a, b){
                    if (a[property] > b[property]) return 1;
                    if (b[property] > a[property]) return -1;
                    return 0;
                });
            };
            
            _.each(this.get('related_resources'), function(rr){
                
                var res = {'graph_name': rr.name, 'related':[]};
                
                _.each(rr.resources, function(resource) {
                    
                    $.ajax({
                        type: 'GET',
                        url: arches_3d.urls.node_values,
                        async: false,
                        data: {
                            resourceid: resource.instance_id,
                            node_name: 'Thumbnail Image'
                        },
                        success: function(response){

                            if (response.length > 0){
                                resource.thumbnail_url = response[0].url;
                            }

                            _.each(resource.relationships, function (relationship) {
                                res.related.push({
                                    'displayname': resource.displayname,
                                    'link': arches.urls.resource_report + resource.instance_id,
                                    'relationship': relationship,
                                    'resourceid': resource.instance_id,
                                    'thumbnail_url': resource.thumbnail_url
                                });
                            });
                        },
                        error: function(response){
                            console.log(response);
                        }
                    });
                });

                this.sort_related(res.related, 'displayname');
                this.related_resources.push(res);
                
            }, this);

            this.sort_related(this.related_resources, 'graph_name');

            this._data(JSON.stringify(this.toJSON()));
        },

    });
    return CustomReportModel;
});
