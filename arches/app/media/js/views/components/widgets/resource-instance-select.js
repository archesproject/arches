import ko from 'knockout';
import resourceInstanceSelectWidgetTemplate from 'templates/views/components/widgets/resource-instance-select.htm';
import ResourceInstanceSelectViewModel from 'viewmodels/resource-instance-select';
import 'bindings/select2-query';


const viewModel = function(params) {
    params.multiple = false;
    params.datatype = 'resource-instance';
    ResourceInstanceSelectViewModel.apply(this, [params]);
};

export default ko.components.register('resource-instance-select-widget', {
    viewModel: viewModel,
    template: resourceInstanceSelectWidgetTemplate,
});
