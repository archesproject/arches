define([
    'jquery',
    'underscore',
    'knockout',
    'knockout-mapping',
    'arches',
    'viewmodels/mobile-survey-manager',
    'views/base-manager',
    'profile-manager-data'
], function($, _, ko, koMapping, arches, MobileSurveyManagerViewModel, BaseManagerView, data) {

    var UserProfileManager = BaseManagerView.extend({
        initialize: function(options) {
            var self = this;
            self.viewModel.showChangePasswordForm = ko.observable(false);
            self.viewModel.showEditUserForm = ko.observable(!!data.error_count);

            self.viewModel.validationErrors = ko.observableArray();
            self.viewModel.invalidPassword = ko.observable();
            self.viewModel.mismatchedPasswords = ko.observable();
            self.viewModel.changePasswordSuccess = ko.observable();

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
            self.viewModel.mobileSurveyManager = new MobileSurveyManagerViewModel(data);

            _.each(self.viewModel.mobileSurveyManager.mobilesurveys(), function(mobilesurvey) {
                mobilesurvey.resources = ko.computed(function() {
                    var resources = [];
                    var resourceLookup = {};
                    _.each(self.viewModel.mobileSurveyManager.resourceList.items(), function(resource) {
                        _.each(resource.cards(), function(card) {
                            if (_.contains(mobilesurvey.cards(), card.cardid)) {
                                if (resourceLookup[resource.id]) {
                                    resourceLookup[resource.id].cards.push(card);
                                } else {
                                    resourceLookup[resource.id] = {
                                        name: resource.name,
                                        cards: [card]
                                    };
                                }
                            }
                        });
                    });
                    _.each(resourceLookup, function(resource) {
                        resources.push(resource);
                    });
                    resources.sort(function(a, b) {
                        return a.name - b.name;
                    });
                    return resources;
                });
            }, self);

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
