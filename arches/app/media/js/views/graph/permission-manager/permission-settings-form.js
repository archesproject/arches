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
            this.graphid = options.graphid;
            this.selectedUsersAndGroups = options.selectedUsersAndGroups;
            this.selectedCards = options.selectedCards;

            options.nodegroupPermissions.forEach(function(perm){
                perm.selected = ko.observable(false);
            })
            this.nodegroupPermissions = ko.observableArray(options.nodegroupPermissions);
        },

        save: function(){
            var postData = {
                'selectedUsersAndGroups': this.selectedUsersAndGroups(),
                'selectedCards': this.selectedCards(),
                'selectedPermissions': _.filter(this.nodegroupPermissions(), function(perm){
                    return perm.selected();
                })
            }

            $.ajax({
                type: 'POST',
                url: arches.urls.permission_manager.replace('//', '/' + this.graphid + '/'),
                data: JSON.stringify(postData),
                success: function(res){
                    //self.options(res.results);
                },
                complete: function () {
                    //self.loading(false);
                }
            });
        }
    });
    return PermissionSettingsForm;
});
