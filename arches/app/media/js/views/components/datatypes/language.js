import ko from 'knockout';
import arches from 'arches';
import LanguageSelectViewModel from "viewmodels/language-select";
import languageDatatypeTemplate from 'templates/views/components/datatypes/language.htm';

const name = 'language-datatype-config';

const viewModel = function (params) {
    const self = this;
    self.search = params.search;

    LanguageSelectViewModel.apply(this, [params]);
    if (self.search) {
        let filter = params.filterValue();
        self.op = ko.observable(filter.op || 'eq');
        self.node = params.node;
        self.searchValue = ko.observable(filter.val || null);
        self.filterValue = ko.computed(function () {
            return {
                op: self.op(),
                val: self.searchValue()
            }
        }).extend({ throttle: 750 });
        params.filterValue(self.filterValue());
        self.filterValue.subscribe(function (val) {
            params.filterValue(val);
        });
    }
};

ko.components.register(name, {
    viewModel: viewModel,
    template: languageDatatypeTemplate
});

export default name;