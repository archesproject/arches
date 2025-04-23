import ko from 'knockout';
import ResourceInstanceSelectViewModel from 'viewmodels/resource-instance-select';
import resourceInstanceSelectWidgetTemplate from 'templates/views/components/widgets/resource-instance-select.htm';
import 'bindings/select2-query';


const viewModel =  function(params) {
    params.multiple = true;
    params.datatype = 'resource-instance-list';
    ResourceInstanceSelectViewModel.apply(this, [params]);
};

export default ko.components.register('resource-instance-multiselect-widget', {
    viewModel: viewModel,
    template: resourceInstanceSelectWidgetTemplate,
});
