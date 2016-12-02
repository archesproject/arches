require([
    'jquery',
    'underscore',
    'knockout',
    'arches',
    'views/base-manager',
    'bindings/chosen',
    'bindings/datatable'
], function($, _, ko, arches, BaseManagerView) {
    /**
    * a BaseManagerView representing the resource listing and recent edits pages
    */
    var ResourceView = BaseManagerView.extend({
        initialize: function(options){
            var self = this;

            _.defaults(this.viewModel, {
                showResources: ko.observable(true),
                showFind: ko.observable(false),
                graphId: ko.observable(null),
                editResource: function(url, vm, e){
                    e.stopPropagation();
                    this.navigate(url)
                },
                tableConfig: {
                    "responsive": true,
                    "language": {
                        "paginate": {
                            "previous": '<i class="fa fa-angle-left"></i>',
                            "next": '<i class="fa fa-angle-right"></i>'
                        }
                    }
                },
                getErrorMsg: function(resourceModel) {
                  if (resourceModel.isactive && !resourceModel.hasforms && resourceModel.formsviewable) {
                    return arches.resourceModelErrorMsgs.formsNotAdded.concat(arches.resourceModelErrorMsgs.endErrorMsg);
                  }
                  else if (resourceModel.isactive && resourceModel.hasforms && !resourceModel.formsviewable) {
                    return arches.resourceModelErrorMsgs.formsNotViewable.concat(arches.resourceModelErrorMsgs.endErrorMsg);
                  }
                  else if (resourceModel.isactive && !resourceModel.hasforms && !resourceModel.formsviewable) {
                    return arches.resourceModelErrorMsgs.formsNotAdded.concat(' and', arches.resourceModelErrorMsgs.formsNotViewable.toLowerCase(), arches.resourceModelErrorMsgs.endErrorMsg);
                  }
                  else if (!resourceModel.isactive && resourceModel.hasforms && resourceModel.formsviewable) {
                    return arches.resourceModelErrorMsgs.resourceNotActive.concat(arches.resourceModelErrorMsgs.endErrorMsg);
                  }
                  else if (!resourceModel.isactive && !resourceModel.hasforms && resourceModel.formsviewable) {
                    return arches.resourceModelErrorMsgs.resourceNotActive.concat(' and', arches.resourceModelErrorMsgs.formsNotAdded.toLowerCase(), arches.resourceModelErrorMsgs.endErrorMsg);
                  }
                  else if (!resourceModel.isactive && resourceModel.hasforms && !resourceModel.formsviewable) {
                    return arches.resourceModelErrorMsgs.resourceNotActive.concat(arches.resourceModelErrorMsgs.formsNotViewable.toLowerCase(), arches.resourceModelErrorMsgs.endErrorMsg);
                  }
                  else if (!resourceModel.isactive && !resourceModel.hasforms && !resourceModel.formsviewable) {
                    return arches.resourceModelErrorMsgs.resourceNotActive.concat(',', arches.resourceModelErrorMsgs.formsNotAdded.toLowerCase(), ' and', arches.resourceModelErrorMsgs.formsNotViewable.toLowerCase(), arches.resourceModelErrorMsgs.endErrorMsg);
                  }
                  else {
                    return false;
                  }
                }
            });

            this.viewModel.graphId.subscribe(function (graphid) {
                if(graphid && graphid !== ""){
                    self.viewModel.navigate(arches.urls.graph + graphid + '/add_resource');
                }
            });

            BaseManagerView.prototype.initialize.call(this, options)
        }
    });
    return new ResourceView();
});
