define([
    'jquery',
    'underscore',
    'knockout',
    'knockout-mapping',
    'arches',
    'views/base-manager',
], function($, _, ko, koMapping, arches, BaseManagerView) {

    var UserProfileManager = BaseManagerView.extend({
        initialize: function(options){
            var self = this;
            self.viewModel.showChangePasswordForm = ko.observable(false);
            self.viewModel.showEditUserForm = ko.observable(false);
            self.viewModel.toggleChangePasswordForm = function(val){
                this.showChangePasswordForm(!this.showChangePasswordForm())
            };
            self.viewModel.toggleEditUserForm = function(val){
                this.showEditUserForm(!this.showEditUserForm())
            };

            self.viewModel.credentials = koMapping.fromJS({
                old_password: '',
                new_password: '',
                new_password2: ''
            });

            self.viewModel.changePassword = function(){
                var payload = koMapping.toJS(self.viewModel.credentials)
                $.ajax({
                    url: arches.urls.change_password,
                    method: "POST",
                    data: payload,
                }).done(function(data){
                    console.log(data);
                }).fail(function(err){
                    console.log(err);
                });
            }

            BaseManagerView.prototype.initialize.call(this, options)
        }
    });
    return new UserProfileManager();

});
