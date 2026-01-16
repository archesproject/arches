import ko from 'knockout';
import arches from 'arches';
import languageDatatypeTemplate from 'templates/views/components/datatypes/language.htm';

const name = 'language-datatype-config';

const viewModel = function (params) {
    const self = this;
    this.search = params.search;
    if (this.search) {
        var filter = params.filterValue();
        this.op = ko.observable(filter.op || '~');
        this.node = params.node;
        this.languages = ko.observableArray(arches.languages);
        this.searchValue = ko.observable(filter.val || arches.activeLanguage);
        this.filterValue = ko.computed(function () {
            return {
                op: self.op(),
                val: self.searchValue()
            }
        }).extend({ throttle: 750 });
        params.filterValue(this.filterValue());
        this.filterValue.subscribe(function (val) {
            params.filterValue(val);
        });
    }
};

ko.components.register(name, {
    viewModel: viewModel,
    template: languageDatatypeTemplate
});

export default name;