define([
    'jquery',
    'knockout',
    'knockout-mapping',
    'arches',
    'viewmodels/alert',
    'bindings/select2-query'
], function($, ko, koMapping, arches, AlertViewModel) {
    return ko.components.register('permissions-manager', {
        viewModel: function(params) {
            var self = this;
            this.instancePermissions = ko.observable();
            this.resourceId = params.resourceId();
            this.alert = params.alert;
            this.openEditor = ko.observable(undefined);
            this.identities = ko.observableArray();
            this.filter = ko.observable('');
            this.dirty = ko.observable(false);
            this.creatorid = params.creator;
            this.alertTitle = params.alertTitle;
            this.alertMessage = params.alertMessage;
            this.permissionLabelLookup = params.permissionLabelLookup;

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
                if (ko.unwrap(self.dirty)) {
                    var payload = {
                        "selectedIdentities": [],
                        "selectedInstances": [{"resourceinstanceid": ko.unwrap(this.resourceId)}],
                        "instanceid": ko.unwrap(self.resourceId)
                    };
                    self._currentPermissions.identities.forEach(function(identity){
                        var selectedPermissions = identity.default_permissions.map(function(perm){return {"codename": perm.codename};});
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
                }
            };

            this.revertPermissions = function(){
                var resetPermissions;
                if (ko.unwrap(self.dirty)) {
                    resetPermissions = JSON.parse(self._startPermissions);
                    resetPermissions.identities.forEach(function(identity){
                        if (Number(identity.id) === Number(self.creatorid) && identity.type == 'user') {
                            //pass
                        } else {
                            var defaultperms = identity.default_permissions.map(function(perm){return perm.codename;});
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
                }
            };

            this.removePermission = function(permissionlist, codename) {
                var permissionIndexLookup = function(p){return p.codename === codename;};
                var permissionIndex = permissionlist.findIndex(permissionIndexLookup);
                permissionlist.splice(permissionIndex, 1);
            };

            this.checkDirty = function(start, current) {
                var clean = start.identities.every(function(k, i){
                    var startPerms = k.default_permissions;
                    var currentPerms = current.identities[i].default_permissions;
                    var startPattern = JSON.stringify(startPerms.map(function(p){return p.id;}).sort());
                    var endPattern = JSON.stringify(currentPerms.map(function(p){return p.id;}).sort());
                    return startPattern === endPattern;
                });
                var dirty = !clean;
                return dirty;
            };

            this.updateState = function(includePermission, identityId, type, permission) {
                self._currentPermissions['identities'].forEach(function(id) {
                    if (id.type === type && id.id === identityId) {
                        if (includePermission) {
                            var currentIdentity = self.filteredPermissions().find(function(identity){return identity.type === type && identity.id === identityId;});
                            if (permission.codename === 'no_access_to_resourceinstance') {
                                id.default_permissions = [];
                                currentIdentity.availablePermissions.forEach(function(p){if (p.codename !== 'no_access_to_resourceinstance'){p.selected(false);}});
                            } else {
                                currentIdentity.availablePermissions.forEach(function(p){if (p.codename === 'no_access_to_resourceinstance'){p.selected(false);}});
                            }
                            id.default_permissions.push(permission);
                        } else {
                            self.removePermission(id.default_permissions, permission.codename);
                        }
                    }
                }, self);
                self.dirty(self.checkDirty(self._currentPermissions, JSON.parse(self._startPermissions)));
            };

            this.initPermissions = function(data) {
                self._startPermissions = JSON.stringify(data);
                self._currentPermissions = JSON.parse(self._startPermissions);
                self._permissionLookup = {};

                data.permissions.forEach(function(perm){ 
                    self._permissionLookup[perm.codename] = perm;
                });

                data['identities'].forEach(function(id){
                    id.selected = ko.observable(false);
                    id.creatorOrSuperUser = Number(self.creatorid) === Number(id.id) && id.type === 'user';

                    id.availablePermissions = JSON.parse(JSON.stringify(data['permissions'])).filter(function(permission) {
                        if (
                            permission.codename === "change_resourceinstance" 
                            || permission.codename === "delete_resourceinstance"
                        )  {
                            if (id.type === 'user') {
                                if (id.creatorOrSuperUser || id.is_editor_or_reviewer) { return true; }
                            } else {  // id.type === 'group'
                                if (id.name === 'Resource Editor' || id.name === 'Resource Reviewer') { return true; }
                            }

                            return false;
                        }

                        return true;
                    });
                  
                    var defaultPermissions = id.default_permissions.map(function(perm){return perm.codename;});
                    var iconLookup = {
                        "view_resourceinstance":"ion-ios-book",
                        "change_resourceinstance":"ion-edit",
                        "no_access_to_resourceinstance":"ion-close",
                        "delete_resourceinstance":"ion-android-delete",
                    };
                    id.availablePermissions.forEach(function(p){
                        p.icon = iconLookup[p.codename];
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
                    url: arches.urls.resource_permission_data,
                    data: {"instanceid": params.resourceId, "action": "restrict", "graphid": params.graphId}
                }).done(function(data){
                    self.openEditor(data['limitedaccess']);
                    var parsed = self.initPermissions(data);
                    self.instancePermissions(parsed);
                });
            };

            this.makeInstancePublic = function(){
                this.alert(new AlertViewModel('ep-alert-red', this.alertTitle, this.alertMessage, function() {
                    return;
                }, function(){
                    $.ajax({
                        type: 'POST',
                        url: arches.urls.resource_permission_data,
                        data: {"instanceid": params.resourceId, "action": "open", "graphid": params.graphId}
                    }).done(function(data){
                        var parsed = self.initPermissions(data);
                        self.instancePermissions(parsed);
                        self.openEditor(data['limitedaccess']);
                    });
                }));
            };

            this.getInstancePermissions();
        },
        template: { require: 'text!templates/views/resource/permissions/permissions-manager.htm' }
    });
});