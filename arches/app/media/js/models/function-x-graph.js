define([
    'arches',
    'models/abstract',
    'knockout',
    'knockout-mapping',
    'underscore'
], function (arches, AbstractModel, ko, koMapping, _) {

    var FunctionXGraphModel = AbstractModel.extend({
        /**
        * A backbone model to manage function data
        * @augments AbstractModel
        * @constructor
        * @name FunctionXGraphModel
        */
        url: arches.urls.functionXGraph,

        /**
        * parse - parses the passed in attributes into a {@link FunctionXGraphModel}
        * @memberof FunctionXGraphModel.prototype
        * @param  {object} attributes - the properties to seed a {@link FunctionXGraphModel} with
        */
        initialize: function(options) {
            var self = this;
            this._json = ko.observable('');
            this.function = options.function;
            this.graphid = ko.observable();
            this.config = koMapping.fromJS({});

            this.parse(options);

            this.json = ko.computed(function() {
                return JSON.stringify(_.extend(JSON.parse(self._json()), {
                    graphid: self.graphid(),
                    config: koMapping.toJS(self.config),
                }))
            });

            self.dirty = ko.computed(function() {
                return self.json() !== self._json();
            });
        },

        parse: function(data) {
            this._json(JSON.stringify(data));
            this.function = data.function;
            this.graphid(data.graphid);
            koMapping.fromJS(data.config, this.config)

            this.set('id', data.function)
        },

        /**
        * discard unsaved model changes and resets the model data
        * @memberof FunctionXGraphModel.prototype
        */
        reset: function () {
            this.parse(JSON.parse(this._json()));
        },

        /**
        * returns a JSON object containing model data
        * @memberof FunctionXGraphModel.prototype
        * @return {object} a JSON object containing model data
        */
        toJSON: function () {
            return JSON.parse(this.json());
        },
    });
    return FunctionXGraphModel;
});
