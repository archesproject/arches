define([
    'underscore',
    'arches',
    'models/abstract',
    'knockout',
    'knockout-mapping',
    'underscore'
], function (_, arches, AbstractModel, ko, koMapping, _) {

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
            this._id = options._id = _.uniqueId();
            this._json = ko.observable('');
            this.id = null;
            this.function = '';
            this.function_id = '';
            this.graphid = '';
            this.config = koMapping.fromJS({});


            // this.json = ko.computed(function() {
            //     var config = koMapping.toJS(this.config);
            //     delete config['__ko_mapping__'];
            //     return JSON.stringify(_.extend(JSON.parse(this._json()), {
            //         config: config,
            //     }))
            // }, this);

            // this.dirty = ko.computed(function() {
            //     var _json = JSON.parse(self._json())
            //     delete _json.config['__ko_mapping__'];
            //     return JSON.stringify(this.toJSON()) !== JSON.stringify(_json);
            // }, this);

            this.parse(options);

            this.dirty = ko.computed(function(){
                return JSON.stringify(_.extend(JSON.parse(self._json()),self.toJSON())) !== self._json();
            })
        },

        parse: function(data) {
            //this._json(JSON.stringify(koMapping.toJS(data)));
            this.id = data.id;
            this.function = data.function;
            this.function_id = data.function_id;
            this.graphid = data.graphid;
            koMapping.fromJS(data.config, this.config)

            this.set('id', data.id)
            this._json(JSON.stringify(this.toJSON()));
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
            //return JSON.parse(this.json());
            var ret = {};
            for(var key in this.attributes){
                if(key === 'id' || key === 'function_id' || key === 'graphid'|| key === 'config'){
                     if(key === 'config'){
                        ret[key] = koMapping.toJS(this[key]);
                    }else{
                        ret[key] = this[key];
                    }
                   
                }
            }
            return ret;
            return koMapping.toJS(this.attributes);
        },
    });
    return FunctionXGraphModel;
});
