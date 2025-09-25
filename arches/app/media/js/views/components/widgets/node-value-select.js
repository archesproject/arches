import ko from 'knockout';
import NodeValueSelectViewModel from 'viewmodels/node-value-select';
import nodeValueSelectTemplate from 'templates/views/components/widgets/node-value-select.htm';
import 'bindings/select2-query';


export default ko.components.register('node-value-select', {
    viewModel: NodeValueSelectViewModel,
    template: nodeValueSelectTemplate,
});
