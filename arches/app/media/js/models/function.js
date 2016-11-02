define([
    'arches',
    'models/abstract',
    'knockout',
    'knockout-mapping',
    'underscore'
], function (arches, AbstractModel, ko, koMapping, _) {

    var FunctionModel = AbstractModel.extend({
        /**
        * A backbone model to manage function data
        * @augments AbstractModel
        * @constructor
        * @name FunctionModel
        */
        url: arches.urls.function,

        /**
        * parse - parses the passed in attributes into a {@link FunctionModel}
        * @memberof FunctionModel.prototype
        * @param  {object} attributes - the properties to seed a {@link FunctionModel} with
        */
        initialize: function(options) {
            var self = this;
            this._json = ko.observable('');
            this.functionid = options.functionid;
            this.defaultconfig = koMapping.fromJS({});
            this.name = ko.observable();
            this.description = ko.observable();
            this.functiontype = ko.observable();
            this.component = ko.observable();

            this.parse(options);

            this.json = ko.computed(function() {
                return JSON.stringify(_.extend(JSON.parse(self._json()), {
                    defaultconfig: koMapping.toJS(self.defaultconfig),
                    name: self.name(),
                    description: self.description(),
                    functiontype: self.functiontype(),
                    component: self.component(),
                }))
            });

            self.dirty = ko.computed(function() {
                return self.json() !== self._json();
            });
        },

        parse: function(data) {
            this._json(JSON.stringify(data));
            this.functionid = data.functionid;
            koMapping.fromJS(data.defaultconfig,this.defaultconfig);
            this.name(data.name);
            this.description(data.description);
            this.functiontype(data.functiontype);
            this.component(data.component);

            this.set('id', data.functionid)
        },

        /**
        * discard unsaved model changes and resets the model data
        * @memberof FunctionModel.prototype
        */
        reset: function () {
            this.parse(JSON.parse(this._json()));
        },

        /**
        * returns a JSON object containing model data
        * @memberof FunctionModel.prototype
        * @return {object} a JSON object containing model data
        */
        toJSON: function () {
            return JSON.parse(this.json());
        },
    });
    return FunctionModel;
});
