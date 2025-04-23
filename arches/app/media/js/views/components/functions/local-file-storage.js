import $ from 'jquery';
import ko from 'knockout';
import koMapping from 'knockout-mapping';
import FunctionViewModel from 'viewmodels/function-view-model';
import chosen from 'bindings/chosen';
import localFileStorageTemplate from 'templates/views/components/functions/local-file-storage.htm'; 


export default ko.components.register('views/components/functions/local-file-storage', {
    viewModel: function(params) {
        FunctionViewModel.apply(this, arguments);

        window.setTimeout(function(){$("select[data-bind^=chosen]").trigger("chosen:updated");}, 300);
    },
    template: localFileStorageTemplate,
});
