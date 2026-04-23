import ko from 'knockout';
import externalDomainTemplate from 'templates/views/components/datatypes/external-domain.htm';

const name = 'external-domain-datatype-config';

export const ExternalDomainConfigViewModel = function (params) {
    const self = this;
    self.search = params.search;
    self.options = ko.observableArray();

    if (self.search) {
        self.node = params.node;
        const filter = params.filterValue();
        self.op = ko.observable(filter.op || 'eq');
        self.searchValue = ko.observable(filter.val || null);
        self.filterValue = ko.computed(() => ({
            op: self.op(),
            val: self.searchValue(),
        })).extend({ throttle: 750 });
        params.filterValue(self.filterValue());
        self.filterValue.subscribe((val) => params.filterValue(val));

        const datatype = ko.unwrap(params.node.datatype);
        fetch(`/api/datatypes/${datatype}/options`)
            .then((r) => r.json())
            .then((data) => self.options(data.options))
            .catch((err) => console.error('Error fetching datatype options:', err));
    }
};

ko.components.register(name, { viewModel: ExternalDomainConfigViewModel, template: externalDomainTemplate });
export default name;
