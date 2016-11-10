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
        * Initializes the model with optional parameters
        * @memberof FunctionXGraphModel.prototype
        * @param {object} options
        * @param {object} options.id - the id of the {@link FunctionXGraphModel}
        * @param {object} options.function - a reference to the parent {@link FunctionModel}
        * @param {object} options.function_id - a reference to the parent {@link FunctionModel} id
        * @param {object} options.graph_id - a reference to the parent {@link GraphModel} id
        * @param {object} options.config - the properties requiring user configuration 
        */
        initialize: function(options) {
            var self = this;
            // _id is needed because we can apply more then
            // one function at a time in the function-manager
            this._id = _.uniqueId();  
            this._json = ko.observable('');
            this.id = options.id;
            this.function = options.function;
            this.function_id = options.function_id;
            this.graph_id = options.graph_id;
            this.config = koMapping.fromJS({});

            this.parse(options);
            
            this.dirty = ko.computed(function(){
                return JSON.stringify(_.extend(JSON.parse(this._json()),this.toJSON())) !== this._json();
            }, this)

        },

        /**
        * parse - parses any passed in data to observable attributes 
        * @memberof FunctionXGraphModel.prototype
        * @param {object} data - the observable properties to seed a {@link FunctionXGraphModel} with
        * @param {object} data.id - the id of the {@link FunctionXGraphModel}
        * @param {object} data.config - the properties requiring user configuration 
        */
        parse: function(data) {
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
            var ret = {};
            var trackedProperties = ['_id', 'id', 'function_id', 'graph_id', 'config'];
            for(var key in this){
                if(trackedProperties.indexOf(key) !== -1){
                    if(key === 'config'){
                        ret[key] = koMapping.toJS(this[key]);
                        delete ret[key]['__ko_mapping__'];
                    }else{
                        ret[key] = this[key];
                    }
                   
                }
            }
            return ret;
        },
    });
    return FunctionXGraphModel;
});
