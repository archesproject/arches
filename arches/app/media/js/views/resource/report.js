import $ from 'jquery';
import _ from 'underscore';
import ko from 'knockout';
import BaseManagerView from 'views/base-manager';
import 'views/components/resource-report-abstract';


var View = BaseManagerView.extend({
    initialize: function(options){
        BaseManagerView.prototype.initialize.call(this, options);

        if (location.search.indexOf('print') > 0) {
            const self = this;
            self.viewModel.loading(true);
            setTimeout(
                function() {
                    self.viewModel.loading(false);
                    window.print();
                },
                7000 // a generous timeout here to allow maps/images to load
            );
        }
    }
});
export default new View();
