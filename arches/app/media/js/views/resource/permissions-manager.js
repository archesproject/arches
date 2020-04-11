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
            this.identities = ko.observableArray();
            this.filter = ko.observable('');
            this.dirty = ko.observable(false);

            this.getInstancePermissions = function(){
                $.ajax({
                    url: arches.urls.resource_permission_data,
                    data: {"instanceid": ko.unwrap(self.resourceId)}
                }).done(function(data){
                    self.openEditor(data['limitedaccess']);
                    var parsed = self.initPermissions(data);
                    self.instancePermissions(parsed);
                });
            };

            this.updatePermissions = function(){
                var payload = {
                    "selectedIdentities": [],
                    "selectedInstances": [{"resourceinstanceid": ko.unwrap(this.resourceId)}],
                    "instanceid": ko.unwrap(self.resourceId)
                }
                self._currentPermissions.identities.forEach(function(identity){
                    var selectedPermissions = identity.default_permissions.map(function(perm){return {"codename": perm.codename} });
                    payload.selectedIdentities.push({"type": identity.type, "id": identity.id, "selectedPermissions": selectedPermissions});
                });
                $.ajax({
                    type: 'POST',
                    url: arches.urls.resource_permission_data,
                    data: JSON.stringify(payload),
                }).done(function(data){
                    self._startPermissions = JSON.stringify(data);
                    self._currentPermissions = JSON.parse(self._startPermissions);
                    self.dirty(koMapping.toJSON(self._currentPermissions) !== self._startPermissions);
                });
            };

            this.revertPermissions = function(){
                var resetPermissions = JSON.parse(self._startPermissions);
                resetPermissions.identities.forEach(function(identity){
                    if (Number(identity.id) === Number(self.creator) && identity.type == 'user') {
                        console.log('skipping', identity)
                    } else {
                        var defaultperms = identity.default_permissions.map(function(perm){return perm.codename});
                        self.instancePermissions()['identities'].forEach(function(activeidentity){
                            if (activeidentity.id === identity.id && activeidentity.type === identity.type) {
                                activeidentity.availablePermissions.forEach(function(availablePermission){
                                    var status = defaultperms.indexOf(availablePermission.codename) > -1;
                                    if (availablePermission.selected() !== status) {
                                        availablePermission.selected(status); 
                                    }
                                });
                            }
                        });
                    }
                });
            };

            this.updateState = function(includePermission, identityId, type, permission) {
                self._currentPermissions['identities'].forEach(function(id) {
                    if (id.type === type && id.id === identityId) {
                        if (includePermission) {
                            id.default_permissions.push(permission);
                        } else {
                            var permissionIndexLookup = (p) => p.codename === permission.codename;
                            var permissionIndex = id.default_permissions.findIndex(permissionIndexLookup);
                            id.default_permissions.splice(permissionIndex, 1);
                        }
                    }
                }, self);
                var dirty = koMapping.toJSON(self._currentPermissions) !== self._startPermissions;
                self.dirty(dirty);
            };

            this.initPermissions = function(data) {
                self._startPermissions = JSON.stringify(data);
                self._currentPermissions = JSON.parse(self._startPermissions);
                self._permissionLookup = {};
                self.creator = data['creatorid']
                data.permissions.forEach(perm => self._permissionLookup[perm.codename] = perm);
                data['identities'].forEach(function(id){
                    id.selected = ko.observable(false);
                    id.creator = Number(self.creator) === Number(id.id) && id.type == 'user';
                    id.availablePermissions = JSON.parse(JSON.stringify(data['permissions']));
                    var defaultPermissions = id.default_permissions.map(function(perm){return perm.codename;});
                    id.availablePermissions.forEach(function(p){
                        var hasPerm = defaultPermissions.indexOf(p.codename) > -1;
                        p.selected = ko.observable(hasPerm);
                        p.selected.subscribe(function(val){
                            self.updateState(val, id.id, id.type, self._permissionLookup[p.codename]);
                        });
                    });
                });
                return data;
            };

            this.filteredPermissions = ko.pureComputed(function(){
                var res = [];
                if (ko.unwrap(self.instancePermissions)) {
                    res = self.instancePermissions()['identities'].filter(function(p){
                        var filtered = p.name.toLowerCase().includes(self.filter().toLowerCase());
                        return filtered;
                    }, this);
                } 
                return res;
            }, this).extend({deferred:true});    

            this.makeInstancePrivate = function(){
                $.ajax({
                    type: 'POST',
                    url: arches.urls.restrict_resource_access,
                    data: {"instanceid": params.resourceId}
                }).done(function(data){
                    self.openEditor(data['limitedaccess']);
                    var parsed = self.initPermissions(data);
                    self.instancePermissions(parsed);
                });
            };

            this.getInstancePermissions();
        },
        template: { require: 'text!templates/views/resource/permissions/permissions-manager.htm' }
    });
});