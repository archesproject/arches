define([
    'jquery',
    'underscore',
    'knockout',
    'views/base-manager',
], function($, _, ko, BaseManagerView) {

    var UserProfileManager = BaseManagerView.extend({
        initialize: function(options){
            var self = this;
            BaseManagerView.prototype.initialize.call(this, options)
        }
    });
    return new UserProfileManager();

});
