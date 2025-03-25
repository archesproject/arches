import $ from 'jquery';
import _ from 'underscore';
import ko from 'knockout';
import koMapping from 'knockout-mapping';
import arches from 'arches';
import BaseManagerView from 'views/base-manager';
import data from 'views/profile-manager-data';

class UserProfileManager extends BaseManagerView {
    constructor(options) {
        options = options || {};
        options.viewModel = options.viewModel || {};

        options.viewModel.showChangePasswordForm = ko.observable(false);
        options.viewModel.showEditUserForm = ko.observable(!!data.error_count);
        options.viewModel.validationErrors = ko.observableArray();
        options.viewModel.invalidPassword = ko.observable();
        options.viewModel.mismatchedPasswords = ko.observable();
        options.viewModel.changePasswordSuccess = ko.observable();
        options.viewModel.notifTypeObservables = ko.observableArray();

        options.viewModel.isTwoFactorAuthenticationEnabled =
            data.two_factor_authentication_settings['ENABLE_TWO_FACTOR_AUTHENTICATION'];
        options.viewModel.isTwoFactorAuthenticationForced =
            data.two_factor_authentication_settings['FORCE_TWO_FACTOR_AUTHENTICATION'];
        options.viewModel.hasUserEnabledTwoFactorAuthentication = ko.observable(
            data.two_factor_authentication_settings['user_has_enabled_two_factor_authentication']
        );

        options.viewModel.toggleChangePasswordForm = function () {
            this.showChangePasswordForm(!this.showChangePasswordForm());
            if (this.showChangePasswordForm()) {
                this.validationErrors([]);
                this.invalidPassword('');
                this.mismatchedPasswords('');
                this.changePasswordSuccess('');
            }
        };

        options.viewModel.toggleEditUserForm = function () {
            this.showEditUserForm(!this.showEditUserForm());
        };

        options.viewModel.getNotifTypes = function () {
            const vm = this;
            vm.notifTypeObservables.removeAll();
            $.ajax({
                url: arches.urls.get_notification_types,
                method: 'GET'
            }).done((data) => {
                data.types.forEach((type) => {
                    const koType = koMapping.fromJS(type);
                    vm.notifTypeObservables.push(koType);
                });
            });
        };

        options.viewModel.updateNotifTypes = function () {
            const vm = this;
            const updatedTypes = vm.notifTypeObservables().map(function (type) {
                const modified = koMapping.toJS(type);
                delete modified._state;
                return modified;
            });
            $.ajax({
                url: arches.urls.update_notification_types,
                method: 'POST',
                data: { types: JSON.stringify(updatedTypes) }
            });
        };

        options.viewModel.credentials = koMapping.fromJS({
            old_password: '',
            new_password: '',
            new_password2: ''
        });

        options.viewModel.changePassword = function () {
            const vm = this;
            const payload = koMapping.toJS(vm.credentials);
            $.ajax({
                url: arches.urls.change_password,
                method: 'POST',
                data: payload
            }).done(function (data) {
                vm.invalidPassword(data.invalid_password);
                vm.mismatchedPasswords(data.mismatched);
                vm.validationErrors(data.password_validations);
                if (data.success) {
                    vm.changePasswordSuccess(data.success);
                    vm.toggleChangePasswordForm();
                }
            });
        };

        options.viewModel.alertTwoFactorAuthenticationChange = function (userEmail) {
        };

        super(options);

        const vm = this.viewModel;
        vm.jsonNotifTypes = ko.computed(function () {
            return koMapping.toJS(vm.notifTypeObservables);
        }).extend({ throttle: 100 });
        vm.jsonNotifTypes.subscribe(function (val) {
            if (val && !vm.loading() && vm.notifTypeObservables().length > 0) {
                vm.updateNotifTypes();
            }
        });
    }
}

export default new UserProfileManager();
