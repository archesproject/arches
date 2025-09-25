import ko from 'knockout';
import arches from 'arches';
import Cookies from 'js-cookie';
import referenceSelect from 'viewmodels/reference-select';
import referenceDatatypeTemplate from 'templates/views/components/datatypes/reference.htm';

const viewModel = function(params) {
    const self = this;
    this.search = params.search;

    if (this.search) {
        var filter = params.filterValue();
        params.config = ko.observable({
            controlledList:[],
            placeholder: arches.translations.selectAnOption,
            multiValue: true
        });
        this.op = ko.observable(filter.op || 'eq');
        this.searchValue = ko.observable(filter.val || '');
        this.node = params.node;
        params.value = this.searchValue;
        referenceSelect.apply(this, [params]);

        this.filterValue = ko.computed(function() {
            return {
                op: self.op(),
                val: reduceReferenceShape(self.searchValue())
            };
        });
        params.filterValue(this.filterValue());
        this.filterValue.subscribe(function(val) {
            params.filterValue(val);
        });
    }

    else {
        this.controlledList = params.config.controlledList;
        this.multiValue = params.config.multiValue;
        this.controlledLists = ko.observable();
        this.getControlledLists = async function() {
            const response = await fetch(arches.urls.controlled_lists, {
                method: 'GET',
                credentials: 'include',
                headers: {
                    "X-CSRFToken": Cookies.get('csrftoken')
                },
            });
            if (response.ok) {
                return await response.json();
            } else {
                console.error('Failed to fetch controlled lists');
            }
        };
        
        this.init = async function() {
            const lists = await this.getControlledLists();
            this.controlledLists(lists?.controlled_lists);
        };

        this.init();
    }

    // In an effort to reduce adv search URL length, only keep labels and uri
    // TODO: Keeping labels could also be used for fuzzy text matching in the future
    function reduceReferenceShape(items) {
        if (items?.length) {
            if (Array.isArray(items)) {
                const slimmedObj = items.map((item) => {
                    return {
                        "labels": item.labels,
                        "uri": item.uri,
                    }
                });
                return slimmedObj;
            } else {
                return [items];
            }
        }
        return '';
    };
};


export default ko.components.register('reference-datatype-config', {
    viewModel: viewModel,
    template: referenceDatatypeTemplate,
});