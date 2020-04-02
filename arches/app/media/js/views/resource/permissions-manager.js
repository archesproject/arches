define([
    'jquery',
    'knockout',
], function($, ko) {
    return ko.components.register('permissions-manager', {
        viewModel: function(params) {
            this.makeInstancePrivate = function(){
                $.ajax({
                    url: arches.urls.restrict_resource_access,
                    data: {"instanceid": params.resourceId}
                }).done(function(data){
                    console.log(data);
                });
            }
        },
        template: { require: 'text!templates/views/resource/permissions/permissions-manager.htm' }
    });
});