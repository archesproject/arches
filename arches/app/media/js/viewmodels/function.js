define([], function () {
    /**
    * A base viewmodel for functions
    *
    * @constructor
    * @name FunctionViewModel
    *
    * @param  {string} params - a configuration object
    */
    var FunctionViewModel = function(params) {
        var self = this;
        this.state = params.state || 'form';
        
    };
    return FunctionViewModel;
});
