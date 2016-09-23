define(['arches',
    'models/abstract',
    'knockout',
    'knockout-mapping',
    'underscore'
], function (arches, AbstractModel, ko, koMapping, _) {
    var ReportModel = AbstractModel.extend({
        /**
        * A backbone model to manage report data
        * @augments AbstractModel
        * @constructor
        * @name ReportModel
        */

        url: arches.urls.report_editor,

        initialize: function(attributes){
            var self = this;

            this.set('reportid', ko.observable());
            this.set('name', ko.observable());
            this.set('template_id', ko.observable());
            this.set('graph', ko.observable());
            this.set('active', ko.observable());
            this.set('config', {});
            self.configKeys = ko.observableArray();

            this._data = ko.observable('{}');

            this.dirty = ko.computed(function(){
                return JSON.stringify(_.extend(JSON.parse(self._data()),self.toJSON())) !== self._data();
            });

            this.parse(attributes);
        },

        /**
         * parse - parses the passed in attributes into a {@link ReportModel}
         * @memberof ReportModel.prototype
         * @param  {object} attributes - the properties to seed a {@link ReportModel} with
         */
        parse: function(attributes){
            var self = this;
            this._attributes = attributes;

            _.each(attributes.data, function(value, key){
                switch(key) {
                    case 'reportid':
                        this.set('id', value);
                    case 'name':
                    case 'template_id':
                    case 'graph':
                    case 'active':
                        this.get(key)(value);
                        break;
                    case 'config':
                        var config = {};
                        self.configKeys.removeAll();
                        _.each(value, function(configVal, configKey) {
                            config[configKey] = ko.observable(configVal);
                            self.configKeys.push(configKey);
                        });
                        this.set(key, config);
                        break;
                    default:
                        this.set(key, value);
                }
            }, this);

            this._data(JSON.stringify(this.toJSON()));
        },

        reset: function () {
            this._attributes.data  = JSON.parse(this._data());
            this.parse(this._attributes);
        },

        toJSON: function(){
            var ret = {};
            for(var key in this.attributes){
                if (ko.isObservable(this.attributes[key])){
                    ret[key] = this.attributes[key]();
                } else if (key === 'config') {
                    var configKeys = this.configKeys();
                    var config = null;
                    if (configKeys.length > 0) {
                        config = {};
                        _.each(configKeys, function(configKey) {
                            config[configKey] = self.config[configKey]();
                        });
                    }
                    ret[key] = config;
                } else {
                    ret[key] = this.attributes[key];
                }
            }
            return ret;
        }
    });
    return ReportModel;
});
