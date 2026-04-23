import ko from 'knockout';
import WidgetViewModel from 'viewmodels/widget';
import selectTemplate from 'templates/views/components/widgets/select.htm';

const viewModel = function (params) {
    params.configKeys = ['defaultValue'];
    WidgetViewModel.apply(this, [params]);
    const self = this;

    self.multiple = false;
    self.defaultValue = ko.observable(params.config.defaultValue || null);
    self.options = ko.observableArray();
    self.placeholder = ko.observable(params.config.placeholder || 'Select an option');

    const datatype = self.node && self.node.datatype;
    if (datatype) {
        fetch(`/api/datatypes/${ko.unwrap(datatype)}/options`)
            .then((r) => r.json())
            .then((data) => self.options(data.options))
            .catch((err) => console.error('Error fetching widget options:', err));
    }
};

export default ko.components.register('external-domain', {
    viewModel,
    template: selectTemplate,
});
