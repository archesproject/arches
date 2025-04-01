import $ from 'jquery';
import _ from 'underscore';
import ko from 'knockout';
import arches from 'arches';
import BaseManagerView from 'views/base-manager';
import 'bindings/chosen';


/**
* a BaseManagerView representing the resource listing and recent edits pages
*/
var ResourceView = BaseManagerView.extend({
    initialize: function(options){
        var self = this;

        _.defaults(this.viewModel, {
            showFind: ko.observable(false),
            graphId: ko.observable(null),
            arches: arches,
        });

        this.viewModel.graphId.subscribe(function(graphid) {
            if(graphid && graphid !== ""){
                self.viewModel.navigate(arches.urls.add_resource(graphid));
            }
        });

        BaseManagerView.prototype.initialize.call(this, options);
    }
});
export default new ResourceView();
