define([
    'jquery',
    'knockout',
    'arches'
], function($, ko, arches) {
    return ko.components.register('permissions-manager', {
        viewModel: function(params) {
            this.makeInstancePrivate = function(){
                $.ajax({
                    type: 'POST',
                    url: arches.urls.restrict_resource_access,
                    data: {"instanceid": params.resourceId},
                    dataType: 'json'
                }).done(function(data){
                    console.log(data);
                });
            }
        },
        template: { require: 'text!templates/views/resource/permissions/permissions-manager.htm' }
    });
});