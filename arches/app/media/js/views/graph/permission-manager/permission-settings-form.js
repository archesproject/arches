define([
    'jquery',
    'underscore',
    'arches',
    'backbone',
    'knockout',
], function($, _, arches, Backbone,  ko) {
    var PermissionSettingsForm = Backbone.View.extend({
        /**
        * A backbone view representing a card component form
        * @augments Backbone.View
        * @constructor
        * @name PermissionSettingsForm
        */

        /**
        * Initializes the view with optional parameters
        * @memberof PermissionSettingsForm.prototype
        * @param {boolean} options.selection - the selected item, either a {@link CardModel} or a {@link NodeModel}
        */
        initialize: function(options) {
            this.selectedIdentities = options.selectedIdentities;
            this.identityList = options.identityList;
            this.selectedCards = options.selectedCards;
            this.noAccessPerm = undefined;
            this.whiteListPerms = [];
            this.groupedNodeList = options.groupedNodeList;

            options.nodegroupPermissions.forEach(function(perm){
                perm.selected = ko.observable(false);
                if(perm.codename === 'no_access_to_nodegroup'){
                    this.noAccessPerm = perm;
                    perm.selected.subscribe(function(selected){
                        if (selected){
                            this.whiteListPerms.forEach(function(perm){
                                perm.selected(false);
                            }, this);
                        }
                    }, this);
                }else{
                    this.whiteListPerms.push(perm)
                    perm.selected.subscribe(function(selected){
                        if (selected){
                            this.noAccessPerm.selected(false);
                        }
                    }, this);
                }
            }, this)
            this.nodegroupPermissions = ko.observableArray(options.nodegroupPermissions);
            this.identityList.items()[0].selected(true);
        },

        save: function(){
            var self = this;
            var postData = {
                'selectedIdentities': this.selectedIdentities(),
                'selectedCards': this.selectedCards(),
                'selectedPermissions': _.filter(this.nodegroupPermissions(), function(perm){
                    return perm.selected();
                })
            }

            $.ajax({
                type: 'POST',
                url: arches.urls.permission_data,
                data: JSON.stringify(postData),
                success: function(res){
                    self.trigger('save');
                }
            });
        },

        revert: function(){
            var self = this;
            var postData = {
                'selectedIdentities': this.selectedIdentities(),
                'selectedCards': this.selectedCards()
            }

            $.ajax({
                type: 'DELETE',
                url: arches.urls.permission_data,
                data: JSON.stringify(postData),
                success: function(res){
                    self.trigger('revert');
                }
            });
        }
    });
    return PermissionSettingsForm;
});
