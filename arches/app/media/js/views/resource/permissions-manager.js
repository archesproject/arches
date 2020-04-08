define([
    'jquery',
    'knockout',
    'knockout-mapping',
    'arches',
    'bindings/select2-query'
], function($, ko, koMapping, arches) {
    return ko.components.register('permissions-manager', {
        viewModel: function(params) {
            var self = this;
            this.instancePermissions = ko.observable();
            this.resourceId = params.resourceId();
            this.openEditor = ko.observable(undefined);
            this.identities = [{'text':'one', 'id': 1}, {'text':'two', 'id': 2}];
            this.selectedIdentities = ko.observableArray([]);
            this.updatePermissions = function(){
                var payload = {
                    "selectedIdentities": [
                        {"type": "group", "id": 2}
                    ],
                    "selectedInstances": [
                        {"resourceinstanceid": ko.unwrap(this.resourceId)}
                    ],
                    "selectedPermissions": [
                        {"codename": "change_resourceinstance"},
                        {"codename": "delete_resourceinstance"}
                    ]};
                $.ajax({
                    type: 'POST',
                    url: arches.urls.resource_permission_data,
                    data: JSON.stringify(payload),
                }).done(function(data){
                    // eslint-disable-next-line no-console
                    console.log(data);
                });
            };

            this.getInstancePermissions = function(){
                $.ajax({
                    url: arches.urls.resource_permission_data,
                    data: {"instanceid": ko.unwrap(self.resourceId)}
                }).done(function(data){
                    self.openEditor(data['limitedaccess']);
                    self.instancePermissions(data);
                });
            };

            this.makeInstancePrivate = function(){
                $.ajax({
                    type: 'POST',
                    url: arches.urls.restrict_resource_access,
                    data: {"instanceid": params.resourceId}
                }).done(function(data){
                    self.openEditor(data['limitedaccess']);
                    self.instancePermissions(data);
                });
            };

            this.getInstancePermissions();
        },
        template: { require: 'text!templates/views/resource/permissions/permissions-manager.htm' }
    });
});