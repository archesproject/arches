define(['views/graph/graph-base-data'], function(data) {
    /**
    * A base viewmodel for functions
    *
    * @constructor
    * @name FunctionViewModel
    *
    * @param  {string} params - a configuration object
    */
    var FunctionViewModel = function(params) {
        this.graphid = data.graphid;
        this.graph = data.graph;
        this.config = params.config;
    };
    return FunctionViewModel;
});
