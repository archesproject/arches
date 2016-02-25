require([
    'jquery',
    'views/page-view',
    'views/form',
    'bootstrap-nifty'
], function($, PageView, Form) {
    var viewModel = {
        form: new Form({ 
            el: $('.arches-form')[0]
        })
    };

    new PageView({
        viewModel: viewModel
    });
});
