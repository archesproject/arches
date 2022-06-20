define([
    'jquery',
    'underscore',
    'knockout',
    'knockout-mapping',
    'arches',
    'views/base-manager',
    'profile-manager-data'
], function($, _, ko, koMapping, arches, BaseManagerView, data) {

    var UserProfileManager = BaseManagerView.extend({
        initialize: function(options) {
            var self = this;
            self.viewModel.showChangePasswordForm = ko.observable(false);
            self.viewModel.showEditUserForm = ko.observable(!!data.error_count);

            self.viewModel.validationErrors = ko.observableArray();
            self.viewModel.invalidPassword = ko.observable();
            self.viewModel.mismatchedPasswords = ko.observable();
            self.viewModel.changePasswordSuccess = ko.observable();
            self.viewModel.notifTypeObservables = ko.observableArray();

            self.viewModel.toggleChangePasswordForm = function() {
                this.showChangePasswordForm(!this.showChangePasswordForm());
                if (this.showChangePasswordForm()) {
                    self.viewModel.validationErrors([]);
                    self.viewModel.invalidPassword('');
                    self.viewModel.mismatchedPasswords('');
                    self.viewModel.changePasswordSuccess('');
                }
            };
            self.viewModel.toggleEditUserForm = function() {
                this.showEditUserForm(!this.showEditUserForm());
            };

            self.viewModel.getNotifTypes = function() {
                self.viewModel.notifTypeObservables.removeAll();
                $.ajax({
                    url: arches.urls.get_notification_types,
                    method: "GET"
                }).done(function(data) {
                    var koType;
                    data.types.forEach(function(type) {
                        koType = ko.mapping.fromJS(type);
                        self.viewModel.notifTypeObservables.push(koType);
                    });
                });
            };
            self.viewModel.getNotifTypes();

            self.viewModel.updateNotifTypes = function() {
                var modified;
                var updatedTypes = self.viewModel.notifTypeObservables().map(function(type) {
                    modified = ko.mapping.toJS(type);
                    delete modified._state;
                    return modified;
                });
                $.ajax({
                    url: arches.urls.update_notification_types,
                    method: "POST",
                    data: {"types": JSON.stringify(updatedTypes)}
                });
            };

            self.jsonNotifTypes = ko.computed(function() {
                return ko.mapping.toJS(self.viewModel.notifTypeObservables);
            });
            self.jsonNotifTypes.subscribe(function(val) {
                if(val && !self.viewModel.loading() && self.viewModel.notifTypeObservables().length > 0) {
                    self.viewModel.updateNotifTypes();
                }
            });

            self.viewModel.credentials = koMapping.fromJS({
                old_password: '',
                new_password: '',
                new_password2: ''
            });

            self.viewModel.changePassword = function() {
                var payload = koMapping.toJS(self.viewModel.credentials);
                $.ajax({
                    url: arches.urls.change_password,
                    method: "POST",
                    data: payload,
                }).done(function(data) {
                    self.viewModel.invalidPassword(data.invalid_password);
                    self.viewModel.mismatchedPasswords(data.mismatched);
                    self.viewModel.validationErrors(data.password_validations);
                    if (data.success) {
                        self.viewModel.changePasswordSuccess(data.success);
                        self.viewModel.toggleChangePasswordForm();
                    }
                });
            };

            BaseManagerView.prototype.initialize.call(this, options);
        }
    });
    return new UserProfileManager();

});
