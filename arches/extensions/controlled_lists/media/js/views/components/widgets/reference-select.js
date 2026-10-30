import ko from 'knockout';
import ReferenceSelectViewModel from 'viewmodels/reference-select';
import referenceSelectTemplate from 'templates/views/components/widgets/reference-select.htm';
import 'bindings/select2-query';

export default ko.components.register('reference-select-widget', {
    viewModel: ReferenceSelectViewModel,
    template: referenceSelectTemplate,
});
