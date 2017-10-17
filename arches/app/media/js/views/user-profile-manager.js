define([
    'jquery',
    'underscore',
    'knockout',
    'views/base-manager',
], function($, _, ko, BaseManagerView) {

    var UserProfileManager = BaseManagerView.extend({
        initialize: function(options){
            var self = this;
            self.viewModel.showChangePasswordForm = ko.observable(false);
            self.viewModel.toggleChangePasswordForm = function(val){
                this.showChangePasswordForm(!this.showChangePasswordForm())
            }
            BaseManagerView.prototype.initialize.call(this, options)
        }
    });
    return new UserProfileManager();

});
