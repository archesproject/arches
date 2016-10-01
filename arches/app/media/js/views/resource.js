require([
    'jquery',
    'underscore',
    'knockout',
    'arches',
    'views/base-manager',
    'bindings/chosen',
    'datatables',
], function($, _, ko, arches, BaseManagerView) {

    var recentlyAddedResourceTable = $('#demo-dt-selection').DataTable({
        "responsive": true,
        "language": {
            "paginate": {
              "previous": '<i class="fa fa-angle-left"></i>',
              "next": '<i class="fa fa-angle-right"></i>'
            }
        },
        // "columnDefs": [
        //     { targets: [0], visible: false}
        // ]
    });


    /**
    * a BaseManagerView representing the resource listing and recent edits pages
    */
    var ResourceView = BaseManagerView.extend({
        initialize: function(options){
            var self = this;
            this.viewModel.showResources = ko.observable(true);

            _.defaults(this.viewModel, {
                showFind: ko.observable(false),
                graphId: ko.observable(null),
            });

            this.viewModel.graphId.subscribe(function (graphid) {
                if(graphid && graphid !== ""){
                    self.viewModel.navigate(arches.urls.graph + graphid + '/add_resource');
                }
            });

            $('#demo-dt-selection tbody').on('dblclick', 'tr', function () {
                var data = recentlyAddedResourceTable.row( this ).data();
                self.viewModel.navigate(arches.urls.resource_editor + data[0]);
            });


            BaseManagerView.prototype.initialize.call(this, options)
        }
    });
    return new ResourceView();

});
