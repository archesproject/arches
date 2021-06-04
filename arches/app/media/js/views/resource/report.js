require([
    'jquery',
    'underscore',
    'knockout',
    'arches',
    'views/base-manager',
    'views/components/foo'
], function($, _, ko, arches, BaseManagerView) {
    var ddd = BaseManagerView.extend({
        initialize: function(options){
            BaseManagerView.prototype.initialize.call(this, options);
        }
    });
    return new ddd()
});
