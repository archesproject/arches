require([
    'jquery',
    'underscore',
    'knockout',
    'arches',
    'views/base-manager',
    'views/components/foo'
], function($, _, ko, arches, BaseManagerView) {
    var View = BaseManagerView.extend({
        initialize: function(options){
            BaseManagerView.prototype.initialize.call(this, options);
        }
    });
    return new View();
});
