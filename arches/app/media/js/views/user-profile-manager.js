define([
    'jquery',
    'underscore',
    'knockout',
    'knockout-mapping',
    'arches',
    'viewmodels/alert',
    'viewmodels/mobile-survey',
    'models/mobile-survey',
    'views/base-manager',
    'views/mobile-survey-manager/identity-list',
    'profile-manager-data'
], function($, _, ko, koMapping, arches, AlertViewModel, MobileSurveyViewModel, MobileSurveyModel, BaseManagerView, IdentityList, data) {

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

            self.viewModel.isTwoFactorAuthenticationEnabled = data.two_factor_authentication_settings['ENABLE_TWO_FACTOR_AUTHENTICATION'];
            self.viewModel.isTwoFactorAuthenticationForced = data.two_factor_authentication_settings['FORCE_TWO_FACTOR_AUTHENTICATION'];
            self.viewModel.hasUserEnabledTwoFactorAuthentication = ko.observable(data.two_factor_authentication_settings['user_has_enabled_two_factor_authentication']);

            console.log(data.two_factor_authentication_settings)

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

            this.identityList = new IdentityList({
                items: ko.observableArray(data.identities)
            });

            this.viewModel.mobilesurveys = data.mobilesurveys.map(function(mobilesurvey) {
                return new MobileSurveyViewModel({
                    resources: data.resources,
                    mobilesurvey: mobilesurvey,
                    identities: data.identities,
                    context: 'userprofile'
                });
            });

            this.viewModel.mobileSurveyFilter = ko.observable('');

            this.viewModel.filteredMobileSurveys = ko.computed(function() {
                var filter = self.viewModel.mobileSurveyFilter();
                var list = self.viewModel.mobilesurveys;
                if (filter.length === 0) {
                    return list;
                }
                return _.filter(list, function(mobilesurvey) {
                    return mobilesurvey.mobilesurvey.name().toLowerCase().indexOf(filter.toLowerCase()) >= 0;
                });
            });

            _.each(self.viewModel.mobilesurveys, function(mobilesurvey) {
                mobilesurvey.resources = ko.computed(function() {
                    var resources = [];
                    var resourceLookup = {};
                    _.each(mobilesurvey.allResources, function(resource) {
                        _.each(resource.cards(), function(card) {
                            if (_.contains(mobilesurvey.mobilesurvey.cards(), card.cardid)) {
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

            self.viewModel.alertTwoFactorAuthenticationChange = function() {
                var sendTwoFactorAuthenticationEmail = function() {
                    $.ajax({
                        url: arches.urls.two_factor_authentication_reset,
                        method: "POST",
                        
                    }).done(function(data) {
                        console.log(data)
                        self.viewModel.alert(
                            new AlertViewModel(
                                'ep-alert-blue',
                                arches.twoFactorAuthenticationEmailSuccess.title,
                                arches.twoFactorAuthenticationEmailSuccess.text,
                            )
                        )
                    });
                };

                self.viewModel.alert(
                    new AlertViewModel(
                        'ep-alert-blue',
                        arches.confirmSendTwoFactorAuthenticationEmail.title,
                        arches.confirmSendTwoFactorAuthenticationEmail.text,
                        function(){},
                        sendTwoFactorAuthenticationEmail,
                    )
                )
            };

            BaseManagerView.prototype.initialize.call(this, options);
        }
    });
    return new UserProfileManager();

});
