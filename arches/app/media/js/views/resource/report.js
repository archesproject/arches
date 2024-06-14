require([
    'jquery',
    'underscore',
    'knockout',
    'views/base-manager',
    'views/components/resource-report-abstract'
], function($, _, ko, BaseManagerView) {
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
    return new View();
});
